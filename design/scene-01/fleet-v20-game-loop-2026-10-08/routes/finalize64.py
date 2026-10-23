from pathlib import Path
import numpy as np,json
P=Path(__file__).resolve().parent
old=np.load(P/'motion.npy');N0=len(old)-1;N=1536
if N0!=2304:raise RuntimeError('Expected frozen 96s source')
np.save(P/'motion96.npy',old)
t=np.arange(N+1)/N;out=np.empty((N+1,8,4));base=np.empty_like(out)
for i in range(4):
 speed=float(np.linalg.norm(np.diff(old[:,i*2,:2],axis=0),axis=1).sum())/96
 warp=(1.75/speed/96*np.sin(2*np.pi*4*t)*(1 if i==0 else -1)) if i in(0,3) else np.zeros_like(t)
 sample=t+warp;cycles=np.floor(sample);phase=sample%1
 for k in range(i*2,i*2+2):
  for j in range(4):
   base[:,k,j]=np.interp(t*N0,np.arange(N0+1),old[:,k,j])
   out[:,k,j]=np.interp(phase*N0,np.arange(N0+1),old[:,k,j])
   if j==3:out[:,k,j]+=cycles*(old[-1,k,j]-old[0,k,j])
out[-1]=out[0];out[-1,:,3]+=4*np.pi
speeds=np.linalg.norm(np.diff(out[:,::2,:2],axis=0),axis=2)*24
report=dict(frames=N,seconds=64,laps=[2]*4,modulation='opposite-phase 4-cycle periodic red/yellow pace warp',max_position_deviation=np.linalg.norm(out[:,:,:2]-base[:,:,:2],axis=2).max(axis=0).tolist(),speed_min=speeds.min(axis=0).tolist(),speed_max=speeds.max(axis=0).tolist(),speed_mean=speeds.mean(axis=0).tolist(),loop_position_error=float(np.abs(out[0,:,:2]-out[-1,:,:2]).max()))
assert max(report['max_position_deviation'])<=2
np.save(P/'motion.npy',out);(P/'final64-report.json').write_text(json.dumps(report,indent=2));print(report)
