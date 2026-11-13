"""select_stills.py plan_zz_v2.json [--print-frames] -- pick one hit frame per instrument section for still checks:
maximise the number of same-section strikers inside the v2+ camera frame (camera rig offset (0.5,-5.3,1.0), aim (0,0,-0.9),
40 mm lens, 36 mm vertical sensor, 9:16) and keep the marble near the upper-middle; skip the first/last 15% of each section."""
import json, sys, math, numpy as np
P = json.load(open(sys.argv[1])); K = P['keys']; fps = P['fps']; cam = np.array(P['camera'])
OFF = np.array([0.5,-5.3,1.0]); AIM = np.array([0,0,-0.9]); TANV = (36/2)/40; TANH = TANV*9/16
def project(cz, pts):
    c = np.array([0, 0, cz]) + OFF; t = np.array([0, 0, cz]) + AIM; f = (t-c)/np.linalg.norm(t-c)
    r = np.cross(f, [0,0,1]); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = pts - c; zc = d @ f; return (d @ r)/zc/TANH, (d @ u)/zc/TANV
secs = {}
for k in K: secs.setdefault(k['track'], []).append(k)
allp = np.array([[k['x'], 0, k['z']] for k in K]); tr = np.array([k['track'] for k in K])
out = []
for s, ks in secs.items():
    n = len(ks); best = None
    for k in ks[int(n*0.15):max(int(n*0.85), int(n*0.15)+1)]:
        f = round(k['t']*fps); cz = cam[f][1]
        u, v = project(cz, allp); vis = (np.abs(u) < 0.85) & (np.abs(v) < 0.88)
        same = int((vis & (tr == s)).sum())
        mu, mv = project(cz, np.array([[k['cx'], 0, k['cz']]]))
        score = same - 4*abs(mv[0]-0.15)
        if best is None or score > best[0]: best = (score, f, same, int(vis.sum()), float(mv[0]))
    out.append((s, best))
for s, b in out: print(f"{s:34s} frame {b[1]:5d}  same-section strikers in view {b[2]}  all {b[3]}  marble v={b[4]:+.2f}")
print(','.join(str(b[1]) for s, b in out))
