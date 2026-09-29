"""Summarize verified Docker continuation manifests without running methods on host."""
import hashlib
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'runs/q16/dp_reference'


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    paths={k:BASE/v for k,v in {
        'input_first':'observation1/assessment.json',
        'input_full':'observation2/assessment.json',
        'dataset':'traincontract1/assessment.json',
        'fit':'finetune1/fit.json',
        'evaluation':'compare1/evaluation.json',
        'verification':'compare1/verification.json'}.items()}
    data={k:json.loads(v.read_text()) for k,v in paths.items()}
    assert data['input_first']['status']==data['input_full']['status']=='incompatible'
    assert data['dataset']['status']==data['verification']['status']=='passed'
    assert data['fit']['status']==data['evaluation']['status']=='completed'
    assert data['verification']['checked_traces']==64
    evaluation=data['evaluation']
    verified={(r['seed'],r['route']):r for r in data['verification']['rows']}
    routes={}
    for route in ('frozen','feedback','prediction','updated'):
        rows=[r for r in evaluation['rows'] if r['route']==route]
        assert len(rows)==16
        frozen={r['seed']:r for r in evaluation['rows'] if r['route']=='frozen'}
        changed_gains=[verified[(r['seed'],route)]['one_step_overlap_gain_vs_frozen']
                       for r in rows if r['intervention_changed']]
        routes[route]=dict(success=sum(r['any_success'] for r in rows),total=len(rows),
            mean_max_coverage=statistics.mean(r['max_coverage'] for r in rows),
            mean_final_coverage=statistics.mean(r['final_coverage'] for r in rows),
            rescues_vs_frozen=sum(r['any_success'] and not frozen[r['seed']]['any_success'] for r in rows),
            harms_vs_frozen=sum(not r['any_success'] and frozen[r['seed']]['any_success'] for r in rows),
            mean_max_coverage_gain_vs_frozen=statistics.mean(
                r['max_coverage']-frozen[r['seed']]['max_coverage'] for r in rows),
            mean_one_step_overlap_gain_when_changed=(statistics.mean(changed_gains)
                                                     if changed_gains else None),
            any_contact=sum(r['any_contact'] for r in rows),
            intervention_attempts=sum(r['intervention_attempted'] for r in rows),
            action_changes=sum(r['intervention_changed'] for r in rows),
            total_rollout_seconds=sum(r['rollout_seconds'] for r in rows),
            total_policy_inference_seconds=sum(r['policy_inference_seconds'] for r in rows),
            total_correction_selection_seconds=sum(r['correction_selection_seconds'] for r in rows))
    paired=[]
    for seed in evaluation['seeds']:
        rows={r['route']:r for r in evaluation['rows'] if r['seed']==seed}
        assert len(rows)==4
        paired.append(dict(seed=seed,success={k:r['any_success'] for k,r in rows.items()},
                           max_coverage={k:r['max_coverage'] for k,r in rows.items()},
                           feedback_attempted=rows['feedback']['intervention_attempted'],
                           prediction_attempted=rows['prediction']['intervention_attempted'],
                           prediction_changed=rows['prediction']['intervention_changed'],
                           prediction_reason=(rows['prediction']['decision']['model']['decision_reason']
                              if rows['prediction']['decision'] else None)))
    model_decisions=[r['decision']['model'] for r in evaluation['rows']
                     if r['route']=='prediction' and r['decision']]
    reason_counts={reason:sum(d['decision_reason']==reason for d in model_decisions)
                   for reason in ('selected','no_predicted_gain','out_of_distribution')}
    artifact_hashes={k:digest(v) for k,v in paths.items()}
    output=dict(status='verified_exploratory',source_commit=evaluation['source_commit'],
                source_checkpoint_sha256=evaluation['source_checkpoint_sha256'],
                updated_checkpoint_sha256=evaluation['updated_checkpoint_sha256'],
                transition_model_sha256=evaluation['transition_model_sha256'],
                dataset_sha256=evaluation['dataset_sha256'],
                image_id=json.loads(sorted((BASE/'jobs').glob('*_compare.json'))[-1].read_text())['image_id'],
                seeds=evaluation['seeds'],routes=routes,paired=paired,
                prediction_decision_reasons=reason_counts,
                validation_loss_before=data['fit']['validation_loss_before'],
                validation_loss_after=data['fit']['validation_loss_after'],
                update_training_seconds=data['fit']['training_seconds'],
                updated_checkpoint_bytes=data['fit']['checkpoint_bytes'],
                input_status='Stored keypoint/state exact-pose check failed; official stored-keypoint training contract used.',
                claim_boundary='Exploratory 16 paired seeds, one fixed correction, small fixed policy update; no generality or method superiority claim.',
                docker_verification=dict(checked_traces=data['verification']['checked_traces'],
                    max_replay_drift=data['verification']['max_replay_drift']),
                artifact_sha256=artifact_hashes)
    target=HERE/'dp_continuation_summary.json'
    target.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(path=str(target),sha256=digest(target),routes=routes,
                          prediction_decision_reasons=reason_counts),indent=2),flush=True)


if __name__=='__main__':
    main()
