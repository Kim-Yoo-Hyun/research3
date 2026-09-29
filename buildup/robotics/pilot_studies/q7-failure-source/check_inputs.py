"""Check the intervention preserves END pixels before any task predictions."""
import hashlib
import json
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor
from vlm import prompt_payload

out=Path('/output/vlm_input_check.json')
assert not out.exists()
cfg=json.loads(Path('/study/vlm_config.json').read_text())
cases=json.loads(Path('/prepared/cases.json').read_text())
processor=AutoProcessor.from_pretrained('/model',local_files_only=True,trust_remote_code=False)
processor.image_processor.size={'longest_edge':cfg['image_longest_edge']}
processor.image_processor.do_image_splitting=False
checks=[]
for case in cases:
    public={k:case[k] for k in ['task','subtask','start','end']}
    tensors={}
    counts={}
    for cond in cfg['conditions']:
        prompt,paths,_=prompt_payload(public,cond,cfg,processor)
        images=[]
        for path in paths:
            with Image.open(Path('/prepared/originals')/path) as im:images.append(im.convert('RGB'))
        inputs=processor(text=prompt,images=images,return_tensors='pt')
        n=3 if cond=='end_only' else 6
        assert inputs['pixel_values'].shape[1]==n
        assert int((inputs['input_ids']==processor.tokenizer.convert_tokens_to_ids(processor.image_token)).sum())==n*81
        tensors[cond]=inputs['pixel_values']
        counts[cond]={'images':n,'input_tokens':inputs['input_ids'].shape[-1],'tensor_shape':list(inputs['pixel_values'].shape)}
    assert torch.equal(tensors['end_only'],tensors['start_end'][:,-3:])
    checks.append({'case':case['id'],'end_pixels_equal':True,'conditions':counts})
out.write_text(json.dumps({'status':'PASS','cases':len(checks),'task_predictions':0,
                          'checks':checks,'config_sha256':hashlib.sha256(Path('/study/vlm_config.json').read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS',len(checks),'cases; identical END tensors across conditions; zero task predictions')
