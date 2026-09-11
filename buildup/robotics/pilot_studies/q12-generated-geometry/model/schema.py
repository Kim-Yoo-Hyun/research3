"""CPU Docker probe of checkpoint keys and exact model-state compatibility; no forward."""
import argparse
import hashlib
import json
from pathlib import Path
import torch
from construction import construct,CALLS


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()

def choose(checkpoint,allowed):
    found=[k for k in allowed if k in checkpoint and isinstance(checkpoint[k],dict)]
    if len(found)!=1:raise ValueError('Expected one unambiguous state root: '+repr(found))
    root=found[0];state=checkpoint[root]
    if not state or not all(isinstance(k,str) and isinstance(v,torch.Tensor) for k,v in state.items()):
        raise ValueError('state must contain only named tensors')
    prefix=[k.startswith('module.') for k in state]
    if any(prefix) and not all(prefix):raise ValueError('mixed module prefix')
    return root,{k[7:] if all(prefix) else k:v for k,v in state.items()},bool(all(prefix))

def schema(state):
    return {k:{'shape':list(v.shape),'dtype':str(v.dtype),'numel':v.numel()} for k,v in sorted(state.items())}

def differences(expected,observed):
    return {'missing':sorted(set(expected)-set(observed)),
            'unexpected':sorted(set(observed)-set(expected)),
            'mismatched':{k:{'expected':expected[k],'observed':observed[k]} for k in sorted(set(expected)&set(observed)) if expected[k]!=observed[k]}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    base=Path(__file__).parent;protocol=json.loads((base/'schema_protocol.json').read_text());frozen=json.loads((base/'schema_freeze.json').read_text())
    for name,h in frozen['files'].items():assert sha(base/name)==h,name
    assert not a.output.exists();a.output.mkdir(parents=True)
    result={'device':'cpu','torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'checkpoint_bytes':a.checkpoint.stat().st_size,'checkpoint_sha256':sha(a.checkpoint),'protocol_sha256':sha(base/'schema_protocol.json'),'forward_executed':False,'strict_load':False}
    try:
        assert result['checkpoint_bytes']==protocol['checkpoint']['bytes']
        assert result['checkpoint_sha256']==protocol['checkpoint']['sha256']
        torch.set_num_threads(protocol['cpus']);torch.manual_seed(protocol['seed'])
        checkpoint=torch.load(a.checkpoint,map_location='cpu',weights_only=True)
        result['checkpoint_root_keys']=sorted(checkpoint)
        root,state,prefix=choose(checkpoint,protocol['allowed_state_roots'])
        result.update(selected_root=root,module_prefix_removed=prefix,upstream_loader_accepts_root=root in ['model','base_model'])
        observed=schema(state)
        model,adaptations=construct(protocol['model_config']);expected=schema(model.state_dict())
        result.update(construction_adaptations=adaptations,checkpoint_tensor_count=len(observed),model_tensor_count=len(expected),parameter_count=sum(p.numel() for p in model.parameters()))
        diff=differences(expected,observed);result['differences']=diff
        result['checkpoint_schema']=observed;result['model_schema']=expected
        if any(diff.values()):result['decision']='STOP_MODEL_STATE_MISMATCH'
        else:
            nonfinite=[k for k,v in state.items() if v.is_floating_point() and not torch.isfinite(v).all().item()]
            result['nonfinite_tensors']=nonfinite
            if nonfinite:result['decision']='STOP_NONFINITE_CHECKPOINT'
            else:
                model.load_state_dict(state,strict=True)
                matches={k:torch.equal(v,state[k]) for k,v in model.state_dict().items()}
                assert all(matches.values())
                result.update(strict_load=True,loaded_tensors_equal=len(matches),decision='STATE_COMPATIBLE_FORWARD_UNVERIFIED')
        assert not CALLS
        result['native_operator_calls']=len(CALLS)
    except Exception as error:
        result['decision']='STOP_CHECKPOINT_OR_CONSTRUCTION';result['error']=str(error)
    (a.output/'schema.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    assert (a.output/'schema.json').stat().st_size <= protocol['output_cap_mib']*1024**2
    print(json.dumps({k:v for k,v in result.items() if k in ['decision','selected_root','checkpoint_root_keys','model_tensor_count','checkpoint_tensor_count','parameter_count','strict_load','error','upstream_loader_accepts_root']}))

if __name__=='__main__':main()
