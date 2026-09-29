"""Host-allowed archive layout, deterministic member selection and byte manifests."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path('/home/yoohyun/research3/datasets/q14/dream')
out = root/'selected'
assert not out.exists(), 'Do not overwrite selected inputs'
out.mkdir()
with zipfile.ZipFile(root/'panda-3cam_realsense.archive') as z:
    names = z.namelist()
    images = sorted(n for n in names if n.endswith('.rgb.jpg'))
    indices = [k*(len(images)-1)//23 for k in range(24)] if len(images)>=24 else list(range(len(images)))
    rows=[]; files=[]
    targets=['panda-3cam_realsense/_camera_settings.json']
    for i in indices:
        image=images[i]; anno=image.replace('.rgb.jpg','.json')
        rows.append({'id':Path(image).name.split('.')[0],'ordinal':i,'image':Path(image).name,
                     'annotation':Path(anno).name,'annotation_present':anno in names})
        targets.append(image)
        if anno in names:targets.append(anno)
    for name in targets:
        data=z.read(name)  # verifies ZIP-member CRC
        p=out/Path(name).name;p.write_bytes(data)
        files.append({'name':p.name,'archive_member':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest={'selection':'floor(k*(N-1)/23), k=0..23, before inference','rgb_population':len(images),
          'archive_sha256':hashlib.sha256((root/'panda-3cam_realsense.archive').read_bytes()).hexdigest(),
          'samples':rows,'files':files}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'population':len(images),'selected':len(rows),'files':len(files),'ids':[r['id'] for r in rows]}))
