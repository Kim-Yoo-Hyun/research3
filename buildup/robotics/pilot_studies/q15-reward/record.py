"""Recording-only hooks after optimizer update; no gradient or RNG operations."""
import dataclasses
import time
from pathlib import Path
import torch
from common import configuration, write_json, sha

START=None

def begin(args,envs,agent):
    global START
    START=time.monotonic()
    write_json('config.json',dict(args=vars(args),environment=configuration(envs.unwrapped),
                                initial_model_sha256=tensor_hash(agent)))

def tensor_hash(agent):
    import hashlib
    h=hashlib.sha256()
    for name,value in sorted(agent.state_dict().items()):
        h.update(name.encode()); h.update(value.detach().cpu().numpy().tobytes())
    return h.hexdigest()

def after_update(args,envs,agent,optimizer,iteration,global_step,rollout_time,update_time):
    row=dict(update=iteration,transitions=global_step,elapsed_seconds=time.monotonic()-START,
             rollout_seconds=rollout_time,update_seconds=update_time,
             cuda_peak_bytes=torch.cuda.max_memory_allocated(),reward_calls=envs.unwrapped.reward_calls)
    import json
    with Path('training.jsonl').open('a') as f: f.write(json.dumps(row)+'\n')
    if iteration in (97,195) or args.num_iterations!=195 and iteration==args.num_iterations:
        path=Path(f'checkpoint_{iteration}.pt')
        assert not path.exists()
        torch.save(agent.state_dict(),path)
        write_json(path.with_suffix('.json'),dict(**row,seed=args.seed,sha256=sha(path),
            save_timing='after optimizer update',reward_variant=envs.unwrapped.reward_variant))
        write_json('reward_audit.json',envs.unwrapped.audit_samples)
