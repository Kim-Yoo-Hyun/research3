"""Q12 measurement implementation. Import/execute only in the pinned CPU container."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pybullet as pb


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def read_obj(path):
    vertices, faces = [], []
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'v':
            vertices.append([float(x) for x in fields[1:4]])
        elif fields[0] == 'f':
            face = [int(x.split('/')[0]) for x in fields[1:]]
            assert len(face) == 3 and min(face) > 0, 'require original positive triangle indices'
            faces.append([x - 1 for x in face])
    v, f = np.array(vertices, dtype=np.float64), np.array(faces, dtype=np.int64)
    assert v.ndim == 2 and v.shape[1] == 3 and len(v) >= 4 and np.isfinite(v).all()
    assert f.ndim == 2 and f.shape[1] == 3 and len(f) >= 4 and f.min() >= 0 and f.max() < len(v)
    return v, f


def prepare_mesh(v, f, cfg):
    v = np.asarray(v, dtype=np.float64)
    lo, hi = v.min(0), v.max(0)
    scale = cfg['longest_aabb_extent_m'] / float((hi - lo).max())
    assert np.isfinite(scale) and scale > 0
    center = (lo + hi) / 2
    offset = np.asarray(cfg['aabb_center_world_m'])
    world = (v - center) * scale + offset
    tri = world[f]
    areas = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)/2
    # OBJ texture seams may repeat exact vertex coordinates. Weld only exact duplicates for topology.
    unique, inverse = np.unique(v, axis=0, return_inverse=True)
    wf = inverse[f]
    directed = np.concatenate([wf[:, [0, 1]], wf[:, [1, 2]], wf[:, [2, 0]]])
    edges, counts = np.unique(np.sort(directed, axis=1), axis=0, return_counts=True)
    signed = np.where(directed[:, 0] < directed[:, 1], 1, -1)
    _, idx = np.unique(np.sort(directed, axis=1), axis=0, return_inverse=True)
    orientation = np.bincount(idx, weights=signed)
    closed = bool(np.all(counts == 2) and np.all(orientation == 0))
    receipt = {'raw_vertices': len(v), 'exact_unique_vertices': len(unique), 'triangles': len(f),
               'raw_aabb': [lo.tolist(), hi.tolist()], 'raw_center': center.tolist(),
               'synthetic_scale': scale, 'world_offset': offset.tolist(),
               'closed_oriented_edges': closed, 'bad_edge_count': int(np.count_nonzero(counts != 2)),
               'bad_orientation_count': int(np.count_nonzero(orientation)),
               'minimum_triangle_area_m2': float(areas.min()),
               'inverse_max_error': float(np.max(np.abs((world-offset)/scale+center-v)))}
    return world, f, receipt


def camera(cfg, view_index):
    eye = np.array(cfg['eyes_m'][view_index], dtype=np.float64)
    target, up = np.array(cfg['target_m']), np.array(cfg['up'])
    forward = target-eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    down = -np.cross(right, forward)
    rot = np.stack([right, down, forward], axis=1)
    view = pb.computeViewMatrix(eye, target, up)
    proj = pb.computeProjectionMatrixFOV(cfg['fov_y_deg'], cfg['width']/cfg['height'], cfg['near_m'], cfg['far_m'])
    return {'eye': eye, 'rotation': rot, 'view': view, 'projection': proj,
            'focal': cfg['height']/(2*np.tan(np.deg2rad(cfg['fov_y_deg'])/2)),
            'width': cfg['width'], 'height': cfg['height'], 'near': cfg['near_m'], 'far': cfg['far_m']}


def unproject(depth, cam):
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w)+0.5, np.arange(h)+0.5)
    optical = np.stack([(u-w/2)/cam['focal']*depth, (v-h/2)/cam['focal']*depth, depth], axis=-1)
    world = optical @ cam['rotation'].T + cam['eye']
    return optical, world


def render(body, cam):
    args = dict(width=cam['width'], height=cam['height'], viewMatrix=cam['view'],
                projectionMatrix=cam['projection'], renderer=pb.ER_TINY_RENDERER,
                flags=pb.ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX)
    a, b = pb.getCameraImage(**args), pb.getCameraImage(**args)
    depth_buffer, seg = np.asarray(a[3]), np.asarray(a[4])
    same = bool(np.array_equal(depth_buffer, np.asarray(b[3])) and np.array_equal(seg, np.asarray(b[4])))
    z = cam['far']*cam['near']/(cam['far']-(cam['far']-cam['near'])*depth_buffer.astype(np.float64))
    mask = (seg >= 0) & ((seg & ((1 << 24)-1)) == body) & (depth_buffer < 1)
    optical, world = unproject(z, cam)
    return {'depth': z, 'depth_buffer': depth_buffer, 'segmentation': seg, 'mask': mask,
            'repeat_depth_buffer': np.asarray(b[3]), 'repeat_segmentation': np.asarray(b[4]),
            'optical': optical, 'world': world, 'repeat_equal': same}


def mesh_body(v, f):
    args = dict(vertices=v.tolist(), indices=f.reshape(-1).tolist(), meshScale=[1, 1, 1])
    collision = pb.createCollisionShape(pb.GEOM_MESH, flags=pb.GEOM_FORCE_CONCAVE_TRIMESH, **args)
    visual = pb.createVisualShape(pb.GEOM_MESH, rgbaColor=[0.7, 0.7, 0.7, 1], **args)
    body = pb.createMultiBody(baseMass=0, baseCollisionShapeIndex=collision, baseVisualShapeIndex=visual)
    pb.changeDynamics(body, -1, collisionMargin=0)
    return body


def fps(points, count):
    assert len(points) >= count
    distance = np.full(len(points), np.inf)
    selected = np.empty(count, dtype=np.int64)
    current = 0
    for i in range(count):
        selected[i] = current
        distance = np.minimum(distance, np.sum((points-points[current])**2, axis=1))
        current = int(np.argmax(distance))
    assert len(np.unique(selected)) == count
    return points[selected], selected


def surface_points(tri, count, seed):
    areas = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)
    rng = np.random.default_rng(seed)
    ids = rng.choice(len(tri), count, p=areas/areas.sum())
    uv = rng.random((count, 2))
    a = np.sqrt(uv[:, 0])
    weights = np.stack([1-a, a*(1-uv[:, 1]), a*uv[:, 1]], axis=1)
    return (tri[ids]*weights[:, :, None]).sum(1), ids, weights


def candidates(partial_optical, cam, cfg):
    anchor = partial_optical.mean(0)
    rows = []
    for width, roll, dz, dx in itertools.product(cfg['widths_m'], cfg['rolls_deg'], cfg['z_offsets_m'], cfg['x_offsets_m']):
        angle = np.deg2rad(roll)
        r = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        rotation = cam['rotation'] @ r
        center = cam['eye'] + cam['rotation'] @ (anchor + np.array([dx, 0, dz]))
        half = cfg['finger_half_extents_m']
        local_boxes = [([-width/2-half[0], 0, 0], half), ([width/2+half[0], 0, 0], half),
                       ([0, 0, cfg['palm_center_z_m']], [width/2+2*half[0], half[1], cfg['palm_half_depth_m']])]
        boxes = [{'center': (center+rotation@np.array(c)).tolist(), 'half': h} for c, h in local_boxes]
        rows.append({'id': len(rows), 'width_m': width, 'roll_deg': roll, 'x_offset_m': dx, 'z_offset_m': dz,
                     'utility_cost': dx*dx+dz*dz, 'rotation': rotation.tolist(), 'center': center.tolist(), 'boxes': boxes})
    assert len(rows) == cfg['candidate_count']
    return rows


def solid_angle_inside(point, tri):
    a, b, c = (tri-point).transpose(1, 0, 2)
    na, nb, nc = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(c, axis=1)
    top = np.einsum('ij,ij->i', a, np.cross(b, c))
    bottom = na*nb*nc + np.einsum('ij,ij->i', a, b)*nc + np.einsum('ij,ij->i', b, c)*na + np.einsum('ij,ij->i', c, a)*nb
    winding = abs(float(np.sum(2*np.arctan2(top, bottom))/(4*np.pi)))
    return winding > 0.5, winding


def point_collision(points, candidate, tolerance):
    r = np.asarray(candidate['rotation'])
    for box in candidate['boxes']:
        local = (points-box['center']) @ r
        if np.any(np.all(np.abs(local) <= np.array(box['half'])+tolerance, axis=1)):
            return True
    return False


def physics_labels(body, tri, rows, tolerance):
    result = []
    for c in rows:
        # Quaternion from orthonormal columns, using camera-facing gripper basis.
        r = np.asarray(c['rotation'])
        # Matrix-to-quaternion via the symmetric eigenproblem avoids trace singularities.
        k = np.array([[r[0,0]-r[1,1]-r[2,2], r[1,0]+r[0,1], r[2,0]+r[0,2], r[2,1]-r[1,2]],
                      [r[1,0]+r[0,1], r[1,1]-r[0,0]-r[2,2], r[2,1]+r[1,2], r[0,2]-r[2,0]],
                      [r[2,0]+r[0,2], r[2,1]+r[1,2], r[2,2]-r[0,0]-r[1,1], r[1,0]-r[0,1]],
                      [r[2,1]-r[1,2], r[0,2]-r[2,0], r[1,0]-r[0,1], np.trace(r)]])/3
        _, vecs = np.linalg.eigh(k)
        quat = vecs[:, -1]
        boxes = []
        for box in c['boxes']:
            shape = pb.createCollisionShape(pb.GEOM_BOX, halfExtents=box['half'])
            bid = pb.createMultiBody(baseMass=0, baseCollisionShapeIndex=shape, basePosition=box['center'], baseOrientation=quat)
            pb.changeDynamics(bid, -1, collisionMargin=0)
            contacts = pb.getClosestPoints(body, bid, distance=0.02)
            distance = min((x[8] for x in contacts), default=None)
            inside, winding = solid_angle_inside(np.array(box['center']), tri)
            boxes.append({'distance_m': distance, 'distance_lower_bound_if_missing_m': 0.02,
                          'center_inside': inside, 'absolute_winding': winding})
            pb.removeBody(bid)
        collides = any(x['center_inside'] or (x['distance_m'] is not None and x['distance_m'] <= 0) for x in boxes)
        # Near-contact candidates are retained and flagged; no adaptive thresholding.
        ambiguous = any(x['distance_m'] is not None and abs(x['distance_m']) <= tolerance for x in boxes)
        result.append({'id': c['id'], 'collision': collides, 'near_contact': ambiguous, 'boxes': boxes})
    return result


def run_case(v, f, cfg, view_index, out, seed):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    pb.resetSimulation()
    body = mesh_body(v, f)
    cam = camera(cfg['camera'], view_index)
    observation = render(body, cam)
    points = observation['optical'][observation['mask']]
    assert len(points) >= cfg['sampling']['partial_count'], 'insufficient rendered pixels'
    sampled, indices = fps(points, cfg['sampling']['partial_count'])
    mean = sampled.mean(0)
    radius = float(np.linalg.norm(sampled-mean, axis=1).max())
    normalized = (sampled-mean)/radius
    rows = candidates(points, cam, cfg['gripper'])
    # Candidate manifest is saved before any full-geometry labels or oracle samples.
    save_json(out/'candidates.json', rows)
    tri = v[f]
    labels = physics_labels(body, tri, rows, cfg['tolerances']['near_contact_m'])
    oracle, triangle_ids, weights = surface_points(tri, cfg['sampling']['oracle_dense_count'], seed)
    for c, label in zip(rows, labels):
        label['oracle_8192_collision'] = point_collision(oracle[:cfg['sampling']['oracle_surface_count']], c, cfg['tolerances']['point_in_box_m'])
        label['oracle_32768_collision'] = point_collision(oracle, c, cfg['tolerances']['point_in_box_m'])
    serial_cam = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in cam.items()}
    receipt = {'view_index': view_index, 'object_body_id': body, 'camera': serial_cam, 'valid_pixels': len(points),
               'sampled_points': len(sampled), 'repeat_equal': observation['repeat_equal'],
               'normalization': {'mean': mean.tolist(), 'radius': radius,
                                 'inverse_max_error_m': float(np.abs(normalized*radius+mean-sampled).max())},
               'seed': seed, 'candidate_sha256': digest(out/'candidates.json'), 'labels': labels}
    np.savez_compressed(out/'observation.npz', depth=observation['depth'], depth_buffer=observation['depth_buffer'],
                        repeat_depth_buffer=observation['repeat_depth_buffer'], repeat_segmentation=observation['repeat_segmentation'],
                        mask=observation['mask'], segmentation=observation['segmentation'],
                        partial_optical=sampled, sampled_indices=indices, normalized=normalized)
    np.savez_compressed(out/'geometry.npz', vertices=v, faces=f, oracle_points=oracle,
                        triangle_ids=triangle_ids, barycentric=weights)
    save_json(out/'result.json', receipt)
    return receipt
