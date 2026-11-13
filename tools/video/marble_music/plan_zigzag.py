"""Zig-zag marble planner: angled paddles alternate LEFT/RIGHT; marble hits paddle i exactly on note i's frame.
Between hits: ballistic parabola (gravity g, constant vx). Paddle normal bisects reversed-incoming and outgoing directions.
usage: python plan_zigzag.py hits.json --fps 30 -o plan.json"""
import json, argparse, math
import numpy as np
ap=argparse.ArgumentParser(); ap.add_argument('hits'); ap.add_argument('--fps',type=int,default=30)
ap.add_argument('--g',type=float,default=30.0); ap.add_argument('--half-gap',type=float,default=0.6,help='marble-centre x at contact = +-this')
ap.add_argument('--drop-rate',type=float,default=5.0,help='max mean descent per second (long gaps become lobs)')
ap.add_argument('--min-drop',type=float,default=0.35); ap.add_argument('--frac',type=float,default=0.5,help='drop as fraction of free-fall drop (lower = higher hop, flatter paddles)'); ap.add_argument('--snap',type=int,default=1,help='snap hit times to frame grid')
ap.add_argument('-o',default='plan.json'); ap.add_argument('--verbose',type=int,default=0); ap.add_argument('--frame-margin',type=float,default=1.4); a=ap.parse_args()
H=json.load(open(a.hits)); hits=H['hits']; dur=H['end']-H['start']; fps=a.fps; g=a.g; X=a.half_gap
R=0.15; PL,KD,PT=0.62,0.36,0.09          # paddle length, depth (into wall), thickness
T=[(round(h['time']*fps)/fps if a.snap else h['time']) for h in hits]
n=len(T)
side=[(-1 if i%2==0 else 1) for i in range(n)]           # first paddle on the left
xs=[side[i]*X for i in range(n)]
def drop_for(dt): return max(a.min_drop, min(a.frac*0.5*g*dt*dt, a.drop_rate*dt))
# pre-roll: marble enters from the opposite side 0.5s before first hit
pre_dt=0.5
def dist_rect_xy(p,c,nn):
    d=np.array(p)-c; tt=np.array([nn[1],-nn[0]])
    u,v=abs(d@tt)-PL/2, abs(d@nn)-PT/2
    return math.hypot(max(u,0),max(v,0))+min(max(u,v),0)
def seg_hits(seg,paddles,skip_first):
    t0,x0,z0,vx,vz,dt=seg
    for u in np.linspace(0,dt,int(dt*fps*8)+2):
        if skip_first and u<1.2/fps: continue
        if dt-u<1.2/fps: continue
        p=(x0+vx*u, z0+vz*u-0.5*g*u*u)
        for j,(c,nn) in enumerate(paddles):
            if dist_rect_xy(p,c,nn)<R*1.05: return True
    return False
def normal(vin,vout):
    nrm=vout/np.linalg.norm(vout)-vin/np.linalg.norm(vin); return nrm/np.linalg.norm(nrm)
# entry segment from opposite side
pre_dt=0.5; d0=max(a.min_drop,a.frac*0.5*g*pre_dt**2)
entry=(T[0]-pre_dt,-xs[0],d0,(xs[0]+xs[0])/pre_dt*1.0,0,pre_dt)
entry=(T[0]-pre_dt,-xs[0],d0,(2*xs[0])/pre_dt,(-d0+0.5*g*pre_dt**2)/pre_dt,pre_dt)
allsegs=[entry]; zs=[0.0]; paddles=[]; warn=0
def vel_end(s): return np.array([s[3], s[4]-g*s[5]])
for i in range(n):
    if i==n-1: dt=0.4; xn=-xs[i]
    else: dt=T[i+1]-T[i]; xn=xs[i+1]
    vx=(xn-xs[i])/dt; vin=vel_end(allsegs[-1])
    nat=max(a.min_drop, min(a.frac*0.5*g*dt*dt, a.drop_rate*dt))
    chosen=None
    for d in list(np.arange(nat, nat+40, 0.1)):
        vz=(-d+0.5*g*dt*dt)/dt; seg=(T[i],xs[i],zs[i],vx,vz,dt)
        nn=normal(vin,np.array([vx,vz])); c=np.array([xs[i],zs[i]])-nn*(R+PT/2)
        if i==n-1 or not seg_hits(seg,paddles+[(c,nn)],True): chosen=(d,seg,c,nn); break
    if chosen is None: warn+=1; d=nat; vz=(-d+0.5*g*dt*dt)/dt; seg=(T[i],xs[i],zs[i],vx,vz,dt); nn=normal(vin,np.array([vx,vz])); c=np.array([xs[i],zs[i]])-nn*(R+PT/2); chosen=(d,seg,c,nn); print('WARN key',i)
    d,seg,c,nn=chosen; paddles.append((c,nn))
    if i==n-1: seg=seg[:5]+(1e9,)
    allsegs.append(seg); zs.append(zs[-1]-d)
