"""Remove only this continuation's verified, exited Docker containers."""
import datetime
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT/'runs/q16/dp_reference'
COMMIT = '5ba07ac6661db573af695b419a7947ecb704690f'
SOURCE = ROOT/'external/q16'/f'diffusion_policy-{COMMIT}'
CHECKPOINT = OUT/'checkpoint/epoch=0550-test_mean_score=0.969.ckpt'


def main():
    removed=[]
    for record in sorted((OUT/'jobs').glob('*.json')):
        job=json.loads(record.read_text())
        if job.get('stage') not in ('inspect','parity','evaluate','verify','branch','branchverify',
                                   'lock','obsaudit','obsresolve','traincontract','finetune',
                                   'compare','compareverify') or job.get('status') not in ('completed','failed'):
            continue
        inspected=subprocess.run(['docker','inspect',job['container']],capture_output=True,text=True)
        if inspected.returncode!=0:
            continue
        info=json.loads(inspected.stdout)[0]
        mounts={m['Destination']:m['Source'] for m in info['Mounts']}
        checks=[not info['State']['Running'],info['State']['Status']=='exited',
                info['Name']=='/'+job['container'], info['Id']==job['inspection']['Id'],
                info['Image']==job['image_id'],
                info['Config']['Labels'].get('research3.workspace')==str(ROOT),
                info['Config']['Labels'].get('research3.study')=='q16-dp-reference',
                mounts.get('/study')==job['source_snapshot'],
                mounts.get('/source')==str(SOURCE),
                mounts.get('/checkpoint/model.ckpt')==str(CHECKPOINT),
                mounts.get('/previous')==str(ROOT/'runs/q16/pusht_repeat'),
                mounts.get('/output')==str(OUT),
                Path(job['log']).exists(),Path(job['exit']).exists()]
        if not all(checks):
            raise RuntimeError(f'Ownership or preservation mismatch: {job["container"]}: {checks}')
        subprocess.run(['docker','rm',info['Id']],check=True,capture_output=True)
        removed.append(dict(id=info['Id'],name=job['container'],job=str(record)))
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path=ROOT/'logs'/f'{stamp}_q16_dp_reference_cleanup.log'
    path.write_text(json.dumps(dict(removed=removed),indent=2)+'\n')
    print(json.dumps(dict(count=len(removed),log=str(path)),indent=2))


if __name__=='__main__':
    main()
