"""Small residual MLP with matched capacity/data for history-only and action inputs."""
from pathlib import Path
import json
import numpy as np
import torch
from task import DT, HORIZON


def network(dim):
    return torch.nn.Sequential(torch.nn.Linear(dim,64),torch.nn.SiLU(),
                               torch.nn.Linear(64,64),torch.nn.SiLU(),torch.nn.Linear(64,3))


class Predictor:
    def __init__(self, path):
        d=torch.load(path,map_location='cpu',weights_only=False)
        self.mode=d['mode'];self.mean=d['mean'];self.std=d['std'];self.yscale=d['yscale']
        self.net=network(len(self.mean));self.net.load_state_dict(d['weights']);self.net.eval()

    def predict(self, f, actions):
        fs=np.tile(f,(len(actions),1)) if f.ndim==1 else f
        act=actions if self.mode=='action' else np.zeros_like(actions)
        x=np.concatenate([fs,act],1)
        with torch.no_grad():
            residual=self.net(torch.from_numpy((x-self.mean)/self.std).float()).numpy()*self.yscale
        # Same bounded residual for both models; this is a pilot stability constraint.
        return fs[:,7:10]*(DT*HORIZON)+np.clip(residual,-0.05,0.05)


def fit_models(data_dir,out):
    records=[]
    for p in sorted(Path(data_dir).glob('*.npz')):
        m=json.loads(p.with_suffix('.json').read_text())['meta']
        if not 10000<=m['seed']<10080:continue
        d=dict(np.load(p));records.append((m,d))
    assert len(records)==160,len(records)
    train=[d for m,d in records if m['seed']<10064]
    val=[d for m,d in records if m['seed']>=10064]
    def assemble(ds):
        f=np.concatenate([d['features'] for d in ds]);a=np.concatenate([d['row_action'] for d in ds])
        delta=np.concatenate([d['delta'] for d in ds])
        return f.astype(np.float32),a.astype(np.float32),delta.astype(np.float32)
    f,a,y=assemble(train);vf,va,vy=assemble(val)
    residual=y-f[:,7:10]*(DT*HORIZON);yscale=np.maximum(residual.std(0),0.002)
    metrics={}
    for mode in ('history','action'):
        torch.manual_seed(16023)
        x=np.concatenate([f,a if mode=='action' else np.zeros_like(a)],1)
        vx=np.concatenate([vf,va if mode=='action' else np.zeros_like(va)],1)
        mean=x.mean(0);std=np.maximum(x.std(0),0.01)
        tx=torch.tensor((x-mean)/std);ty=torch.tensor(residual/yscale)
        tvx=torch.tensor((vx-mean)/std);tvy=torch.tensor((vy-vf[:,7:10]*(DT*HORIZON))/yscale)
        net=network(x.shape[1]);optimizer=torch.optim.AdamW(net.parameters(),lr=0.001,weight_decay=1e-4)
        best=float('inf');best_weights=None;best_epoch=None;curve=[]
        for epoch in range(100):
            net.train();order=torch.randperm(len(tx))
            for batch in order.split(256):
                optimizer.zero_grad();loss=((net(tx[batch])-ty[batch])**2).mean();loss.backward();optimizer.step()
            net.eval()
            with torch.no_grad():v=float(((net(tvx)-tvy)**2).mean())
            curve.append(v)
            if v<best:
                best=v;best_epoch=epoch+1;best_weights={k:t.detach().clone() for k,t in net.state_dict().items()}
        path=out/(mode+'.pt')
        torch.save(dict(mode=mode,mean=mean,std=std,yscale=yscale,weights=best_weights,
                        train_seeds=list(range(10000,10064)),val_seeds=list(range(10064,10080)),
                        architecture='Linear64-SiLU-Linear64-SiLU-Linear3',fit_seed=16023),path)
        pred=Predictor(path).predict(vf,va)
        metrics[mode]=dict(parameters=sum(t.numel() for t in net.parameters()),train_rows=len(tx),
                           val_rows=len(tvx),best_epoch=best_epoch,val_normalized_mse=best,
                           val_position_rmse_m=float(np.sqrt(np.mean(np.sum((pred-vy)**2,1)))),
                           curve=curve)
        print(mode,metrics[mode]['val_position_rmse_m'],flush=True)
    metrics['constant_velocity_val_rmse_m']=float(np.sqrt(np.mean(np.sum((vf[:,7:10]*(DT*HORIZON)-vy)**2,1))))
    metrics['data_episodes']=len(records)
    return metrics
