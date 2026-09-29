"""Host-only Docker orchestration; called in tmux with a timestamped log."""
import argparse
from pathlib import Path
import json
import shutil
import subprocess
import os

root=Path('/home/yoohyun/research3')
study=root/'buildup/robotics/pilot_studies/q14-frame-errors/real'
p=argparse.ArgumentParser();p.add_argument('phase',choices=['build','observe','verify','analyze','correct']);p.add_argument('run_id');a=p.parse_args()
run=root/'runs/q14'/a.run_id
run.mkdir(parents=True,exist_ok=True)
def call(cmd):
    with (run/'commands.jsonl').open('a') as f:f.write(json.dumps({'phase':a.phase,'cwd':str(root),'argv':cmd})+'\n')
    subprocess.run(cmd,cwd=root,check=True)
if a.phase=='build':
    context=run/'build_context';context.mkdir()
    for name in ['Dockerfile','requirements.lock','adapt.py']:shutil.copy2(study/name,context/name)
    shutil.copytree(root/'external/q14-dream',context/'upstream')
    call(['docker','build','--pull','--no-cache','--iidfile',str(run/'image.id'),'-t','research3-q14-real-keypoints:v1',str(context)])
else:
    source=run/(a.phase+'_source');shutil.copytree(study,source)
    output=run/a.phase;output.mkdir()
    name=f'research3-q14-real-{a.phase}-{a.run_id}'
    cmd=['docker','run','--name',name,'--cidfile',str(run/(a.phase+'.cid')),
         '--label','research3.workspace='+str(root),'--label','research3.study=q14-real-keypoints',
         '--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
         '--cpus','4','--memory','6g','--pids-limit','256','--user',f'{os.getuid()}:{os.getgid()}',
         '--tmpfs','/tmp:rw,nosuid,size=256m','--mount',f'type=bind,src={source},dst=/study,readonly',
         '--mount',f'type=bind,src={root}/datasets/q14/dream,dst=/input,readonly',
         '--mount',f'type=bind,src={output},dst=/output']
    if a.phase in ['verify','analyze','correct']:cmd+=['--mount',f'type=bind,src={run}/observe,dst=/result,readonly']
    cmd += [(run/'image.id').read_text().strip(),'/study/'+a.phase+'.py']
    try:call(['timeout','3600s']+cmd)
    finally:
        if (run/(a.phase+'.cid')).exists():
            cid=(run/(a.phase+'.cid')).read_text().strip()
            result=subprocess.run(['docker','inspect',cid],capture_output=True,text=True)
            (run/(a.phase+'.inspect.json')).write_text(result.stdout)
            result=subprocess.run(['docker','logs',cid],capture_output=True,text=True)
            (run/(a.phase+'.container.log')).write_text(result.stdout+result.stderr)
