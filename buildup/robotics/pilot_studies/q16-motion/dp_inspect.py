"""Inspect official checkpoint schema and installed runtime inside Docker."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil

import dill
from omegaconf import OmegaConf
import torch

ROOT = Path('/output')
OUT = ROOT / 'inspect1'
CHECKPOINT = Path('/checkpoint/model.ckpt')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    payload = torch.load(CHECKPOINT, map_location='cpu', pickle_module=dill, weights_only=False)
    cfg = payload['cfg']
    def value(path):
        try:
            return OmegaConf.select(cfg, path, throw_on_missing=True)
        except Exception:
            return None
    state_dicts = payload['state_dicts']
    weights = {}
    for name, state in state_dicts.items():
        if not isinstance(state, dict):
            continue
        tensors = [(key, entry) for key, entry in state.items() if torch.is_tensor(entry)]
        weights[name] = dict(entries=len(state), tensors=len(tensors),
                             elements=sum(item.numel() for _, item in tensors),
                             first_shapes={key:list(item.shape) for key,item in tensors[:12]})
    if (Path('/recipe/installed.dp.lock')).exists():
        shutil.copy2('/recipe/installed.dp.lock', ROOT/'installed.dp.lock')
    try:
        matplotlib_version = importlib.metadata.version('matplotlib')
    except importlib.metadata.PackageNotFoundError:
        matplotlib_version = None
    doc = dict(status='completed', checkpoint_bytes=CHECKPOINT.stat().st_size,
               checkpoint_sha256=digest(CHECKPOINT), torch_version=torch.__version__,
               matplotlib_version=matplotlib_version,
               policy_target=value('policy._target_'), task_name=value('task.name'),
               task_obs_dim=value('task.obs_dim'), task_action_dim=value('task.action_dim'),
               horizon=value('horizon'), n_obs_steps=value('n_obs_steps'),
               n_action_steps=value('n_action_steps'), n_latency_steps=value('n_latency_steps'),
               inference_steps=value('policy.num_inference_steps'),
               obs_as_global_cond=value('policy.obs_as_global_cond'),
               action_step_convention=value('policy.oa_step_convention'),
               keypoint_visible_rate=value('keypoint_visible_rate'),
               runner_target=value('task.env_runner._target_'),
               runner_legacy_test=value('task.env_runner.legacy_test'),
               runner_max_steps=value('task.env_runner.max_steps'),
               use_ema=value('training.use_ema'),
               state_dicts=weights, payload_keys=list(payload.keys()),
               configured_task=OmegaConf.to_container(cfg.task, resolve=False))
    (OUT/'config.json').write_text(json.dumps(doc, indent=2, default=str) + '\n')
    print(json.dumps({k:doc[k] for k in ('checkpoint_bytes','checkpoint_sha256','policy_target',
                                         'task_obs_dim','task_action_dim','horizon',
                                         'n_obs_steps','n_action_steps','inference_steps',
                                         'runner_target','runner_legacy_test','use_ema','state_dicts')},
                     indent=2, default=str), flush=True)


if __name__ == '__main__':
    main()
