"""Independent checkpoint metadata check in CPU Docker; no construction or forward."""
import hashlib,json
from pathlib import Path
import torch
base=Path(__file__).parent
p=Path('/checkpoint/model.pth');result=json.loads(Path('/result/schema.json').read_text())
h=hashlib.sha256()
with p.open('rb') as f:
    for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
assert h.hexdigest()==result['checkpoint_sha256']
checkpoint=torch.load(p,map_location='cpu',weights_only=True)
assert sorted(checkpoint)==result['checkpoint_root_keys']
state=checkpoint[result['selected_root']]
normalized={k.removeprefix('module.'):v for k,v in state.items()}
assert len(normalized)==len(state)==result['checkpoint_tensor_count']==408
for k,v in normalized.items():
    expected={'shape':list(v.shape),'dtype':str(v.dtype),'numel':v.numel()}
    assert expected==result['checkpoint_schema'][k]==result['model_schema'][k]
    assert not v.is_floating_point() or torch.isfinite(v).all().item()
assert result['strict_load'] and result['loaded_tensors_equal']==len(state)
assert result['differences']=={'missing':[],'unexpected':[],'mismatched':{}}
assert result['forward_executed'] is False and result['native_operator_calls']==0
receipt={'status':'VERIFIED_CHECKPOINT_SCHEMA','checkpoint_sha256':h.hexdigest(),'schema_sha256':hashlib.sha256(Path('/result/schema.json').read_bytes()).hexdigest(),'tensor_count':len(state),'strict_loading_receipt_consistent':True,'forward_verified':False,'boundary':'independent checkpoint metadata/finite check; model constructor and strict loading are evidenced by original probe'}
out=Path('/verification/verification.json');assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
