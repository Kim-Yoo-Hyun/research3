"""Codec-path accounting; no reconstructed action is executed in the simulator."""
import contextlib
import io
import json
from pathlib import Path
import numpy as np
from scipy.fft import dct, idct
from transformers import AutoProcessor
P = json.loads(Path('/work/protocol.json').read_text())
O = Path('/outputs')


def maxerr(a,b): return float(np.max(np.abs(a-b)))


def main():
    proc = AutoProcessor.from_pretrained('/inputs/fast', trust_remote_code=True, local_files_only=True)
    data = {}
    for seed in P['seeds']:
        p = O/f'seed_{seed}'/'generation.npz'
        if p.exists():
            a = np.load(p)['actions']
            if len(a): data[seed] = a.astype(np.float64)
    calibration = [a for s,a in data.items() if s in P['calibration_seeds']]
    if not calibration:
        (O/'codec.json').write_text(json.dumps({'status':'NO_CALIBRATION_INPUTS','rows':[]}))
        return
    cal = np.concatenate(calibration)
    lo,hi = np.quantile(cal, P['quantiles'], axis=0)
    center=(lo+hi)/2
    constant=(hi-lo)<P['constant_channel_epsilon']
    width=(hi-lo)/2
    width[constant]=P['constant_channel_scale']
    stats={'calibration_seeds':P['calibration_seeds'],'center':center.tolist(),
           'half_range':width.tolist(),'constant_channels':constant.tolist()}
    rows=[]
    for seed,a in data.items():
        schema=json.loads((O/f'seed_{seed}'/'generation.json').read_text()).get('schema')
        if schema is None:
            rows.append({'seed':seed,'status':'NO_CONTROLLER_SCHEMA'});continue
        for normalization in P['normalizations']:
            if normalization=='joint_limits':
                low=np.array(schema['action_low']);high=np.array(schema['action_high'])
                c=(low+high)/2;w=(high-low)/2
            else: c=center;w=width
            assert np.isfinite(w).all() and (w>0).all()
            normalized=(a-c)/w
            identity=maxerr(normalized*w+c,a)
            chunks=[];lengths=[]
            for t in range(0,len(a),P['chunk_length']):
                part=normalized[t:t+P['chunk_length']];lengths.append(len(part))
                chunks.append(np.pad(part,((0,P['chunk_length']-len(part)),(0,0)),mode='edge'))
            chunks=np.stack(chunks)
            coeff=dct(chunks,axis=1,norm='ortho')
            quant=np.around(coeff*proc.scale)
            clamped=np.maximum(quant,proc.min_token)
            tokens=proc(chunks)
            back=[];bpe_valid=[]
            for ids,expected in zip(tokens,clamped):
                z=np.array([ord(x) for x in proc.bpe_tokenizer.decode(ids)])+proc.min_token
                bpe_valid.append(bool(z.size==expected.size and np.array_equal(z.reshape(expected.shape),expected)))
                back.append(z.tolist())
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture):
                decoded=proc.decode(tokens,time_horizon=P['chunk_length'],action_dim=8)
            analytic=idct(quant/proc.scale,axis=1,norm='ortho')
            expected=idct(clamped/proc.scale,axis=1,norm='ortho')
            identity_dct=maxerr(idct(coeff,axis=1,norm='ortho'),chunks)
            row={'seed':seed,'normalization':normalization,'status':'completed',
                 'steps':len(a),'chunks':len(chunks),'valid_lengths':lengths,
                 'normalization_identity_error':identity,'dct_identity_error':identity_dct,
                 'clamped_coefficients':int((quant<proc.min_token).sum()),
                 'bpe_equal_all':all(bpe_valid),'bpe_equal':bpe_valid,
                 'decode_messages':capture.getvalue(),'decode_finite':bool(np.isfinite(decoded).all()),
                 'official_vs_clamped_error':maxerr(decoded,expected),
                 'official_vs_quantized_error':maxerr(decoded,analytic),
                 'outside_normalized_range':int((np.abs(normalized)>1).sum()),
                 'tokens_per_chunk':[len(x) for x in tokens],
                 'token_json_bytes':len(json.dumps(tokens,separators=(',',':')).encode()),
                 'normalized_mse_valid':float(np.mean((np.concatenate([d[:n] for d,n in zip(decoded,lengths)])-normalized)**2))}
            stem=f'codec_{seed}_{normalization}'
            np.savez_compressed(O/(stem+'.npz'), normalized=chunks, coefficients=coeff,
                                quantized=quant, clamped=clamped, decoded=decoded,
                                center=c,half_range=w,valid_lengths=np.array(lengths))
            (O/(stem+'.json')).write_text(json.dumps({'tokens':tokens,'decoded_coefficients':back}))
            rows.append(row)
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture): invalid=proc.decode([[]],time_horizon=P['chunk_length'],action_dim=8)
    out={'status':'completed','calibration':stats,'scale':proc.scale,'min_token':proc.min_token,
         'vocabulary_size':len(proc.bpe_tokenizer),'synthetic_invalid_decode':{
             'input':'empty token sequence','zero_fallback':bool(np.all(invalid==0)),
             'messages':capture.getvalue(),'not_a_natural_failure':True},'rows':rows}
    (O/'codec.json').write_text(json.dumps(out,indent=2))
    print('codec rows',len(rows),flush=True)


if __name__=='__main__':main()
