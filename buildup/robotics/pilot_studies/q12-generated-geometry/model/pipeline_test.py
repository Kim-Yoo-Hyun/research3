"""Synthetic end-to-end CLI test and semantic output-tampering rejection, in Docker."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
import torch
from reference import construct


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    base = Path(__file__).parent
    torch.set_num_threads(4)
    torch.manual_seed(12022)
    with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
        root = Path(tmp)
        for name in ['config','inputs','gt','predictions']:
            (root/name).mkdir()
        protocol = json.loads((base/'completion_protocol.json').read_text())
        model, _ = construct(protocol['model_config'])
        checkpoint = root/'synthetic.pth'
        torch.save({'base_model':model.state_dict()},checkpoint)
        del model
        protocol['checkpoint_sha256'] = sha(checkpoint)
        rng = np.random.RandomState(12022)
        pairs = []
        for idx in range(4):
            points = rng.normal(size=(2048,3))
            file = f'{idx}.xyz'
            np.savetxt(root/'inputs'/file,points,fmt='%.17g')
            np.savetxt(root/'gt'/file,np.tile(points,(4,1)),fmt='%.17g')
            pairs.append(dict(index=idx,sampled_file=file,sampled_sha256=sha(root/'inputs'/file),
                              gt_file=file,gt_sha256=sha(root/'gt'/file)))
        write(root/'config/completion_protocol.json',protocol)
        write(root/'config/completion_inputs.json',dict(pairs=pairs))
        write(root/'config/completion_freeze.json',dict(synthetic=True,files={
            name:sha(root/'config'/name) for name in ['completion_protocol.json','completion_inputs.json']}))
        for repeat in range(2):
            subprocess.run([sys.executable,str(base/'predict.py'),'--repeat',str(repeat),
                            '--base',str(root/'config'),'--checkpoint',str(checkpoint),
                            '--inputs',str(root/'inputs'),'--output',str(root/'predictions')],
                           check=True,stdout=subprocess.PIPE,timeout=90)
        def verify(name):
            subprocess.run([sys.executable,str(base/'verify_completion.py'),'--base',str(root/'config'),
                            '--inputs',str(root/'inputs'),'--gt',str(root/'gt'),
                            '--predictions',str(root/'predictions'),'--output',str(root/name)],
                           check=True,stdout=subprocess.PIPE,timeout=60)
            return json.loads((root/name).read_text())
        passed = verify('valid.json')
        assert passed['decision'] == 'REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED'
        assert all(r['gt_unique_points']==2048 for r in passed['pairs'])
        # Change a copied coordinate in both repeats and refresh hashes: only a
        # semantic verifier can catch this, not checksum or repeat-equality checks.
        for repeat in range(2):
            path = root/'predictions'/str(repeat)/'0.npz'
            with np.load(path,allow_pickle=False) as z:
                arrays = {k:z[k] for k in z.files}
            arrays['dense'][6144,0] += 0.25
            np.savez(path,**arrays)
            receipt = root/'predictions'/str(repeat)/'result.json'
            value = json.loads(receipt.read_text())
            value['pairs'][0]['sha256'] = sha(path)
            write(receipt,value)
        rejected = verify('tampered.json')
        assert rejected['decision'] == 'REFINE_REFERENCE_OUTPUT'
        assert [r['status'] for r in rejected['pairs']] == ['fail','pass','pass','pass']
    result = dict(status='PASS_SYNTHETIC_PIPELINE', synthetic_model_forwards=8,
                  production_predict_and_verify_cli=True, independent_process_repeat=True,
                  refreshed_hash_copied_suffix_tampering_rejected=True,
                  four_case_denominator_preserved=True, real_checkpoint_or_xyz_mounted=False)
    (Path('/output')/'pipeline_test.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
