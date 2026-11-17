"""hscroll v2 planner: seeded, deterministic motion-pattern system for the 16:9 horizontal long scroll (plan_hscroll.py --style v2).

Every contact still lands exactly on its note frame; between contacts the marble flies a gravity parabola (ONE gravity for the
whole piece, --g 10 ~ real 9.81 m/s^2 at scene scale, so arcs stay low and compact). Each striker is placed where the marble
touches it, its face normal bisects the reversed incoming and the outgoing direction (mirror reflection; the striker may add or
take energy, |v_out|/|v_in| in [--kick-min, --kick-max]).

Two mounts
- floor: face up-ish (n_z >= cos(--tilt-max)), marble must ARRIVE FALLING (v_z <= -vmin_dn).
- ceil : face down-ish (n_z <= -cos(--tilt-max)), striker hung upside down; marble must ARRIVE RISING (v_z >= +vmin_up), so the
  floor->ceiling gap must be >= g dt^2/2 + vmin_up dt (0.71 m for a 0.306 s note at g 10). Assets with world-vertical hanging
  parts (vibraphone / tubular-bell tubes) are floor-only (their tubes would hang through the marble path).
A reversal ('reverse hit') is just a contact where v_x changes sign; the tilt limit keeps reversal faces <= --tilt-max from the
mount direction, so reversals happen where the marble moves steeply (mostly off the ceiling row, or a steep fall onto the floor).

Patterns (per phrase; phrases = runs of one instrument split at gaps >= --phrase-gap and at --phrase-max hits)
  stair_down     floor steps, small dx, gentle drop
  stair_up       climbing zipper: floor -> ceiling -> floor a bit higher ... (the only cheap way up with real gravity)
  shuttle        upper/lower pincer: alternate floor / ceiling rows ~0.8-1.0 m apart, moving right
  zigzag_rev     back-and-forth: rise right onto a ceiling striker, bounce back LEFT-down onto the floor, rise right again ...
  cluster_spiral tight loop: rise LEFT onto the ceiling, fall far right onto the floor, rise left again ... (compact, circling)
  long_glide     long low arc that trades height for distance (long notes; the instrument hand-off hop is a glide too)
Variety rules: never the same pattern in two consecutive phrases; intensity follows note density (dense phrases draw the busy
patterns: shuttle / zigzag_rev / cluster_spiral; sparse ones stair / glide); height steering: near the band top descending
patterns are favoured, near the bottom climbing ones; every pattern drifts right on average (net x velocity > 0) so the camera
mostly pans right and only briefly backs up on reversals.
Randomness: numpy default_rng(--seed) drives the pattern draw and per-hop jitter; same hits + seed + options -> identical plan.
Each hop: the pattern's proposal (+ jitter) is tried first, then a fixed fallback grid ordered by closeness to the proposal; a
candidate must pass physics (arrival direction, tilt, kick ratio, apex <= --apex-max above the higher end, height band) and
geometry (probe points of the new striker vs all placed strikers >= --pair-gap; marble path vs every striker >= R outside the
own-hit window; same rules as check_pairs.py / check_keepout.py). If no candidate passes, the same list is retried with relaxed
physics (level 1: long-note apex up to the level lob g dt^2/8 + 0.1 and 0.45 m more floor depth; level 2: + 8 deg tilt, kick
0.3-3.2, apex +0.4 m), then dead ends backtrack (bounded). The planner prints how many hops needed a relax level."""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments'))
import library
R = 0.15; PL, KD, PT = 0.62, 0.36, 0.09
PATTERNS = ['stair_down', 'stair_up', 'shuttle', 'zigzag_rev', 'cluster_spiral', 'long_glide']
BUSY = {'shuttle', 'zigzag_rev', 'cluster_spiral'}
def add_args(ap):
    ap.add_argument('--seed', type=int, default=4)
    ap.add_argument('--tilt-max', type=float, default=62.0); ap.add_argument('--vmin-dn', type=float, default=1.0); ap.add_argument('--vmin-up', type=float, default=0.8)
    ap.add_argument('--kick-min', type=float, default=0.45); ap.add_argument('--kick-max', type=float, default=2.4)
    ap.add_argument('--apex-max', type=float, default=1.1, help='max apex above the higher end of a hop (m); long notes may reach 0.6*g*dt^2/8+0.2 (1.3 m for the 1.224 s hand-off)')
    ap.add_argument('--band', default='-2.4,0.0', help='floor-contact height band (m); ceiling contacts may sit up to --row-max above')
    ap.add_argument('--row-max', type=float, default=1.25); ap.add_argument('--phrase-gap', type=float, default=0.85); ap.add_argument('--phrase-max', type=int, default=9)
    ap.add_argument('--backtrack', type=int, default=8)
