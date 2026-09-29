"""END+END input control; prepare, infer and review only inside the recorded Docker image."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median
from types import SimpleNamespace

STUDY = Path('/study')
PREP = Path('/prepared')
OLD = Path('/previous')
OUT = Path('/output')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def baseline():
    saved = read(STUDY/'outcome.json')['vlm_comparison']
    for name in ('vlm.py', 'vlm_config.json', 'review_vlm.py', 'requirements.vlm.lock'):
        assert sha(STUDY/name) == saved['source_files'][name], name
    for name in ('inputs.json', 'predictions.jsonl', 'runtime.json', 'review.json', 'completion.json'):
        assert sha(OLD/name) == saved['artifacts']['runs/q7/vlm/'+name], name
    assert sha(PREP/'cases.json') == saved['runtime']['cases_sha256']
    assert sha('/model/download.json') == saved['runtime']['download_receipt_sha256']
    assert sha('/opt/requirements.resolved.txt') == sha(STUDY/'requirements.vlm.lock')
    return saved


def prepare():
    import torch
    from PIL import Image
    from transformers import AutoProcessor
    from vlm import prompt_payload

    baseline()
    assert not (OUT/'plan.json').exists()
    cfg = read(STUDY/'vlm_config.json')
    processor = AutoProcessor.from_pretrained('/model', local_files_only=True, trust_remote_code=False)
    processor.image_processor.size = {'longest_edge': cfg['image_longest_edge']}
    processor.image_processor.do_image_splitting = cfg['do_image_splitting']
    torch.set_num_threads(4)
    old_inputs = {(x['case'], x['condition']): x for x in read(OLD/'inputs.json')}
    original_hashes = {x['path']: x['sha256'] for x in read(PREP/'input.json')['files']}
    for name, digest in original_hashes.items():
        assert sha(PREP/'originals'/name) == digest, name
    cases, plan = [], []
    for case in read(PREP/'cases.json'):
        public = {key: case[key] for key in ('task', 'subtask', 'start', 'end')}
        control = dict(public, start=public['end'])
        prompt, paths, descriptors = prompt_payload(control, 'start_end', cfg, processor)
        old = old_inputs[(case['id'], 'start_end')]
        assert prompt == old['prompt']
        assert paths == case['end'] * 2
        for d in descriptors:
            d['sha256'] = original_hashes[d['relative_path']]

        def encode(image_paths):
            images = []
            for path in image_paths:
                with Image.open(PREP/'originals'/path) as im:
                    images.append(im.convert('RGB'))
            return processor(text=prompt, images=images, return_tensors='pt')

        now = encode(paths)
        before = encode([d['relative_path'] for d in old['images']])
        assert set(now) == set(before)
        assert torch.equal(now['input_ids'], before['input_ids'])
        assert now['pixel_values'].shape == (1, 6, 3, 384, 384)
        assert torch.equal(now['pixel_values'][:, :3], now['pixel_values'][:, 3:])
        assert torch.equal(now['pixel_values'][:, 3:], before['pixel_values'][:, 3:])
        image_tokens = int((now['input_ids'] == processor.tokenizer.convert_tokens_to_ids(processor.image_token)).sum())
        assert image_tokens == 486
        hash_equal = [d['sha256'] for d in descriptors] == [d['sha256'] for d in old['images']]
        tensors_equal = all(torch.equal(now[k], before[k]) for k in now)
        assert hash_equal == tensors_equal
        if not tensors_equal:
            assert case['role'] in ('source_failure', 'source_success')
            cases.append(dict(id=case['id'], **control))
        plan.append({'case': case['id'], 'condition': 'end_end', 'prompt': prompt,
                     'images': descriptors, 'reuse': tensors_equal,
                     'input_tokens': int(now['input_ids'].shape[-1]), 'image_tokens': image_tokens,
                     'prompt_matches_start_end': True, 'input_ids_match_start_end': True,
                     'end_pixels_preserved': True, 'halves_equal': True,
                     'all_tensors_equal_to_start_end': tensors_equal})
    assert len(plan) == 15 and len(cases) == 8 and sum(x['reuse'] for x in plan) == 7
    # Only batch scope changes; model input still uses the original START/END phase labels.
    control_cfg = dict(cfg, conditions=['start_end'], expected_cases=8, expected_predictions=8)
    write(OUT/'config.json', control_cfg)
    write(OUT/'cases.json', cases)
    write(OUT/'plan.json', {'status': 'PASS', 'conditions_semantics': 'START slots contain END images',
                          'new_predictions': 8, 'reused_predictions': 7, 'cases': plan,
                          'source_sha256': sha(__file__), 'config_sha256': sha(OUT/'config.json'),
                          'cases_sha256': sha(OUT/'cases.json'),
                          'baseline_predictions_sha256': sha(OLD/'predictions.jsonl'),
                          'baseline_inputs_sha256': sha(OLD/'inputs.json')})
    print('PASS 15 inputs; 7 exact prompt/hash/tensor reuses; 8 new predictions required', flush=True)


def infer():
    from vlm import main
    baseline()
    plan = read(OUT/'plan.json')
    assert plan['status'] == 'PASS' and plan['source_sha256'] == sha(__file__)
    assert plan['config_sha256'] == sha(OUT/'config.json')
    assert plan['cases_sha256'] == sha(OUT/'cases.json')
    main(SimpleNamespace(output=str(OUT/'predictions'), config=str(OUT/'config.json'),
                         cases=str(OUT/'cases.json'), images=str(PREP/'originals'),
                         model='/model', device='cuda'))


def review():
    # Independent schema parser from the prior review, not the generation parser.
    from review_vlm import parse
    saved = baseline()
    plan = read(OUT/'plan.json')
    assert plan['source_sha256'] == sha(__file__)
    cfg = read(OUT/'config.json')
    original_cfg = read(STUDY/'vlm_config.json')
    for key in original_cfg:
        if key not in ('conditions', 'expected_cases', 'expected_predictions'):
            assert cfg[key] == original_cfg[key], key
    assert cfg['conditions'] == ['start_end'] and cfg['expected_cases'] == cfg['expected_predictions'] == 8
    run = OUT/'predictions'
    completion = read(run/'completion.json')
    assert completion['status'] == 'completed' and completion['predictions'] == 8
    assert completion['predictions_sha256'] == sha(run/'predictions.jsonl')
    assert completion['inputs_sha256'] == sha(run/'inputs.json')
    runtime, old_runtime = read(run/'runtime.json'), read(OLD/'runtime.json')
    for key in ('python', 'torch', 'cuda_runtime', 'transformers', 'numpy', 'pillow', 'device', 'dtype',
                'gpu', 'source_sha256', 'download_receipt_sha256', 'seed', 'processor', 'model_class',
                'parameters', 'attention_implementation'):
        assert runtime[key] == old_runtime[key], key
    assert runtime['config_sha256'] == plan['config_sha256'] == sha(OUT/'config.json')
    assert runtime['cases_sha256'] == plan['cases_sha256'] == sha(OUT/'cases.json')
    assert sha(run/'requirements.resolved.txt') == sha(STUDY/'requirements.vlm.lock')
    new_rows = rows(run/'predictions.jsonl')
    new = {r['case']: r for r in new_rows}
    new_inputs = {r['case']: r for r in read(run/'inputs.json')}
    old = {(r['case'], r['condition']): r for r in rows(OLD/'predictions.jsonl')}
    old_inputs = {(r['case'], r['condition']): r for r in read(OLD/'inputs.json')}
    expected_new = {p['case'] for p in plan['cases'] if not p['reuse']}
    assert len(new_rows) == len(new) == len(new_inputs) == 8
    assert set(new) == set(new_inputs) == expected_new
    source_cases = {c['id']: c for c in read(PREP/'cases.json')}
    pattern_text = read(OLD/'review.json')['post_hoc_raw_verdict']['regex']
    assert pattern_text == r'The verdict is (GOAL_MET|GOAL_NOT_MET|UNCERTAIN)(?:\.| because ([^\n]+))'
    pattern = re.compile(pattern_text)
    combined = []
    for p in plan['cases']:
        name = p['case']; c = source_cases[name]
        row = old[(name, 'start_end')] if p['reuse'] else new[name]
        inp = old_inputs[(name, 'start_end')] if p['reuse'] else new_inputs[name]
        assert row['condition'] == 'start_end' and inp['prompt'] == p['prompt']
        assert [(d['phase'], d['view_index'], d['sha256']) for d in inp['images']] == [
            (d['phase'], d['view_index'], d['sha256']) for d in p['images']]
        assert [d['relative_path'] for d in p['images']] == c['end'] * 2
        for d in inp['images']:
            assert d['sha256'] == sha(PREP/'originals'/d['relative_path'])
        assert row['prompt_sha256'] == hashlib.sha256(inp['prompt'].encode()).hexdigest()
        assert row['input_tokens'] == p['input_tokens'] == old[(name,'start_end')]['input_tokens']
        assert row['image_count'] == 6 and row['image_tokens'] == p['image_tokens'] == 486
        assert row['tensor_shapes']['pixel_values'] == [1,6,3,384,384]
        target = 'GOAL_NOT_MET' if c['role'] == 'constructed' or c['source_label'] == 0 else 'GOAL_MET'
        entry = {'case': name, 'reference': target, 'role': c['role'],
                 'end_end_origin': 'reused_start_end' if p['reuse'] else 'new_generation'}
        for condition, r in [('end_only', old[(name,'end_only')]), ('start_end', old[(name,'start_end')]), ('end_end', row)]:
            parsed = parse(r['raw_response'])
            assert parsed == r['parsed']
            match = pattern.fullmatch(r['raw_response'].strip())
            verdict = match.group(1) if match else 'UNEXTRACTABLE'
            entry[condition] = {'json_verdict': parsed['verdict'] if parsed else 'INVALID',
                                'raw_verdict': verdict, 'agrees': verdict == target,
                                'raw_response': r['raw_response'], 'terminated_with_eos': r['terminated_with_eos']}
        combined.append(entry)
    assert len(combined) == 15
    counts = {}
    for subset in ('all', 'new_8', 'reused_7', 'source', 'constructed'):
        selected = [r for r in combined if subset == 'all' or
                    (subset == 'new_8' and r['end_end_origin'] == 'new_generation') or
                    (subset == 'reused_7' and r['end_end_origin'] == 'reused_start_end') or
                    (subset == 'source' and r['role'] != 'constructed') or
                    (subset == 'constructed' and r['role'] == 'constructed')]
        counts[subset] = {}
        for condition in ('end_only', 'start_end', 'end_end'):
            counter = Counter(total=len(selected))
            for r in selected:
                value = r[condition]; verdict = value['raw_verdict']
                counter['json_valid'] += int(value['json_verdict'] != 'INVALID')
                counter['json_reference_agreement'] += int(value['json_verdict'] == r['reference'])
                counter['raw_reference_agreement'] += int(value['agrees'])
                counter['uncertain'] += int(verdict == 'UNCERTAIN')
                counter['unextractable'] += int(verdict == 'UNEXTRACTABLE')
                counter['false_positive'] += int(verdict == 'GOAL_MET' and r['reference'] == 'GOAL_NOT_MET')
                counter['false_negative'] += int(verdict == 'GOAL_NOT_MET' and r['reference'] == 'GOAL_MET')
                counter['truncated'] += int(not value['terminated_with_eos'])
                counter[verdict] += 1
            counts[subset][condition] = counter
    for condition in ('end_only','start_end'):
        assert counts['all'][condition]['raw_reference_agreement'] == saved['post_hoc_raw_verdict']['counts'][condition]['reference_agreement']
    contrasts = {}
    for before, after in [('end_only','start_end'), ('end_only','end_end'), ('end_end','start_end')]:
        changed = [r['case'] for r in combined if r[before]['raw_verdict'] != r[after]['raw_verdict']]
        contrasts[before+'_to_'+after] = {
            'changed_cases': changed,
            'gained_reference_agreement': [r['case'] for r in combined if not r[before]['agrees'] and r[after]['agrees']],
            'lost_reference_agreement': [r['case'] for r in combined if r[before]['agrees'] and not r[after]['agrees']]}
    result = {'verification': 'PASS', 'new_generations': 8, 'reused': 7, 'counts': counts,
              'contrasts': contrasts, 'cases': combined, 'raw_verdict_regex': pattern_text,
              'parser_status': 'chosen after original 30 outputs; fixed before these eight outputs',
              'new_run_cost': {'median_seconds': median(r['elapsed_seconds'] for r in new_rows),
                               'generated_tokens': sum(r['generated_tokens'] for r in new_rows),
                               'max_peak_allocated_bytes': max(r['peak_allocated_bytes'] for r in new_rows)},
              'source_sha256': sha(__file__), 'plan_sha256': sha(OUT/'plan.json'),
              'new_predictions_sha256': sha(run/'predictions.jsonl'),
              'baseline_predictions_sha256': sha(OLD/'predictions.jsonl'),
              'limitations': ['Dependent known dev cases; unchanged unverified source labels.',
                             'Seven identity-based reuses are not new generations or repeatability evidence.',
                             'Single greedy runs on different days; execution variability is not estimated.',
                             'Image content influence does not prove correct temporal reasoning or natural-failure transfer.']}
    write(OUT/'review.json', result)
    print(json.dumps({k:result[k] for k in ('verification','new_generations','reused','contrasts','new_run_cost')},ensure_ascii=False))
    print(json.dumps(counts['all'],ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare','infer','review'])
    mode = parser.parse_args().mode
    {'prepare':prepare, 'infer':infer, 'review':review}[mode]()
