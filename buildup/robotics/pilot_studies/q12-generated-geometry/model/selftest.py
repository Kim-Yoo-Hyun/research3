"""Synthetic contract checks; no real checkpoint or cloud is read."""
import torch
from schema import choose,differences,schema
from construction import construct,unavailable,CALLS

state={'module.weight':torch.ones(2,3)}
root,selected,prefix=choose({'_model':state},['model','base_model','_model'])
assert root=='_model' and prefix and list(selected)==['weight']
for bad in [{'model':state,'_model':state},{'_model':{'module.a':torch.ones(1),'b':torch.ones(1)}},{'unrecognized':state}]:
    try:choose(bad,['model','base_model','_model'])
    except ValueError:pass
    else:raise AssertionError('ambiguous/mixed/unknown checkpoint accepted')
x=schema({'a':torch.ones(2,3)});y=schema({'a':torch.ones(3,2),'b':torch.zeros(1)})
d=differences(x,y);assert d['unexpected']==['b'] and 'a' in d['mismatched']
model,changes=construct({'trans_dim':384,'knn_layer':1,'num_pred':6144,'num_query':96})
state=model.state_dict();first=next(iter(state));bad=dict(state);bad.pop(first)
try:model.load_state_dict(bad,strict=True)
except RuntimeError:pass
else:raise AssertionError('strict load accepted a missing state tensor')
model.load_state_dict(state,strict=True)
assert not CALLS and sum(x['cuda_allocation_to_cpu'] for x in changes)==1
try:unavailable()
except RuntimeError:pass
else:raise AssertionError('native forward placeholder did not fail')
print('PASS: root/prefix rejection, shape mismatch, original construction, strict missing-key rejection, native-forward guard')
