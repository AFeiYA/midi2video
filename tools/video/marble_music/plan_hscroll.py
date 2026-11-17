"""Horizontal long-scroll planner (16:9, layout 'hscroll'): the marble travels LEFT -> RIGHT down a staircase of strikers
along one very long wall; every contact still lands exactly on its note frame.
usage: python plan_hscroll.py hits.json --fps 30 -o plan.json   (or: plan_zigzag.py hits.json --layout hscroll ...)

Design
- x: contact points march strictly to the right. Hop length = clamp(speed*dt, need, dx_max) where `need` is the striker
  footprint (probe-point x extent of key i's right side + key i+1's left side + gap) -> wide silhouettes (grand piano) get
  more room, short notes never pack strikers into each other. Afterwards a 3D neighbour check (probe points, same transform as
  scene.py / check_pairs.py) widens any hop whose strikers still come closer than --pair-gap, and a keep-out check (marble vs
  probe points, same rule as check_keepout.py) steepens / flattens the hop that clips a silhouette; the plan is rebuilt until clean.
- z: a sawtooth staircase. Inside one segment (default: one instrument of the relay) the target height falls with a gentle
  slope (--slope m per m of x) so it reads as a descending flight of steps; at the next segment the target jumps back to the top
  (z=0) and the hand-off hop(s) lift the marble back up. Rising is limited so the marble always lands on a striker from ABOVE
  (arrival vz <= -vmin): short hand-off gaps climb over a few hops (a small rising ramp), the usual 1.2 s phrase-end lob climbs
  in one go. Height therefore stays inside a fixed band for the whole piece (wall size and camera height are bounded).
  --reset family keeps descending through a whole family instead (bigger drop, one lift per family); --reset none = endless slope.
- camera: x = heavily smoothed marble x + lead (marble sits left of centre, the camera "looks ahead"), clamped so the marble
  stays inside [left_frac, right_frac] of the frame; z = gently smoothed marble z, clamped so lobs and the lower-third area keep
  the marble on screen. Written as plan['camera'] = [[cx, cz], ...] (rig position, as for 9:16) + plan['cam_rig'] (offset/aim/lens)."""
import json, argparse, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments'))
import library
def build_parser(ap=None):
    ap = ap or argparse.ArgumentParser()
    ap.add_argument('hits'); ap.add_argument('--fps', type=int, default=30); ap.add_argument('-o', default='plan.json')
    ap.add_argument('--g', type=float, default=14.0, help='gravity (lower than zigzag 30: whole-note lobs stay inside a 16:9 frame)')
    ap.add_argument('--speed', type=float, default=2.8, help='preferred horizontal travel (m/s); hop = speed*dt unless the footprint needs more')
    ap.add_argument('--dx-max', type=float, default=3.0); ap.add_argument('--gap', type=float, default=0.06, help='footprint gap between neighbours (m)')
    ap.add_argument('--slope', type=float, default=0.12, help='target descent per metre of x inside a segment')
    ap.add_argument('--reset', default='instrument', choices=['instrument', 'family', 'none'])
    ap.add_argument('--max-drop', type=float, default=1.4); ap.add_argument('--vmin', type=float, default=1.6, help='min downward speed at contact (m/s)')
    ap.add_argument('--pair-gap', type=float, default=0.03); ap.add_argument('--fix-iters', type=int, default=40)
    ap.add_argument('--look', default='v5'); ap.add_argument('--lead', type=float, default=0.8, help='camera leads the marble by this (m)')
    ap.add_argument('--cam-sigma-x', type=float, default=0.6); ap.add_argument('--cam-sigma-z', type=float, default=0.9)
    ap.add_argument('--cam-dist', type=float, default=4.3, help='camera distance in front of the marble plane')
    ap.add_argument('--snap', type=int, default=1); ap.add_argument('--verbose', type=int, default=0)
    return ap
