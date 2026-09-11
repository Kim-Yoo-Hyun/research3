"""Post-run byte audit in Docker; no model, NumPy, Torch, checkpoint, or GT import."""
import ast
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arrays(path):
    result = {}
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist()) == 6
        for name in archive.namelist():
            data = archive.read(name)  # includes ZIP CRC verification
            assert data[:6] == b'\x93NUMPY' and data[6:8] == b'\x01\x00'
            offset = 10 + struct.unpack('<H', data[8:10])[0]
            header = ast.literal_eval(data[10:offset].decode('latin1'))
            assert header['fortran_order'] is False
            size = {'<f4':4, '<f8':8, '<i4':4}[header['descr']]
            body = data[offset:]
            assert len(body) == math.prod(header['shape']) * size
            result[name] = (header, body)
    assert set(result) == {'dense.npy','sparse.npy','input.npy','centroid.npy','radius.npy','sparse_input_indices.npy'}
    return result


def main():
    root = Path('/result')
    verification = json.loads((root/'verification/verification.json').read_text())
    assert verification['decision'] == 'REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED'
    rows = []
    for index in range(4):
        paths = [root/'predictions'/str(repeat)/f'{index}.npz' for repeat in range(2)]
        first, second = [arrays(path) for path in paths]
        assert first == second, 'NPY headers or bytes differ between processes'
        for array in [first, second]:
            for name, shape in [('dense.npy',(8192,3)),('sparse.npy',(192,3)),('input.npy',(2048,3))]:
                assert array[name][0]['shape'] == shape and array[name][0]['descr'] == '<f4'
            assert array['dense.npy'][1][6144*12:] == array['input.npy'][1]
            indices = struct.unpack('<96i', array['sparse_input_indices.npy'][1])
            assert all(0 <= i < 2048 for i in indices)
            copied = b''.join(array['input.npy'][1][i*12:(i+1)*12] for i in indices)
            assert array['sparse.npy'][1][96*12:] == copied
        rows.append(dict(index=index, repeat_npy_bytes_equal=True, dense_copy_bytes_equal=True,
                         sparse_copy_bytes_equal=True, archive_sha256=[sha(p) for p in paths]))
    receipt = dict(status='PASS_OUTPUT_BYTE_AUDIT', pairs=rows, archive_count=8, npy_member_count=48,
                   verification_sha256=sha(root/'verification/verification.json'),
                   new_model_forwards=0, audit_scope='post-run verification of literal bit equality, including signed zero; no new metric')
    output = Path('/audit/audit.json')
    assert not output.exists()
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'], archive_count=8, npy_member_count=48)))


if __name__ == '__main__':
    main()
