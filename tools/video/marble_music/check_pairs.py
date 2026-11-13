"""Striker-vs-striker clearance check (v5: big silhouettes behind the marble plane must not run into neighbouring strikers).
usage: python check_pairs.py plan_zz_v2.json --look v5 [--min 0.01] [--strict] [--whitelist FILE] [--out report.json]
All probe points of every key (whole asset incl. pins, plus world-vertical hanging tubes), placed exactly as scene.py does, are
compared with every other key whose bounding box overlaps (KD-tree nearest distance). A pair closer than --min (m) is flagged:
with ~6 mm probe spacing, < 1 cm means touching or interpenetrating.
--strict exits 1 on any flagged pair that is not in the whitelist (default assets/instruments/pairs_whitelist.json; an entry only
covers its exact key pair + asset and only while the gap stays >= its min_gap_m). Camera-aligned parts (meta.aligned, e.g. the v5
flute head joint) are sampled at their hit-frame placement."""
import json, sys, argparse, os, numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments')); import library
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('--look', default='v5'); ap.add_argument('--min', type=float, default=0.01)
ap.add_argument('--strict', action='store_true'); ap.add_argument('--out', default='')
ap.add_argument('--whitelist', default=os.path.join(HERE, 'assets', 'instruments', 'pairs_whitelist.json')); a = ap.parse_args()
P = json.load(open(a.plan)); K = P['keys']; M = library.metas(a.look); asg = library.assign(K, M)
probes = {(n, v): np.load(os.path.join(m['_dir'], f'probe_{v}.npy')).astype(np.float64)[::2] for n, m in M.items() for v in m['variants']}
W = []
for k, (n, v, j) in zip(K, asg):
    p = probes[(n, v)]; nx, nz = k['nx'], k['nz']; tx, tz = nz, -nx
    pts = np.c_[k['x'] + p[:,0]*tx + p[:,2]*nx, p[:,1], k['z'] + p[:,0]*tz + p[:,2]*nz]
    for h in M[n].get('hanging', []):
        hx, hy, hz = library.hanging_world(k, h); T, Z = np.meshgrid(np.linspace(0, 2*np.pi, 24, endpoint=False), np.linspace(0, -h['length'], 30))
        pts = np.r_[pts, np.c_[hx + h['radius']*np.cos(T).ravel(), hy + h['radius']*np.sin(T).ravel(), hz + Z.ravel()]]
    for ap_ in M[n].get('aligned', []):                      # camera-aligned behind-plane parts at their hit-frame placement
        fr = min(len(P['camera'])-1, int(round(k['t']*P['fps']))); (lx, ly, lz), ph, sc = library.aligned_local(k, P['camera'][fr], ap_)
        L0 = np.hypot(ap_['b'][0]-ap_['a'][0], ap_['b'][2]-ap_['a'][2]); T, U = np.meshgrid(np.linspace(0, 2*np.pi, 20, endpoint=False), np.linspace(0, -L0, 30))
        r = ap_.get('radius', 0.06); mx_, my_, mz_ = U.ravel()*sc[0], r*np.cos(T).ravel()*sc[1], r*np.sin(T).ravel()*sc[2]
        c, s_ = np.cos(ph), np.sin(ph); qx = lx + c*mx_ + s_*mz_; qz = lz - s_*mx_ + c*mz_; qy = ly + my_   # rotation about local Y
        pts = np.r_[pts, np.c_[k['x'] + qx*nz + qz*nx, qy, k['z'] - qx*nx + qz*nz]]
    W.append((pts, pts.min(0), pts.max(0), n))
trees = [cKDTree(w[0]) for w in W]; res = []
for i in range(len(W)):
    for jj in range(i+1, len(W)):
        lo = np.maximum(W[i][1], W[jj][1]); hi = np.minimum(W[i][2], W[jj][2])
        if np.any(lo > hi + a.min): continue
        d, _ = trees[jj].query(W[i][0], k=1, distance_upper_bound=0.2); md = float(d.min())
        if md < 0.2: res.append((md, K[i]['i'], W[i][3], K[jj]['i'], W[jj][3]))
res.sort(); bad = [r for r in res if r[0] < a.min]
WL = json.load(open(a.whitelist))['pairs'] if a.whitelist and os.path.isfile(a.whitelist) else []
def allowed(r):
    return any(sorted(w['keys']) == sorted([r[1], r[3]]) and w['asset'] == r[2] == r[4] and r[0] >= w['min_gap_m'] for w in WL)
known = [r for r in bad if allowed(r)]; new_ = [r for r in bad if not allowed(r)]
print('look', a.look, 'keys', len(K), 'close pairs (<20cm):', len(res), f' pairs under {a.min*100:.1f} cm:', len(bad))
for r in known: print('  known (whitelisted)', r)
for r in new_[:30]: print('  CLASH', r)
print('new (not whitelisted) pairs:', len(new_))
print('closest pairs (m, key, asset, key, asset):', [tuple([round(r[0],4)]+list(r[1:])) for r in res[:10]])
if a.out: json.dump(dict(clashes=new_, whitelisted=known, closest=res[:50]), open(a.out,'w'), indent=1)
if a.strict and new_: sys.exit(1)
