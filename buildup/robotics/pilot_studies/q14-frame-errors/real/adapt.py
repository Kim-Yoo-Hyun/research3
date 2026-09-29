"""Apply explicit inference-only compatibility edits inside the Docker build."""
from pathlib import Path
import hashlib
import json

root = Path('/opt/dream/dream')
changes = []
for name in ['__init__.py', 'network.py', 'models.py']:
    p = root/name
    old = p.read_text()
    new = old
    if name == '__init__.py':
        # Exclude unused training/dataset analysis imports and their dependency tree.
        for text in ['from .analysis import *\n', 'from .datasets import *\n']:
            assert new.count(text) == 1
            new = new.replace(text, '')
    elif name == 'network.py':
        assert new.count('.cuda()') >= 5
        new = new.replace('.cuda()', '.to("cpu")')
    else:
        text = 'vgg_t = tviz_models.vgg19(pretrained=True).features'
        assert new.count(text) == 1
        # Every model tensor is subsequently loaded strictly from released weights.
        new = new.replace(text, 'vgg_t = tviz_models.vgg19(weights=None).features')
    p.write_text(new)
    changes.append({'file':name, 'before_sha256':hashlib.sha256(old.encode()).hexdigest(),
                    'after_sha256':hashlib.sha256(new.encode()).hexdigest()})
Path('/opt/dream_adaptation.json').write_text(json.dumps(changes, indent=2)+'\n')
