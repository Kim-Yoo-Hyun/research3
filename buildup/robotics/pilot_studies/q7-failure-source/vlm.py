"""Frozen general-VLM comparison. All model/image execution is Docker-only."""
import argparse
import hashlib
import json
import os
import platform
import random
import time
from pathlib import Path

import numpy as np
import PIL
import torch
import transformers
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def prompt_payload(public_case, condition, config, processor):
    # Whitelist only task text, subtask text and image paths. Paths themselves are never prompt text.
    assert set(public_case) == {'task', 'subtask', 'start', 'end'}
    content = [{'type': 'text', 'text': config['prompt_prefix'].format(
        task=public_case['task'], subtask=public_case['subtask'])}]
    paths = []
    descriptors = []
    phases = ['end'] if condition == 'end_only' else ['start', 'end']
    for phase in phases:
        for view, path in enumerate(public_case[phase]):
            content.extend([{'type': 'text', 'text': f'{phase.upper()} camera {view}:'}, {'type': 'image'}])
            paths.append(path)
            descriptors.append({'phase': phase, 'view_index': view, 'relative_path': path})
    content.append({'type': 'text', 'text': config['prompt_question']})
    messages = [{'role': 'user', 'content': content}]
    text = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    return text, paths, descriptors


def parse_response(text):
    value = text.strip()
    if value.startswith('```') and value.endswith('```'):
        lines = value.splitlines()
        value = '\n'.join(lines[1:-1]).strip()
    try:
        obj = json.loads(value)
    except (ValueError, TypeError):
        return None, 'invalid_json'
    if not isinstance(obj, dict) or set(obj) != {'verdict', 'evidence'}:
        return None, 'invalid_schema'
    if obj['verdict'] not in ['GOAL_MET', 'GOAL_NOT_MET', 'UNCERTAIN'] or not isinstance(obj['evidence'], str):
        return None, 'invalid_value'
    return obj, None


