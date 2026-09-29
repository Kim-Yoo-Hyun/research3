"""Create a compact, tracked index from already verified Docker outputs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT/'runs/q16/dp_reference'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    config_path=OUT/'inspect1/config.json'
    parity_path=OUT/'parity1/assessment.json'
    eval_path=OUT/'eval1/evaluation.json'
    eval_verify_path=OUT/'eval1/verification.json'
    branch_path=OUT/'branch1/assessment.json'
    branch_verify_path=OUT/'branch1/verification.json'
    config=json.loads(config_path.read_text())
    parity=json.loads(parity_path.read_text())
    evaluation=json.loads(eval_path.read_text())
    eval_verify=json.loads(eval_verify_path.read_text())
    branch=json.loads(branch_path.read_text())
    branch_verify=json.loads(branch_verify_path.read_text())
    assert eval_verify['status']==branch_verify['status']=='passed'
    assert eval_verify['checked_traces']==16 and branch_verify['checked_traces']==8
    assert all(row['max_source_vs_maintained_drift']<=1e-8 and
               row['source_vs_keypoint_contact_match'] for row in parity['cases'])
    image=json.loads(sorted((OUT/'jobs').glob('*_branch.json'))[-1].read_text())['image_id']
    compact=dict(status='exploratory_verified', source_commit=evaluation['source_commit'],
                 source_archive_sha256=digest(ROOT/'external/q16'/f'diffusion_policy-{evaluation["source_commit"]}.tar.gz'),
                 checkpoint_sha256=config['checkpoint_sha256'], image_id=image,
                 environment='original PushTEnv/PushTKeypointsEnv, legacy=True',
                 policy_input='2x20 keypoint/agent-position; all masks visible',
                 action='2D absolute target, 8-step chunks, 100 diffusion steps',
                 policy_training_max_episodes=config['configured_task']['dataset']['max_train_episodes'],
                 comparison='prior 5D ridge BC on same initial states; representation and training budget not matched',
                 seeds=evaluation['seeds'], native_success='coverage >0.95',
                 evaluation=[{k:r[k] for k in ('seed','route','steps','any_success',
                                              'max_coverage','final_coverage','any_contact',
                                              'object_motion_px','rollout_seconds','trace','sha256')}
                             for r in evaluation['rows']],
                 branch_selection=branch['selection'],
                 branches=[{k:r[k] for k in ('seed','route','branch_step','target','any_success',
                                            'max_coverage','final_coverage','prefix_max_drift',
                                            'rollout_seconds','trace','sha256')}
                           for r in branch['rows']],
                 parity=[{k:r[k] for k in ('seed','max_source_vs_maintained_drift',
                                          'keypoint_agent_position_drift',
                                          'source_vs_keypoint_contact_match',
                                          'source_vs_maintained_contact_match')}
                         for r in parity['cases']],
                 docker_verification=dict(evaluation=eval_verify['checked_traces'],
                                          branches=branch_verify['checked_traces'],
                                          max_replay_drift=max(eval_verify['max_replay_drift'],
                                                               branch_verify['max_replay_drift'])),
                 artifact_sha256={str(path.relative_to(OUT)):digest(path) for path in
                                  (config_path,parity_path,eval_path,eval_verify_path,
                                   branch_path,branch_verify_path)},
                 claim_boundary='Two selected, exploratory branch cases; one feedback and arbitrary +x rescue do not establish predictive-model value or generality.')
    output=HERE/'dp_reference_summary.json'
    output.write_text(json.dumps(compact,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),sha256=digest(output)),indent=2))


if __name__=='__main__':
    main()
