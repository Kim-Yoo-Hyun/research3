"""Map replay state-vector indices to source-matched Can simulator joints."""
import json
from pathlib import Path

import h5py
import mujoco

from can_replay import DATA, make_env, restore


OUTPUT = Path('/output/state_map.json')
TARGETS = (28, 49, 50, 55, 56, 60, 61, 62, 63, 64, 68, 69)


def main():
    with h5py.File(DATA, 'r') as data:
        env = make_env(json.loads(data['data'].attrs['env_args']))
        try:
            restore(env, data['data']['demo_0'])
            model = env.sim.model._model
            entries = []
            for joint in range(model.njnt):
                kind = model.jnt_type[joint]
                qpos_width = 7 if kind == mujoco.mjtJoint.mjJNT_FREE else 4 if kind == mujoco.mjtJoint.mjJNT_BALL else 1
                qvel_width = 6 if kind == mujoco.mjtJoint.mjJNT_FREE else 3 if kind == mujoco.mjtJoint.mjJNT_BALL else 1
                name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint)
                entries.append({'name': name, 'qpos_indices': list(range(1+int(model.jnt_qposadr[joint]), 1+int(model.jnt_qposadr[joint])+qpos_width)),
                                'qvel_indices': list(range(1+model.nq+int(model.jnt_dofadr[joint]), 1+model.nq+int(model.jnt_dofadr[joint])+qvel_width))})
            result = {'nq': int(model.nq), 'nv': int(model.nv), 'targets': {
                str(index): [entry['name'] for entry in entries if index in entry['qpos_indices'] or index in entry['qvel_indices']]
                for index in TARGETS}, 'joints': entries}
            OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps({'nq': result['nq'], 'nv': result['nv'], 'targets': result['targets']}, indent=2))
        finally:
            env.close()


if __name__ == '__main__':
    main()