def plan_v2(a, H, hits, T, asg, M, probes, fam, num, dur, fps):
    g = a.g; rng = np.random.default_rng(a.seed); n = len(T)
    cmin = math.cos(math.radians(a.tilt_max)); zlo, zhi = map(float, a.band.split(','))
    hang = [bool(M[asg[i][0]].get('hanging')) for i in range(n)]
    ext = [probes[(asg[i][0], asg[i][1], 'ext')] for i in range(n)]       # local x extent (left, right) of each striker
    # ---------------- phrases + pattern draw
    ph_id = [0]*n; phrases = [[0]]
    for i in range(1, n):
        new = hits[i]['track_name'] != hits[i-1]['track_name'] or (T[i] - T[i-1]) >= a.phrase_gap or len(phrases[-1]) >= a.phrase_max
        if new: phrases.append([])
        phrases[-1].append(i); ph_id[i] = len(phrases) - 1
    def density(p):
        if len(p) < 2: return 0.0
        return (len(p) - 1)/max(1e-3, T[p[-1]] - T[p[0]])
    ph_pat = []
    def draw(q, z_now):
        p = phrases[q]; d = density(p); prev = ph_pat[q-1] if q else None
        w = {'stair_down': 1.0, 'stair_up': 1.0, 'shuttle': 1.0, 'zigzag_rev': 1.0, 'cluster_spiral': 1.0, 'long_glide': 0.35}
        if d >= 3.0:
            for k in BUSY: w[k] *= 2.2
            w['long_glide'] *= 0.3
        elif d < 2.2:
            for k in BUSY: w[k] *= 0.5
            w['stair_down'] *= 1.6; w['long_glide'] *= 2.5
        if len(p) <= 2: w = {'long_glide': 1.0, 'stair_down': 0.6, 'stair_up': 0.3}
        if any(hang[i] for i in p): w = {k_: w.get(k_, 0.3) for k_ in ('stair_down', 'long_glide', 'stair_up')}   # floor-only strikers (hanging tubes)
        mid = 0.5*(zlo + zhi); span = (zhi - zlo)/2; u = (z_now - mid)/span          # -1 bottom .. +1 top
        for k_, e_ in (('stair_down', 1.6), ('long_glide', 1.0), ('stair_up', -1.2), ('shuttle', -0.6)):
            if k_ in w: w[k_] *= math.exp(e_*u)
        if prev in w and len(w) > 1: w[prev] = 0.0
        ks = sorted(w); pw = np.array([w[k] for k in ks]); pw /= pw.sum()
        return ks[int(rng.choice(len(ks), p=pw))]
    # ---------------- probes in world space
    def world(i, c, nn, cam_xz=None):
        nme, v, _ = asg[i]; p = probes[(nme, v)][::3]; nx, nz = nn; tx, tz = nz, -nx
        W = np.c_[c[0] + p[:, 0]*tx + p[:, 2]*nx, p[:, 1], c[1] + p[:, 0]*tz + p[:, 2]*nz]
        k = dict(x=c[0], z=c[1], nx=nx, nz=nz)
        for hh in M[nme].get('hanging', []):
            hx, hy, hz = library.hanging_world(k, hh); th, zz = np.meshgrid(np.linspace(0, 2*np.pi, 16, endpoint=False), np.linspace(0, -hh['length'], 24))
            W = np.r_[W, np.c_[hx + hh['radius']*np.cos(th).ravel(), hy + hh['radius']*np.sin(th).ravel(), hz + zz.ravel()]]
        for ap_ in M[nme].get('aligned', []):     # flute head joint: approximate camera = straight in front, refined by the final check
            cam = cam_xz if cam_xz is not None else (c[0], c[1])
            (lx, ly, lz), phh, sc = library.aligned_local(k, cam, ap_, (0.0, -a.cam_dist, 0.8))
            L0 = math.hypot(ap_['b'][0]-ap_['a'][0], ap_['b'][2]-ap_['a'][2]); th, U = np.meshgrid(np.linspace(0, 2*np.pi, 16, endpoint=False), np.linspace(0, -L0, 24))
            r = ap_.get('radius', 0.06); mx_, my_, mz_ = U.ravel()*sc[0], r*np.cos(th).ravel()*sc[1], r*np.sin(th).ravel()*sc[2]
            cc, ss = math.cos(phh), math.sin(phh); qx = lx + cc*mx_ + ss*mz_; qz = lz - ss*mx_ + cc*mz_; qy = ly + my_
            W = np.r_[W, np.c_[c[0] + qx*nz + qz*nx, qy, c[1] - qx*nx + qz*nz]]
        return W
    def unit(v): return v/np.linalg.norm(v)
    SUB = 1/(fps*8)
    def hop_samples(t0, x0, z0, vx, vz, dt):
        u = np.arange(0, dt + 1e-9, SUB); return np.c_[t0 + u, x0 + vx*u, z0 + vz*u - 0.5*g*u*u]
    # ---------------- sequential placement with bounded backtracking
    pre = 0.5; e_dx, e_dz = 0.9, 0.35
    ent = (T[0] - pre, -e_dx, e_dz, e_dx/pre, (-e_dz + 0.5*g*pre*pre)/pre, pre)
    pos = [None]*n; mount = ['floor'] + [None]*(n-1); pos[0] = (0.0, 0.0)
    hops = [None]*n; vin = [None]*n; vin[0] = np.array([ent[3], ent[4] - g*pre])
    strk = [None]*n                                   # (c, n, W, tree_all, tree_slab, bbox_lo, bbox_hi)
    pat_of = [None]*n; samples = [hop_samples(*ent)]
    def proposals(i, pat, k, dt, st):
        """(dx, dz, mount_next) proposals for hop i -> i+1 (k = index of the hop inside its phrase)."""
        x, z = pos[i]; m = mount[i]; j = lambda lo, hi: float(rng.uniform(lo, hi))
        hreq = 0.5*g*dt*dt + a.vmin_up*dt + 0.08            # min floor->ceiling gap for this dt
        dtn = (T[i+2] - T[i+1]) if i + 2 < n else 9.0             # a ceiling contact must be left quickly (downward / glancing):
        can_ceil = (hreq <= a.row_max) and not hang[i+1] and dtn <= 0.47   # only when the NEXT gap is short too
        zf = st['zf']                                       # floor reference of this phrase
        out = []
        if pat == 'long_glide' or dt >= a.phrase_gap:
            dx = min(2.6, max(1.2, 1.9*dt)); out.append((dx*j(0.9, 1.1), -min(1.2, 0.35 + 0.6*dt)*j(0.8, 1.2) if z > zlo + 0.5 else j(-0.2, 0.1), 'floor'))
        elif pat == 'stair_down':
            out.append((j(0.72, 0.95) + 1.2*max(0, dt - 0.31), -j(0.18, 0.34), 'floor'))
        elif pat == 'stair_up':
            if m == 'floor' and can_ceil: out.append((j(0.45, 0.7), max(hreq, 0.0) + j(0.0, 0.12), 'ceil'))
            elif m == 'ceil': out.append((j(0.45, 0.7), -(hreq - j(0.25, 0.42)) if hreq > 0.45 else -j(0.1, 0.3), 'floor'))
            else: out.append((j(0.7, 0.9), min(0.5*g*dt*dt - a.vmin_dn*dt - 0.05, 0.4), 'floor'))
        elif pat == 'shuttle':
            gap = max(hreq, 0.8)
            if m == 'floor' and can_ceil: out.append((j(0.5, 0.75), zf + gap + j(-0.03, 0.08) - z, 'ceil'))
            else: out.append((j(0.5, 0.75), zf + j(-0.08, 0.06) - z, 'floor'))
        elif pat == 'zigzag_rev':                           # up-right onto the ceiling, bounce back left-down; floor-to-floor spacing
            gap = max(hreq, 1.0); ff = ext[i][1] - ext[min(i+2, n-1)][0] + 0.05      # stays >= the two strikers' footprint
            if m == 'floor' and can_ceil: st['back'] = j(0.4, 0.55); out.append((max(0.9, ff + st['back']), zf + gap - z + j(0.0, 0.08), 'ceil'))
            elif m == 'ceil': out.append((-st.get('back', 0.45), zf - 0.06 - z, 'floor'))
            else: out.append((j(0.8, 1.0), -j(0.15, 0.3), 'floor'))
        elif pat == 'cluster_spiral':                       # up-LEFT onto the ceiling, then far right-down: the marble circles
            gap = max(hreq, 1.0); ff = ext[max(i-1, 0)][1] - ext[i+1][0] + 0.05 if m == 'ceil' else 0.0
            if m == 'floor' and can_ceil: st['back'] = j(0.35, 0.5); out.append((-st['back'], zf + gap - z + j(0.0, 0.08), 'ceil'))
            elif m == 'ceil': out.append((max(0.9, st.get('back', 0.4) + (ext[i-1][1] - ext[i+1][0] + 0.05 if i > 0 else 0.7)), zf - 0.05 - z, 'floor'))
            else: out.append((j(0.8, 1.0), -j(0.1, 0.25), 'floor'))
        need = ext[i][1] - ext[i+1][0] + 0.05                 # same-row neighbours: footprint (wide vibraphone / pianos get room)
        out = [((max(dx_, need) if (mm_ == m and dx_ > 0) else dx_), dz_, mm_) for dx_, dz_, mm_ in out]
        # fallback grid (deterministic), ordered by closeness to the first proposal
        p0 = out[0]; grid = []
        for dx in (0.6, 0.8, 1.0, 1.25, 1.45, 1.6, 2.0, 2.5, -0.5, -0.8):
            for dz in (-1.6, -1.3, -1.0, -0.7, -0.45, -0.25, -0.1, 0.05, 0.2, 0.4, 0.7, 0.95, 1.15):
                for mm in ('floor', 'ceil'):
                    if mm == 'ceil' and not can_ceil: continue
                    grid.append((dx, dz, mm))
        grid.sort(key=lambda c: abs(c[0]-p0[0]) + 1.5*abs(c[1]-p0[1]) + (0.6 if c[2] != p0[2] else 0) + (0.8 if c[0] < 0 else 0))
        return out + grid[:90]
    def physics(i, dx, dz, mm, dt, lv=0):
        x, z = pos[i]; zn = z + dz
        zl_ = zlo - (0.25 if lv == 0 else 0.7); cm_ = cmin if lv < 2 else math.cos(math.radians(a.tilt_max + 8))
        if mm == 'floor' and not (zl_ <= zn <= zhi + 0.05): return None
        if mm == 'ceil' and not (zlo <= zn <= zhi + a.row_max): return None
        vx, vz = dx/dt, (dz + 0.5*g*dt*dt)/dt; ve = vz - g*dt
        if mm == 'floor' and ve > -a.vmin_dn: return None
        if mm == 'ceil' and ve < a.vmin_up: return None
        vo = np.array([vx, vz]); vi = vin[i]
        r_ = np.linalg.norm(vo)/np.linalg.norm(vi)
        if not ((a.kick_min if lv < 2 else 0.3) <= r_ <= (a.kick_max if lv < 2 else 3.2)): return None
        nn = unit(unit(vo) - unit(vi))
        if mount[i] == 'floor' and nn[1] < cm_: return None
        if mount[i] == 'ceil' and nn[1] > -cm_: return None
        if vz > 0 and ve < 0:
            apex = z + vz*vz/(2*g)
            lim = max(a.apex_max, 0.6*g*dt*dt/8 + 0.2) if lv == 0 else max(a.apex_max + (0.4 if lv == 2 else 0.0), g*dt*dt/8 + 0.1)
            if apex - max(z, zn) > lim: return None   # whole-note hand-off: <= 1.3 m (relax level 1: level lob 1.97 m; v1: 3.65 m)
            if apex > zhi + a.row_max + 0.3: return None
        return vx, vz, ve, nn
    def geom(i, nn, hop, t_next):
        c = np.array(pos[i]) - nn*(R + PT/2); W = world(i, c, nn)
        lo, hi = W.min(0), W.max(0)
        for j in range(i-1, -1, -1):                      # pairs vs placed strikers (spatially culled)
            s = strk[j]
            if s[5][0] > hi[0] + 0.1 or s[6][0] < lo[0] - 0.1 or s[5][2] > hi[2] + 0.1 or s[6][2] < lo[2] - 0.1: continue
            Wp = W[::2]                                   # pair test on a coarser subset (gap margin 3 cm >> spacing error)
            sel = (Wp[:, 0] > s[5][0] - 0.1) & (Wp[:, 0] < s[6][0] + 0.1) & (Wp[:, 2] > s[5][2] - 0.1) & (Wp[:, 2] < s[6][2] + 0.1)
            if not sel.any(): continue
            d, _ = s[3].query(Wp[sel], k=1, distance_upper_bound=0.15)
            if d.min() < a.pair_gap: GW[0] = f'pair{j}'; return None
        slab = W[np.abs(W[:, 1]) < R]; ts_ = cKDTree(slab) if len(slab) else None
        newp = hop_samples(*hop)
        near_ = [sm for sm in samples if sm[:, 1].min() < hi[0] + R and sm[:, 1].max() > lo[0] - R]
        allp = np.concatenate(near_ + [newp])           # previous path (spatially culled) + this hop vs the new striker
        if ts_ is not None:
            sel = (allp[:, 1] > lo[0] - R) & (allp[:, 1] < hi[0] + R) & (allp[:, 2] > lo[2] - R) & (allp[:, 2] < hi[2] + R) & (np.abs(allp[:, 0] - T[i]) >= 1.2/fps)
            if sel.any():
                d, _ = ts_.query(np.c_[allp[sel, 1], np.zeros(sel.sum()), allp[sel, 2]], k=1)
                if d.min() < 1.0*R: GW[0] = 'path_vs_new'; return None
        q = newp[np.abs(newp[:, 0] - t_next) >= 1.2/fps]    # this hop vs earlier strikers
        for j in range(i-1, -1, -1):
            s = strk[j]
            if s[4] is None: continue
            if s[5][0] > q[:, 1].max() + R or s[6][0] < q[:, 1].min() - R: continue
            qq = q[np.abs(q[:, 0] - T[j]) >= 1.2/fps]
            if not len(qq): continue
            d, _ = s[4].query(np.c_[qq[:, 1], np.zeros(len(qq)), qq[:, 2]], k=1)
            if d.min() < 1.0*R: GW[0] = f'hop_vs{j}'; return None
        return [c, nn, W, None, ts_, lo, hi]              # full-W tree built only for the accepted candidate
    WHY = {}; GW = ['']
    cand = [None]*n; ci = [0]*n; rl = [0]*n; st_of = [None]*n; ph_start_state = {}
    i = 0; backs = 0; forced = 0
    while i < n:
        last = (i == n-1)
        q = ph_id[i]
        if cand[i] is None:
            if q not in ph_start_state or phrases[q][0] == i:
                while len(ph_pat) <= q: ph_pat.append(None)
                if ph_pat[q] is None or phrases[q][0] == i: ph_pat[q] = draw(q, pos[i][1])
                ph_start_state[q] = dict(zf=pos[i][1] if mount[i] == 'floor' else pos[i][1] - 0.9)
            st = ph_start_state[q]
            dt = 0.5 if last else T[i+1] - T[i]
            k = i - phrases[q][0]
            if last: cl = [(d_, -0.6, 'floor') for d_ in (1.0, 1.4, 0.7, 1.8)] + [(d_, z_, 'floor') for d_ in (0.6, 1.0, 1.5, 2.0) for z_ in (-0.3, -1.0, 0.0)]
            else:
                pat = 'long_glide' if dt >= a.phrase_gap else ph_pat[q]
                cl = proposals(i, pat, k, dt, st)
            cand[i] = (cl, dt); ci[i] = 0; rl[i] = 0
        cl, dt = cand[i]; ok = None
        while True:
            if ci[i] >= len(cl):
                if rl[i] < 2 and not last: rl[i] += 1; ci[i] = 0; continue
                break
            dx, dz, mm = cl[ci[i]]; ci[i] += 1
            ph_ = physics(i, dx, dz, mm, dt, rl[i]) if not last else None
            if last:
                vx, vz = dx/dt, (dz + 0.5*g*dt*dt)/dt; vo = np.array([vx, vz]); nn = unit(unit(vo) - unit(vin[i]))
                if (mount[i] == 'floor' and nn[1] < cmin) or (mount[i] == 'ceil' and nn[1] > -cmin): continue
                ph_ = (vx, vz, vz - g*dt, nn)
            if ph_ is None: WHY['phys'] = WHY.get('phys', 0) + 1; continue
            vx, vz, ve, nn = ph_
            hop = (T[i], pos[i][0], pos[i][1], vx, vz, dt if not last else max(dt, dur - T[i] + 0.2))
            s = geom(i, nn, hop, T[i] + dt if not last else 1e9)
            if s is None: WHY['geom:' + GW[0]] = WHY.get('geom:' + GW[0], 0) + 1; continue
            ok = (dx, dz, mm, vx, vz, ve, nn, hop, s); break
        if ok is None:
            if os.environ.get('V2DBG'): print('fail at', i, 'pos', pos[i], mount[i], 'vin', vin[i], sorted(WHY.items(), key=lambda x: -x[1])[:6]); WHY.clear()
            if backs < a.backtrack*n and i > 0:
                cand[i] = None; i -= 1; backs += 1
                samples.pop(); strk[i] = None; hops[i] = None
                continue
            print('dead-end reasons', sorted(WHY.items(), key=lambda x: -x[1])[:12])
            raise SystemExit(f'v2 planner: dead end at hit {i} (t={T[i]:.2f}); try another --seed or relax --tilt-max/--apex-max')
        dx, dz, mm, vx, vz, ve, nn, hop, s = ok
        s[3] = cKDTree(s[2]); strk[i] = s; hops[i] = hop; samples.append(hop_samples(*hop)); pat_of[i] = ('end' if last else ('long_glide' if dt >= a.phrase_gap else ph_pat[q]))
        if not last:
            pos[i+1] = (pos[i][0] + dx, pos[i][1] + dz); mount[i+1] = mm; vin[i+1] = np.array([vx, ve]); cand[i+1] = None
        i += 1
    print(f'v2: {n} hits, {len(phrases)} phrases, backtracks {backs}, relaxed hops L1 {sum(1 for v in rl if v == 1)} L2 {sum(1 for v in rl if v == 2)}; patterns:', ' '.join(f'{phrases[q][0]}:{ph_pat[q]}' for q in range(len(phrases))))
    segs = [ent] + hops
    pads = [(strk[i][0], strk[i][1]) for i in range(n)]
    return pads, segs, [p[0] for p in pos], [p[1] for p in pos], mount, pat_of, [ph_pat[q] for q in range(len(phrases))], phrases, rl, [v > 1 for v in ci]
