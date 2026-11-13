"""3D keep-out check of the full instrument geometry (contact face + decoration + pins) against the marble path.
usage: python check_keepout.py plan_zz_v2.json [--out report.json]
For every key, all surface probe points of its asset (assets/instruments/<name>/probe_<variant>.npy), transformed exactly as
scene.py places them, must stay >= 0.97 R from the marble centre at all times except within 1.2 frames of its own hit
(same rule as the planner). Also reports the marble-to-surface distance at each hit (should be ~R: contact is real)."""
import json, sys, argparse, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.join(HERE, 'assets', 'instruments')
sys.path.insert(0, INST); import library
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('--out', default=''); ap.add_argument('--sub', type=int, default=8); ap.add_argument('--strict', action='store_true'); ap.add_argument('--look', default='v4'); a = ap.parse_args()
P = json.load(open(a.plan)); fps = P['fps']; R = P['R']; K = P['keys']
M = library.metas(a.look); asg = library.assign(K, M); print('look', a.look)
probes = {}
for n, m in M.items():
    for v in m['variants']: probes[(n, v)] = np.load(os.path.join(m['_dir'], f'probe_{v}.npy')).astype(np.float64)
# marble path at sub-frame resolution: rebuild from per-frame samples by linear interpolation would be lossy; re-evaluate the plan's
# ballistic segments instead -> use the per-frame positions plus quadratic (gravity) interpolation between frames
mar = np.array(P['marble']); g = P['g']
ts = np.arange(0, (len(mar)-1)/fps, 1/(fps*a.sub))
f0 = np.floor(ts*fps).astype(int); u = ts*fps - f0; f1 = np.minimum(f0+1, len(mar)-1)
mx = mar[f0,0]*(1-u) + mar[f1,0]*u
mz = mar[f0,1]*(1-u) + mar[f1,1]*u + 0.5*g*(u/fps)*((1-u)/fps)   # chord + gravity sag correction
viol = []; contact = []; worst = []; hang_pts_total = [0]
for k, (n, v, j) in zip(K, asg):
    pts = probes[(n, v)]; pts = pts[np.abs(pts[:,1]) < R]          # only points within the marble's y-slab can be touched
    nx, nz = k['nx'], k['nz']; tx, tz = nz, -nx
    wx = k['x'] + pts[:,0]*tx + pts[:,2]*nx; wz = k['z'] + pts[:,0]*tz + pts[:,2]*nz; wy = pts[:,1]
    for h in M[n].get('hanging', []):                              # world-vertical parts: sample the tube surface in world space
        hx, hy, hz = library.hanging_world(k, h); th = np.linspace(0, 2*np.pi, 48, endpoint=False); zz = np.linspace(0, -h['length'], 40)
        T, Z = np.meshgrid(th, zz); px = hx + h['radius']*np.cos(T).ravel(); py = hy + h['radius']*np.sin(T).ravel(); pz = hz + Z.ravel()
        sel = np.abs(py) < R; hang_pts_total[0] += int(sel.sum())
        wx = np.r_[wx, px[sel]]; wy = np.r_[wy, py[sel]]; wz = np.r_[wz, pz[sel]]
    rad = (np.sqrt((wx-k['x'])**2 + (wz-k['z'])**2).max() if len(wx) else 0) + R + 0.05
    near = (np.abs(mx-k['x']) < rad) & (np.abs(mz-k['z']) < rad)
    idx = np.where(near)[0]
    if not len(idx): continue
    d = np.sqrt((mx[idx,None]-wx[None])**2 + wy[None]**2 + (mz[idx,None]-wz[None])**2).min(1)
    excl = np.abs(ts[idx]-k['t']) < 1.2/fps
    dd = d[~excl]
    if len(dd): worst.append((float(dd.min()), k['i'], n))
    bad = idx[~excl][dd < 0.97*R]
    for b in bad[:1]: viol.append(dict(key=k['i'], asset=n, variant=v, frame=round(ts[b]*fps,2), dist=round(float(d[np.where(idx==b)[0][0]]),4)))
    hi = np.argmin(np.abs(ts[idx]-k['t'])); contact.append(float(d[hi]))
worst.sort()
c = np.array(contact)
print(f'keys {len(K)}  keep-out violations (<0.97R outside own hit window): {len(viol)}')
for x in viol[:30]: print('  VIOL', x)
print('closest non-hit approaches (dist/R, key, asset):', [(round(w[0]/R,3), w[1], w[2]) for w in worst[:8]])
print('hanging-part points inside the marble slab:', hang_pts_total[0])
print(f'contact distance at hit frame / R: min {c.min()/R:.3f} median {np.median(c)/R:.3f} max {c.max()/R:.3f}')
if a.out: json.dump(dict(violations=viol, closest=[list(w) for w in worst[:50]], contact_over_R=dict(min=c.min()/R, median=float(np.median(c))/R, max=c.max()/R)), open(a.out,'w'), indent=1)

if a.strict and viol: sys.exit(1)