keys=[]
for i in range(n):
    c,nrm=paddles[i]; tilt=math.degrees(math.acos(max(-1,min(1,nrm[1]))))
    keys.append(dict(i=i,x=float(c[0]),z=float(c[1]),nx=float(nrm[0]),nz=float(nrm[1]),ang=math.atan2(nrm[0],nrm[1]),tilt=tilt,
        cx=xs[i],cz=zs[i],t=T[i],t_audio=hits[i]['time'],note=hits[i]['note'],track=hits[i]['track_name'],drum=hits[i]['drum'],side=side[i]))
def pos(t):
    s=allsegs[0]
    for s_ in allsegs:
        if t>=s_[0]: s=s_
    u=t-s[0]; return (s[1]+s[3]*u, s[2]+s[4]*u-0.5*g*u*u)
nf=int(round(dur*fps))
frames=[list(map(float,pos(f/fps))) for f in range(nf+1)]
# collision check on fine substeps: marble centre vs each paddle's oriented rectangle
def dist_rect(p,k):
    d=np.array(p)-np.array([k['x'],k['z']]); nn=np.array([k['nx'],k['nz']]); tt=np.array([nn[1],-nn[0]])
    u,v=abs(d@tt)-PL/2, abs(d@nn)-PT/2
    return math.hypot(max(u,0),max(v,0))+min(max(u,v),0)
bad=[]
for s in np.arange(0,dur,1/(fps*8)):
    p=pos(s)
    for k in keys:
        if abs(s-k['t'])<1.2/fps: continue
        if dist_rect(p,k)<R*0.97: bad.append((round(s*fps,2),k['i'],round(dist_rect(p,k),3)))
print('collisions (frame,key,dist):',bad[:20],'total',len(bad))
arr=np.array(frames)
sig=fps*0.35; kk=np.arange(-int(3*sig),int(3*sig)+1); w=np.exp(-kk**2/(2*sig*sig)); w/=w.sum()
cz=np.convolve(np.pad(arr[:,1],(len(kk)//2,len(kk)//2),mode='edge'),w,mode='valid')
for it in range(6):
    cz=np.clip(cz,arr[:,1]-a.frame_margin,arr[:,1]+a.frame_margin)
    s2=fps*0.12; k2=np.arange(-int(3*s2),int(3*s2)+1); w2=np.exp(-k2**2/(2*s2*s2)); w2/=w2.sum()
    cz=np.convolve(np.pad(cz,(len(k2)//2,len(k2)//2),mode='edge'),w2,mode='valid')
cam=[[0.0,float(z)] for z in cz]
print('max |marble-cam| z: %.2f'%float(np.max(np.abs(arr[:,1]-cz))))
print('tilt min/mean/max %.0f %.0f %.0f'%(min(k['tilt'] for k in keys),np.mean([k['tilt'] for k in keys]),max(k['tilt'] for k in keys)))
if a.verbose:
  for k in keys: print(f"key {k['i']:2d} t={k['t']:.3f} f={k['t']*fps:5.1f} side={k['side']:+d} z={k['cz']:7.2f} tilt={k['tilt']:5.1f}")
json.dump(dict(fps=fps,duration=dur,R=R,KW=PL,KD=KD,KH=PT,g=g,layout='zigzag',keys=keys,marble=frames,camera=cam),open(a.o,'w'))
