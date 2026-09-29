"""Fixed-budget same-extra-demonstration update of released Push-T EMA policy."""
import hashlib
import json
from pathlib import Path
import time

import dill
import hydra
import numpy as np
from omegaconf import OmegaConf
import torch

ROOT=Path('/output')
OUT=ROOT/'finetune1'
CHECKPOINT=Path('/checkpoint/model.ckpt')
DATA=ROOT/'traincontract1/dataset.npz'
STEPS=300
BATCH=64
LR=1e-5
SEED=31415


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def indices(ends,begin,stop):
    start=0 if begin==0 else int(ends[begin-1])
    output=[]
    offsets=np.arange(16,dtype=np.int64)
    for ep in range(begin,stop):
        ep_start=start if ep==begin else int(ends[ep-1])
        ep_end=int(ends[ep])
        length=ep_end-ep_start
        for local_start in range(-1,length-16+7+1):
            local=np.clip(local_start+offsets,0,length-1)
            output.append(ep_start+local)
    return np.asarray(output,np.int64)


def batch_tensors(obs,action,index,device):
    return {'obs':torch.from_numpy(obs[index]).to(device),
            'action':torch.from_numpy(action[index]).to(device)}


def validation_loss(policy,obs,action,selection):
    torch.manual_seed(27182)
    torch.cuda.manual_seed_all(27182)
    policy.eval()
    losses=[]
    with torch.inference_mode():
        for i in range(0,len(selection),BATCH):
            batch=batch_tensors(obs,action,selection[i:i+BATCH],'cuda:0')
            losses.append(float(policy.compute_loss(batch)))
    return float(np.mean(losses))


def main():
    OUT.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    contract=json.loads((ROOT/'traincontract1/assessment.json').read_text())
    assert contract['status']=='passed' and contract['dataset_sha256']==digest(DATA)
    with np.load(DATA,allow_pickle=False) as dataset:
        obs=dataset['obs'].copy();action=dataset['action'].copy();ends=dataset['ends'].copy()
    assert obs.shape==(25650,20) and action.shape==(25650,2)
    train=indices(ends,0,160)
    valid=indices(ends,160,180)
    assert np.max(train)<ends[159] and np.min(valid)>=ends[159]
    rng=np.random.default_rng(SEED)
    validation_sample=valid[rng.choice(len(valid),size=min(256,len(valid)),replace=False)]
    OmegaConf.register_new_resolver('eval',eval,replace=True)
    payload=torch.load(CHECKPOINT,map_location='cpu',pickle_module=dill,weights_only=False)
    policy=hydra.utils.instantiate(payload['cfg'].policy)
    policy.load_state_dict(payload['state_dicts']['ema_model'],strict=True)
    policy.to('cuda:0')
    before=validation_loss(policy,obs,action,validation_sample)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    optimizer=torch.optim.AdamW(policy.model.parameters(),lr=LR)
    policy.train()
    losses=[]
    started=time.perf_counter()
    for step in range(1,STEPS+1):
        chosen=train[rng.integers(len(train),size=BATCH)]
        batch=batch_tensors(obs,action,chosen,'cuda:0')
        optimizer.zero_grad(set_to_none=True)
        loss=policy.compute_loss(batch)
        assert torch.isfinite(loss)
        loss.backward()
        grad=float(torch.nn.utils.clip_grad_norm_(policy.model.parameters(),1.0))
        optimizer.step()
        losses.append(float(loss.detach()))
        if step%50==0:
            print(json.dumps(dict(step=step,loss=float(np.mean(losses[-50:])),
                                  gradient_norm_before_clip=grad,
                                  elapsed_seconds=time.perf_counter()-started)),flush=True)
    torch.cuda.synchronize()
    training_seconds=time.perf_counter()-started
    after=validation_loss(policy,obs,action,validation_sample)
    path=OUT/'checkpoint.pt'
    torch.save({'policy_state_dict':{k:v.cpu() for k,v in policy.state_dict().items()},
                'steps':STEPS,'data_sha256':digest(DATA),'source_checkpoint_sha256':digest(CHECKPOINT)},path)
    doc=dict(status='completed',source_checkpoint_sha256=digest(CHECKPOINT),
             source_config_sha256=digest(ROOT/'inspect1/config.json'),
             dataset_sha256=digest(DATA),train_episodes=[0,159],valid_episodes=[160,179],
             train_rows=int(ends[159]),validation_rows=int(ends[179]-ends[159]),
             train_windows=len(train),validation_windows=len(valid),
             validation_sample_windows=len(validation_sample),
             policy_input='stored 9x2 keypoints plus stored agent XY, not regenerated from state',
             normalizer='frozen released EMA normalizer',base_weights='released EMA',
             optimizer='AdamW',gradient_clip_norm=1.0,steps=STEPS,batch_size=BATCH,
             learning_rate=LR,seed=SEED,validation_noise_seed=27182,
             validation_loss_before=before,validation_loss_after=after,
             train_loss_first50=float(np.mean(losses[:50])),
             train_loss_last50=float(np.mean(losses[-50:])),
             training_seconds=training_seconds,device='cuda:0',
             checkpoint=path.name,checkpoint_bytes=path.stat().st_size,
             checkpoint_sha256=digest(path))
    (OUT/'fit.json').write_text(json.dumps(doc,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:doc[k] for k in ('status','train_windows','validation_loss_before',
                        'validation_loss_after','train_loss_last50','training_seconds',
                        'checkpoint_bytes','checkpoint_sha256')},indent=2),flush=True)


if __name__=='__main__':
    main()
