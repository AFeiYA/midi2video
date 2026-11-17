"""Independent audit of hscroll v2 ballistic segments, signed hit faces and reflection directions.
Usage: python check_hscroll_physics.py plan.json --strict [--out physics.json]
Uses exact segment velocities, not frame finite differences. Powered/frictional strikers may change speed;
this is direction-specular art-directed motion, NOT a passive elastic rigid-body simulation.
The final departing segment is checked for continuity/reflection but exempt from the hop speed/height bounds.
"""
import argparse, json, math
import numpy as np

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('plan'); ap.add_argument('--strict',action='store_true'); ap.add_argument('--out',default='')
a=ap.parse_args(); p=json.load(open(a.plan)); g=p['g']; keys=p['keys']; seg=p['ballistics']; cfg=p['physics']; bad=[]; stats=[]
def fail(i,why): bad.append(dict(key=i,reason=why))
for i,k in enumerate(keys):
    before,after=seg[i],seg[i+1]
    elapsed=k['t']-before[0]
    pin=np.array([before[1]+before[3]*elapsed,before[2]+before[4]*elapsed-.5*g*elapsed**2])
    contact=np.array([k['cx'],k['cz']]); normal=np.array([k['nx'],k['nz']]); c=np.array([k['x'],k['z']])
    vi=np.array([before[3],before[4]-g*elapsed]); vo=np.array([after[3],after[4]])
    if np.linalg.norm(pin-contact)>1e-7 or np.linalg.norm(np.array(after[1:3])-contact)>1e-7: fail(i,'position discontinuity')
    if np.linalg.norm(c+normal*(p['R']+p['KH']/2)-contact)>1e-7: fail(i,'contact on wrong face')
    if vi@normal>=-1e-6 or vo@normal<=1e-6: fail(i,'wrong signed approach/departure')
    ui=vi/np.linalg.norm(vi); uo=vo/np.linalg.norm(vo)
    if np.linalg.norm(ui-2*(ui@normal)*normal-uo)>1e-6: fail(i,'non-specular direction')
    lev=k['relax_level']; tilt=cfg['tilt_max']+(8 if lev==2 else 0)
    cm=math.cos(math.radians(tilt)); mount=k['mount']
    if mount=='ceil':
        if normal[1]>-cm+1e-7 or vi[1]<cfg['vmin_up']-1e-7: fail(i,'ceiling hit without down-facing face/upward arrival')
    else:
        if normal[1]<cm-1e-7 or vi[1]>-cfg['vmin_dn']+1e-7: fail(i,'floor hit without up-facing face/downward arrival')
    ratio=float(np.linalg.norm(vo)/np.linalg.norm(vi)); apex=0.
    if i<len(keys)-1:
        lo,hi=(cfg['kick_min'],cfg['kick_max']) if lev<2 else (.3,3.2)
        if not lo-1e-7<=ratio<=hi+1e-7: fail(i,'speed ratio outside declared relax bound')
        dt=keys[i+1]['t']-k['t']; z0=k['cz']; z1=keys[i+1]['cz']
        ta=min(dt,max(0,vo[1]/g)); top=z0+vo[1]*ta-.5*g*ta*ta; apex=top-max(z0,z1)
        limit=max(cfg['apex_max'],.6*g*dt*dt/8+.2) if lev==0 else max(cfg['apex_max']+(.4 if lev==2 else 0),g*dt*dt/8+.1)
        if apex>limit+1e-6: fail(i,'apex beyond declared bound')
    stats.append(dict(key=i,mount=mount,vin_z=float(vi[1]),vout_z=float(vo[1]),speed_ratio=ratio,relax_level=lev,apex_above_higher_end=apex))
# Audit every exported frame against the same gravity law, including under-hit transitions.
for f,xy in enumerate(p['marble']):
    t=f/p['fps']; s=next((s for s in reversed(seg) if s[0]<=t),seg[0]); u=t-s[0]
    if np.linalg.norm(np.array(xy)-[s[1]+s[3]*u,s[2]+s[4]*u-.5*g*u*u])>1e-6: fail(f,'sample not ballistic')
report=dict(violations=bad,hits=len(keys),ceiling_hits=sum(k['mount']=='ceil' for k in keys),max_apex_above_higher_end=max(s['apex_above_higher_end'] for s in stats),hits_audit=stats)
print('gravity',g,'hits',len(keys),'ceiling hits',report['ceiling_hits'],'physics violations',len(bad),'max apex above higher endpoint',round(report['max_apex_above_higher_end'],3))
for b in bad[:20]: print(b)
if a.out: json.dump(report,open(a.out,'w'),indent=1)
if a.strict and bad: raise SystemExit(1)