def main(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(Path(args.config).read_text())
    cases = json.loads(Path(args.cases).read_text())
    assert len(cases) == cfg['expected_cases']
    assert len({case['id'] for case in cases}) == len(cases)
    cache = Path(args.model)
    download = json.loads((cache/'download.json').read_text())
    assert download['status'] == 'completed' and download['revision'] == cfg['model_revision']
    # The downloader already streamed all file hashes against upstream identities.
    for file in download['files']:
        assert (cache/file['path']).stat().st_size == file['bytes']
    random.seed(cfg['seed']); np.random.seed(cfg['seed']); torch.manual_seed(cfg['seed'])
    torch.set_num_threads(4)
    device = torch.device(args.device)
    dtype = torch.bfloat16 if args.device == 'cuda' else torch.float32
    if args.device == 'cuda':
        assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(cfg['gpu_memory_fraction'], 0)
        torch.cuda.manual_seed_all(cfg['seed'])
        torch.backends.cuda.matmul.allow_tf32 = False
    processor = AutoProcessor.from_pretrained(cache, local_files_only=True, trust_remote_code=False)
    processor.image_processor.size = {'longest_edge': cfg['image_longest_edge']}
    processor.image_processor.do_image_splitting = cfg['do_image_splitting']
    runtime = {'python': platform.python_version(), 'torch': torch.__version__,
               'cuda_runtime': torch.version.cuda, 'transformers': transformers.__version__,
               'numpy': np.__version__, 'pillow': PIL.__version__, 'device': args.device,
               'dtype': str(dtype), 'gpu': torch.cuda.get_device_name(0) if args.device == 'cuda' else None,
               'source_sha256': sha(__file__), 'config_sha256': sha(args.config),
               'cases_sha256': sha(args.cases), 'download_receipt_sha256': sha(cache/'download.json'),
               'seed': cfg['seed'], 'processor': processor.image_processor.to_dict()}
    write_json(output/'runtime.json', runtime)
    (output/'requirements.resolved.txt').write_bytes(Path('/opt/requirements.resolved.txt').read_bytes())
    # Prepare all public inputs before any inference. Do not write or expose evaluation labels here.
    jobs = []
    for index, case in enumerate(cases):
        public_case = {key: case[key] for key in ('task', 'subtask', 'start', 'end')}
        # Alternate condition order across cases; no model state is retained between requests.
        conditions = cfg['conditions'] if index % 2 == 0 else list(reversed(cfg['conditions']))
        for condition in conditions:
            text, paths, descriptors = prompt_payload(public_case, condition, cfg, processor)
            assert len(paths) == (3 if condition == 'end_only' else 6)
            for descriptor in descriptors:
                descriptor['sha256'] = sha(Path(args.images)/descriptor['relative_path'])
            jobs.append({'case': case['id'], 'condition': condition, 'prompt': text, 'images': descriptors})
    assert len(jobs) == cfg['expected_predictions']
    write_json(output/'inputs.json', jobs)
    print('INPUTS_READY', len(jobs), flush=True)
    start_load = time.perf_counter()
    model = AutoModelForImageTextToText.from_pretrained(
        cache, local_files_only=True, trust_remote_code=False, torch_dtype=dtype,
        low_cpu_mem_usage=True, attn_implementation=cfg['attention']).to(device).eval()
    runtime['model_load_seconds'] = time.perf_counter() - start_load
    runtime['model_class'] = type(model).__name__
    runtime['parameters'] = sum(p.numel() for p in model.parameters())
    runtime['attention_implementation'] = model.config._attn_implementation
    write_json(output/'runtime.json', runtime)
    eos = model.generation_config.eos_token_id
    eos_ids = {eos} if isinstance(eos, int) else set(eos)
    with (output/'predictions.jsonl').open('x') as stream, torch.inference_mode():
        for number, job in enumerate(jobs):
            images = []
            for desc in job['images']:
                with Image.open(Path(args.images)/desc['relative_path']) as img:
                    images.append(img.convert('RGB'))
            tic = time.perf_counter()
            if args.device == 'cuda':
                torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
            inputs = processor(text=job['prompt'], images=images, return_tensors='pt')
            tensor_shapes = {key: list(value.shape) for key, value in inputs.items() if torch.is_tensor(value)}
            input_tokens = int(inputs['input_ids'].shape[-1])
            image_tokens = int((inputs['input_ids'] == model.config.image_token_id).sum())
            assert image_tokens == len(images) * processor.image_seq_len, (image_tokens, len(images))
            assert input_tokens + cfg['max_new_tokens'] < model.config.text_config.max_position_embeddings
            inputs = {key: value.to(device=device, dtype=dtype if value.is_floating_point() else value.dtype)
                      for key, value in inputs.items()}
            generated = model.generate(**inputs, do_sample=cfg['do_sample'], max_new_tokens=cfg['max_new_tokens'],
                                       use_cache=cfg['use_cache'])
            answer_ids = generated[0, input_tokens:]
            answer = processor.decode(answer_ids, skip_special_tokens=True)
            parsed, error = parse_response(answer)
            if args.device == 'cuda': torch.cuda.synchronize()
            record = {'case': job['case'], 'condition': job['condition'], 'raw_response': answer,
                      'parsed': parsed, 'parse_error': error, 'input_tokens': input_tokens,
                      'image_tokens': image_tokens, 'image_count': len(images), 'tensor_shapes': tensor_shapes,
                      'generated_tokens': int(answer_ids.numel()),
                      'terminated_with_eos': bool(answer_ids.numel() and int(answer_ids[-1]) in eos_ids),
                      'elapsed_seconds': time.perf_counter()-tic,
                      'peak_allocated_bytes': torch.cuda.max_memory_allocated() if args.device=='cuda' else None,
                      'peak_reserved_bytes': torch.cuda.max_memory_reserved() if args.device=='cuda' else None,
                      'prompt_sha256': hashlib.sha256(job['prompt'].encode()).hexdigest()}
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False)+'\n'); stream.flush(); os.fsync(stream.fileno())
            print('PREDICTION', number+1, job['case'], job['condition'],
                  parsed['verdict'] if parsed else error, round(record['elapsed_seconds'],3), flush=True)
            del inputs, generated, answer_ids
    write_json(output/'completion.json', {'status':'completed','predictions':len(jobs),
                                          'predictions_sha256':sha(output/'predictions.jsonl'),
                                          'inputs_sha256':sha(output/'inputs.json')})
    print('COMPLETED', len(jobs), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='/study/vlm_config.json')
    parser.add_argument('--cases', default='/prepared/cases.json')
    parser.add_argument('--images', default='/prepared/originals')
    parser.add_argument('--model', default='/model')
    parser.add_argument('--device', choices=['cuda','cpu'], default='cuda')
    parser.add_argument('--output', default='/output')
    main(parser.parse_args())
