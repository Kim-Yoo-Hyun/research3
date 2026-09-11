"""Docker-only construction diagnostic. All native forward operations fail closed."""
import ast
from pathlib import Path
from types import SimpleNamespace
import torch
from torch import nn

CALLS=[]

def unavailable(*args,**kwargs):
    CALLS.append('native_forward')
    raise RuntimeError('construction-only diagnostic: native operation unavailable')

class UnavailableOperator(nn.Module):
    def __init__(self,*args,**kwargs):super().__init__()
    def forward(self,*args,**kwargs):return unavailable(*args,**kwargs)

class SourceTransform(ast.NodeTransformer):
    def __init__(self):self.imports=[];self.cpu_allocations=0;self.decorators=0
    def visit_Import(self,node):
        self.imports.append(ast.unparse(node));return None
    def visit_ImportFrom(self,node):
        self.imports.append(ast.unparse(node));return None
    def visit_ClassDef(self,node):
        self.decorators+=len(node.decorator_list);node.decorator_list=[]
        return self.generic_visit(node)
    def visit_Call(self,node):
        node=self.generic_visit(node)
        if isinstance(node.func,ast.Attribute) and node.func.attr=='cuda':
            assert not node.args and not node.keywords
            self.cpu_allocations+=1
            return node.func.value
        return node

def construct(config):
    base=Path(__file__).parent/'upstream';receipts=[]
    common={'torch':torch,'nn':nn,'KNN':UnavailableOperator,
            'pointnet2_utils':SimpleNamespace(furthest_point_sample=unavailable,gather_operation=unavailable),
            'ChamferDistanceL1':UnavailableOperator,'ChamferDistanceL2':UnavailableOperator,
            'DropPath':UnavailableOperator,'trunc_normal_':nn.init.trunc_normal_}
    scopes={}
    for filename,allocation,decorators in [('dgcnn_group.py',0,0),('SGrasp.py',1,1)]:
        path=base/filename;tree=ast.parse(path.read_text());transform=SourceTransform();tree=transform.visit(tree);ast.fix_missing_locations(tree)
        assert transform.cpu_allocations==allocation and transform.decorators==decorators
        scope=dict(common)
        if filename=='SGrasp.py':scope['DGCNN_Grouper']=scopes['dgcnn_group.py']['DGCNN_Grouper']
        exec(compile(tree,str(path),'exec'),scope)
        scopes[filename]=scope
        receipts.append({'file':filename,'removed_imports':transform.imports,'cuda_allocation_to_cpu':allocation,'registry_decorators_removed':decorators})
    model=scopes['SGrasp.py']['SGrasp'](SimpleNamespace(**config)).cpu().eval()
    assert not CALLS
    return model,receipts