R = 0.15; PL, KD, PT = 0.62, 0.36, 0.09
def main(a):
    H = json.load(open(a.hits)); hits = H['hits']; dur = H['end'] - H['start']; fps = a.fps; g = a.g
    iset = H.get('instrument_set')
    T = [(round(h['time']*fps)/fps if a.snap else h['time']) for h in hits]; n = len(T)
    stub = [dict(i=i, track=h['track_name'], program=h.get('program'), drum=h['drum'], note=h['note']) for i, h in enumerate(hits)]
    M = library.metas(a.look); asg = library.assign(stub, M, iset)
    import registry
    fam = []; num = []
    for h in hits:
        e = registry.resolve_track(h['track_name'], h.get('program')) if iset else None
        fam.append(e['family'] if e else 'F?'); num.append(e['num'] if e and e['num'] is not None else 0)
    seg_of = [(h['track_name'] if a.reset == 'instrument' else fam[i] if a.reset == 'family' else 'all') for i, h in enumerate(hits)]
    probes = {}; ext = []
    for nme, v, _ in asg:
        if (nme, v) not in probes:
            p = np.load(os.path.join(M[nme]['_dir'], f'probe_{v}.npy')).astype(np.float64)
            pts = [p]
            for hh in M[nme].get('hanging', []):     # local-frame approximation for the footprint only
                ax, ay, az = hh['attach']; zz = np.linspace(0, -hh['length'], 12)
                pts.append(np.c_[np.full(12, ax), np.full(12, ay), az + zz])
            probes[(nme, v)] = p
            q = np.concatenate(pts); ext_ = (q[:, 0].min(), q[:, 0].max())
            probes[(nme, v, 'ext')] = ext_
        ext.append(probes[(nme, v, 'ext')])
    def normal(vin, vout):
        nrm = vout/np.linalg.norm(vout) - vin/np.linalg.norm(vin); return nrm/np.linalg.norm(nrm)
    def build(extra_dx, extra_d):
        xs = [0.0]; zs = [0.0]; segs = []; pads = []; seg_start = {seg_of[0]: 0.0}
        pre = 0.5; d0 = 0.35; ent_dx = max(1.2, a.speed*pre)
        vz0 = (-d0 + 0.5*g*pre*pre)/pre                         # entry: from the left, slightly above, landing on key 0
        segs.append((T[0]-pre, -ent_dx, d0, ent_dx/pre, vz0, pre))
        for i in range(n):
            vin = np.array([segs[-1][3], segs[-1][4] - g*segs[-1][5]])
            last = (i == n-1)
            dt = 0.45 if last else T[i+1] - T[i]
            need = (ext[i][1] - (ext[i+1][0] if not last else -0.3)) + a.gap
            dx = min(max(a.speed*dt, need), max(a.dx_max, need)) + extra_dx.get(i, 0.0)
            xn = xs[i] + dx
            if last: d = 0.6
            else:
                s = seg_of[i+1]
                if s != seg_of[i] and a.reset != 'none': seg_start[s] = xn
                elif s not in seg_start: seg_start[s] = xn
                zt = -a.slope*(xn - seg_start[s])
                d = zs[i] - zt
                rise_max = 0.5*g*dt*dt - a.vmin*dt               # arrival vz = -(d + g dt^2/2)/dt <= -vmin
                d = min(max(d, -rise_max), a.max_drop) + extra_d.get(i, 0.0)
            vx = dx/dt; vz = (-d + 0.5*g*dt*dt)/dt
            nn = normal(vin, np.array([vx, vz])); c = np.array([xs[i], zs[i]]) - nn*(R + PT/2)
            pads.append((c, nn)); segs.append((T[i], xs[i], zs[i], vx, vz, (1e9 if last else dt)))
            xs.append(xn); zs.append(zs[i] - d)
        return xs[:n], zs[:n], segs, pads
    def pos_arr(segs, ts):
        st = np.array([s[0] for s in segs]); idx = np.clip(np.searchsorted(st, ts, side='right') - 1, 0, len(segs)-1)
        S = np.array([s[:5] for s in segs])[idx]; u = ts - S[:, 0]
        return np.c_[S[:, 1] + S[:, 3]*u, S[:, 2] + S[:, 4]*u - 0.5*g*u*u]
    def world(i, c, nn, sub=2, cam=None):
        nme, v, _ = asg[i]; p = probes[(nme, v)][::sub]; nx, nz = nn; tx, tz = nz, -nx
        W = np.c_[c[0] + p[:, 0]*tx + p[:, 2]*nx, p[:, 1], c[1] + p[:, 0]*tz + p[:, 2]*nz]
        k = dict(x=c[0], z=c[1], nx=nx, nz=nz)
        for hh in M[nme].get('hanging', []):
            hx, hy, hz = library.hanging_world(k, hh); th, zz = np.meshgrid(np.linspace(0, 2*np.pi, 24, endpoint=False), np.linspace(0, -hh['length'], 30))
            W = np.r_[W, np.c_[hx + hh['radius']*np.cos(th).ravel(), hy + hh['radius']*np.sin(th).ravel(), hz + zz.ravel()]]
        for ap_ in M[nme].get('aligned', []):                  # camera-aligned behind-plane parts (flute head joint) at the hit-frame camera
            fr = min(len(cam)-1, max(0, int(round(T[i]*fps)))); (lx, ly, lz), ph, sc = library.aligned_local(k, cam[fr], ap_, CAM_OFF)
            L0 = np.hypot(ap_['b'][0]-ap_['a'][0], ap_['b'][2]-ap_['a'][2]); th, U = np.meshgrid(np.linspace(0, 2*np.pi, 20, endpoint=False), np.linspace(0, -L0, 30))
            r = ap_.get('radius', 0.06); mx_, my_, mz_ = U.ravel()*sc[0], r*np.cos(th).ravel()*sc[1], r*np.sin(th).ravel()*sc[2]
            cc, ss = np.cos(ph), np.sin(ph); qx = lx + cc*mx_ + ss*mz_; qz = lz - ss*mx_ + cc*mz_; qy = ly + my_
            W = np.r_[W, np.c_[c[0] + qx*nz + qz*nx, qy, c[1] - qx*nx + qz*nz]]
        return W
    nf = int(round(dur*fps)); ft = np.arange(nf + 1)/fps
    def camera(segs):
        arr = pos_arr(segs, ft)
        # ---- camera: rig x leads the marble, z follows gently
        def gauss(sig_s, y):
            sig = max(fps*sig_s, 1e-3); kk = np.arange(-int(3*sig), int(3*sig) + 1); w = np.exp(-kk**2/(2*sig*sig)); w /= w.sum()
            return np.convolve(np.pad(y, (len(kk)//2, len(kk)//2), mode='edge'), w, mode='valid')
        vh = 2*a.cam_dist*math.tan(math.atan(18/40)); vw = vh*16/9         # visible height/width at the marble plane (lens 40, 36 mm vertical)
        cx = gauss(a.cam_sigma_x, arr[:, 0] + a.lead)
        for _ in range(6):                                            # marble between 22% and 62% of the frame width
            cx = np.clip(cx, arr[:, 0] - (0.62 - 0.5)*vw, arr[:, 0] + (0.5 - 0.22)*vw); cx = gauss(0.15, cx)
        aim_z = -0.35                                                 # image centre = rig z + aim_z: marble rides a bit above centre
        cz = gauss(a.cam_sigma_z, arr[:, 1])
        up, dn = 0.5*vh - 0.30 + aim_z, 0.5*vh*0.12 - aim_z           # marble <= 0.30 m below the top edge and at most 12% of the half-height below centre: strikers hanging under it stay above the lower third
        for _ in range(6):
            cz = np.clip(cz, arr[:, 1] - up, arr[:, 1] + dn); cz = gauss(0.15, cz)

        return arr, cx, cz, vh, vw, aim_z
    CAM_OFF = (0.0, -a.cam_dist, 0.8)
    from scipy.spatial import cKDTree
    extra_dx = {}; extra_d = {}
    for it in range(a.fix_iters + 1):
        xs, zs, segs, pads = build(extra_dx, extra_d)
        _a, _cx, _cz, *_ = camera(segs); camf = np.c_[_cx, _cz]
        Wd = [world(i, c, nn, cam=camf) for i, (c, nn) in enumerate(pads)]
        clash = []
        for i in range(n):
            for j in range(i+1, min(n, i+4)):
                lo = np.maximum(Wd[i].min(0), Wd[j].min(0)); hi = np.minimum(Wd[i].max(0), Wd[j].max(0))
                if np.any(lo > hi + a.pair_gap): continue
                d_, _ = cKDTree(Wd[j]).query(Wd[i], k=1, distance_upper_bound=0.3)
                if d_.min() < a.pair_gap: clash.append((i, j, float(d_.min())))
        ko = []                                                  # keep-out: marble vs every probe point in the marble slab
        for i in range(n):
            P_ = Wd[i]; P_ = P_[np.abs(P_[:, 1]) < R]
            t0, t1 = T[i] - 2.0, T[i] + 2.0; ts = np.arange(max(t0, -0.5), min(t1, dur + 0.5), 1/(fps*8))
            ts = ts[np.abs(ts - T[i]) >= 1.2/fps]
            if not len(ts): continue
            mp = pos_arr(segs, ts); rad = np.hypot(P_[:, 0] - pads[i][0][0], P_[:, 2] - pads[i][0][1]).max() + R + 0.05
            near = np.hypot(mp[:, 0] - pads[i][0][0], mp[:, 1] - pads[i][0][1]) < rad
            if not near.any(): continue
            tr = cKDTree(P_); dd, _ = tr.query(np.c_[mp[near, 0], np.zeros(near.sum()), mp[near, 1]], k=1)
            bad = dd < 0.985*R
            if bad.any(): ko.append((i, float(ts[near][bad][0]), float(dd.min())))
        if a.verbose or it == 0 or (not clash and not ko): print(f'iter {it}: pair clashes {len(clash)} keep-out {len(ko)}', clash[:4], ko[:4], flush=True)
        if not clash and not ko: break
        for i, j, _ in clash: extra_dx[j-1] = extra_dx.get(j-1, 0.0) + 0.08
        for i, ts_, _ in ko:
            h = int(np.searchsorted(T, ts_, side='right')) - 1       # hop the marble is on when it clips key i
            if h == i - 1: extra_d[h] = extra_d.get(h, 0.0) + 0.12   # approaching key i: steeper arrival
            elif h == i: extra_d[h] = extra_d.get(h, 0.0) - 0.12     # leaving key i: steeper launch
            elif h >= 0: extra_dx[h] = extra_dx.get(h, 0.0) + 0.1
    else:
        print('WARN: fix iterations exhausted', len(clash), len(ko))
    keys = []
    for i in range(n):
        c, nrm = pads[i]; tilt = math.degrees(math.acos(max(-1, min(1, nrm[1]))))
        keys.append(dict(i=i, x=float(c[0]), z=float(c[1]), nx=float(nrm[0]), nz=float(nrm[1]), ang=math.atan2(nrm[0], nrm[1]), tilt=tilt,
                         cx=xs[i], cz=zs[i], t=T[i], t_audio=hits[i]['time'], note=hits[i]['note'], track=hits[i]['track_name'], drum=hits[i]['drum'],
                         program=hits[i].get('program'), side=1, family=fam[i], num=num[i]))
    nf = int(round(dur*fps)); ft = np.arange(nf + 1)/fps
    arr, cx, cz, vh, vw, aim_z = camera(segs)
    frames = arr.tolist()
    cam = np.c_[cx, cz].tolist()
    # ---- wall segments (families) + instrument spans for the titles
    fams = []; insts = []
    for i in range(n):
        if not fams or fams[-1]['family'] != fam[i]: fams.append(dict(family=fam[i], i0=i, t0=T[i], x0=keys[i]['x']))
        fams[-1].update(i1=i, t1=T[i], x1=keys[i]['x'])
        if not insts or insts[-1]['track'] != hits[i]['track_name']: insts.append(dict(track=hits[i]['track_name'], num=num[i], family=fam[i], i0=i, t0=T[i], x0=keys[i]['x']))
        insts[-1].update(i1=i, t1=T[i], x1=keys[i]['x'])
    zr = [k['z'] for k in keys]
    print(f'keys {n}  x span {keys[0]["x"]:.1f}..{keys[-1]["x"]:.1f} m  z band {min(zr):.2f}..{max(zr):.2f} m  visible {vw:.1f} x {vh:.1f} m')
    print('max |marble-camx| %.2f  max marble-camz %+.2f/%+.2f' % (float(np.abs(arr[:, 0] - cx).max()), float((arr[:, 1] - cz).max()), float((arr[:, 1] - cz).min())))
    print('tilt min/mean/max %.0f %.0f %.0f' % (min(k['tilt'] for k in keys), np.mean([k['tilt'] for k in keys]), max(k['tilt'] for k in keys)))
    apex = max(float(arr[(ft >= T[i]) & (ft < (T[i+1] if i+1 < n else dur)), 1].max(initial=-1e9) - zs[i]) for i in range(n))
    print('max apex above take-off %.2f m;  hop dx min/median/max %.2f %.2f %.2f' % (apex, *np.percentile(np.diff(xs), [0, 50, 100])) if n > 1 else '')
    if a.verbose:
        for k in keys: print(f"key {k['i']:3d} t={k['t']:.3f} x={k['cx']:7.2f} z={k['cz']:6.2f} tilt={k['tilt']:5.1f} {asg[k['i']][0]}")
    PLAN = dict(fps=fps, duration=dur, R=R, KW=PL, KD=KD, KH=PT, g=g, layout='hscroll', aspect='16:9', keys=keys, marble=frames, camera=cam,
                cam_rig=dict(off=list(CAM_OFF), aim=[0.0, 0.0, aim_z], lens=40, sensor_fit='VERTICAL', sensor=36),
                families=fams, instruments=insts, hscroll=dict(speed=a.speed, slope=a.slope, reset=a.reset, lead=a.lead))
    if iset: PLAN['instrument_set'] = iset
    json.dump(PLAN, open(a.o, 'w'))
if __name__ == '__main__':
    main(build_parser().parse_args())
