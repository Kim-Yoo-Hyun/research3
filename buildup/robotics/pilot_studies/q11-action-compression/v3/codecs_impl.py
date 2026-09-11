"""Native byte-counted codecs. Shared model/statistics are accounted separately."""
import struct
import numpy as np
from scipy.fft import dct
HEADER=struct.Struct('<4sBBBBHH')
H=20


def pack(values,bits):
    out=bytearray();acc=0;used=0
    for value in np.asarray(values).reshape(-1):
        value=int(value)
        if not 0<=value<(1<<bits):raise ValueError('integer outside wire representation')
        acc|=value<<used;used+=bits
        while used>=8:out.append(acc&255);acc>>=8;used-=8
    if used:out.append(acc)
    return bytes(out)


def unpack(raw,bits,count):
    result=[];acc=0;used=0;i=0
    for _ in range(count):
        while used<bits:acc|=raw[i]<<used;used+=8;i+=1
        result.append(acc&((1<<bits)-1));acc>>=bits;used-=bits
    return np.array(result,dtype=np.int64)


def packet(chunk,valid,kind,param,proc):
    # All variants except FAST full have an exact binary gripper side channel.
    bypass=kind not in ('fast_joint','fast_quantile')
    dim=7 if bypass else 8
    values=chunk[:,:dim]
    side=b''
    if bypass:
        assert np.isin(chunk[:,7],[-1.,1.]).all()
        side=pack((chunk[:,7]>0).astype(int),1)
    if kind.startswith('fast'):
        ids=proc(values)[0]
        quant=np.rint(dct(values,axis=0,norm='ortho')*proc.scale)
        returned=np.array([ord(x) for x in proc.bpe_tokenizer.decode(ids)])+proc.min_token
        if returned.size!=quant.size or not np.array_equal(returned.reshape(quant.shape),quant):
            raise ValueError('FAST coefficient clamp or BPE mismatch')
        bits=(len(proc.bpe_tokenizer)-1).bit_length()
        return HEADER.pack(b'Q11P',0,dim,bits,valid,0,len(ids))+pack(ids,bits)+side
    bits=int(param['bits']);k=H if kind=='uniform_gripper' else int(param['knots'])
    indices=np.rint(np.linspace(0,H-1,k)).astype(int)
    samples=values[indices].reshape(-1)
    escape=(samples < -1)|(samples > 1)
    # Bounded quantization plus lossless escapes, so normalization tails are not clipped away.
    q=np.rint((np.clip(samples,-1,1)+1)*((1<<bits)-1)/2).astype(int)
    flags=bits|(128 if escape.any() else 0)
    body=pack(q,bits)
    if escape.any():body+=pack(escape.astype(int),1)+samples[escape].astype('<f8').tobytes()
    return HEADER.pack(b'Q11P',1 if kind=='uniform_gripper' else 2,dim,flags,valid,k,len(q))+body+side


def depacket(blob,proc):
    magic,code,dim,flags,valid,k,count=HEADER.unpack(blob[:HEADER.size])
    assert magic==b'Q11P' and 1<=valid<=H and dim in [7,8]
    bits=flags&127;size=(count*bits+7)//8;offset=HEADER.size
    ints=unpack(blob[offset:offset+size],bits,count);offset+=size
    if code==0:
        values=proc.decode([ints.tolist()],time_horizon=H,action_dim=dim)[0]
    else:
        samples=ints.astype(float)*2/((1<<bits)-1)-1
        if flags&128:
            size=(count+7)//8
            mask=unpack(blob[offset:offset+size],1,count).astype(bool);offset+=size
            n=int(mask.sum());samples[mask]=np.frombuffer(blob[offset:offset+8*n],dtype='<f8');offset+=8*n
        knots=samples.reshape(k,dim)
        indices=np.rint(np.linspace(0,H-1,k)).astype(int)
        values=np.stack([np.interp(np.arange(H),indices,knots[:,i]) for i in range(dim)],axis=1)
    if dim==7:
        size=(H+7)//8
        grip=unpack(blob[offset:offset+size],1,H)*2.-1.;offset+=size
        values=np.column_stack([values,grip])
    assert offset==len(blob) and np.isfinite(values).all()
    return values,valid


def encode_episode(actions,kind,param,stats,proc):
    c=np.array(stats['center']);w=np.array(stats['half_range'])
    normalized=(actions-c)/w
    bypass=kind not in ('fast_joint','fast_quantile')
    if bypass:normalized[:,7]=actions[:,7]
    blobs=[];decoded=[]
    for start in range(0,len(actions),H):
        block=normalized[start:start+H];n=len(block)
        padded=np.pad(block,((0,H-n),(0,0)),mode='edge')
        blob=packet(padded,n,kind,param,proc);back,valid=depacket(blob,proc)
        a=back[:valid]*w+c
        if bypass:a[:,7]=back[:valid,7]
        blobs.append(blob);decoded.append(a)
    return np.concatenate(decoded),blobs


def join_packets(blobs):
    # Packet lengths are derivable from each header except escapes; explicit offsets counted.
    return struct.pack('<I',len(blobs))+b''.join(struct.pack('<I',len(b))+b for b in blobs)


def read_packets(raw):
    count=struct.unpack_from('<I',raw)[0];offset=4;blobs=[]
    for _ in range(count):
        n=struct.unpack_from('<I',raw,offset)[0];offset+=4;blobs.append(raw[offset:offset+n]);offset+=n
    assert offset==len(raw)
    return blobs
