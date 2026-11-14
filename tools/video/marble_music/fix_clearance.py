"""Plan + 3D clearance fixer: replans with plan_zigzag.py and adds a little extra drop to the segments between two strikers
that come too close (check_pairs.py) or between a striker and the hit the marble is heading for when it grazes that striker
(check_keepout.py), until both --strict checks pass.  Needed when a MIDI puts big silhouettes (flute, glockenspiel, steel drums,
kalimba) on fast runs, e.g. the 6-instrument 16-beat remix.  Instrument changes need nothing special: the checks are per key.
usage: python fix_clearance.py hits.json -o plan_zz_v2.json [--look v5] [--fps 30] [--frame-margin 0.8] [--step 0.05] [--iters 40]
writes <plan>.extra_drop.json next to the plan (pass it to plan_zigzag.py --extra-drop to reproduce)."""
import argparse, json, os, subprocess, sys, bisect
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
ap = argparse.ArgumentParser(); ap.add_argument('hits'); ap.add_argument('-o', required=True); ap.add_argument('--look', default='v5')
ap.add_argument('--fps', default='30'); ap.add_argument('--frame-margin', default='0.8'); ap.add_argument('--step', type=float, default=0.05)
ap.add_argument('--iters', type=int, default=40); a = ap.parse_args()
base = os.path.splitext(a.o)[0]; EX = base + '.extra_drop.json'; KO = base + '.keepout.json'; PR = base + '.pairs.json'
os.makedirs(os.path.dirname(os.path.abspath(a.o)), exist_ok=True); extra = {}
for it in range(a.iters + 1):
    json.dump({str(k): round(v, 4) for k, v in sorted(extra.items())}, open(EX, 'w'), indent=1)
    subprocess.run([PY, os.path.join(HERE, 'plan_zigzag.py'), a.hits, '--fps', a.fps, '--frame-margin', a.frame_margin, '--extra-drop', EX, '-o', a.o], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([PY, os.path.join(HERE, 'check_keepout.py'), a.o, '--look', a.look, '--out', KO], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([PY, os.path.join(HERE, 'check_pairs.py'), a.o, '--look', a.look, '--out', PR], check=True, stdout=subprocess.DEVNULL)
    P = json.load(open(a.o)); fr = [k['t']*P['fps'] for k in P['keys']]
    viol = json.load(open(KO))['violations']; cl = json.load(open(PR))['clashes']
    print(f'iter {it}: keep-out violations {len(viol)}, striker clashes {len(cl)}, extra-drop segments {len(extra)} (total {sum(extra.values()):.2f} m)', flush=True)
    if not viol and not cl: print('clean ->', a.o, '| extra drops:', EX); sys.exit(0)
    bump = set()
    for v in viol:                       # marble grazes key v['key'] on its way to hit m: open up the gap between them
        k = v['key']; m = bisect.bisect_right(fr, v['frame']) - 1
        lo, hi = (k, m) if m > k else (m, k)
        bump.update(range(lo, max(hi, lo+1)))
    for c in cl:                         # two strikers touch: push the later one down
        i, j = sorted((c[1], c[3])); bump.update(range(i, j))
    for i in bump: extra[i] = extra.get(i, 0.0) + a.step
print('not clean after', a.iters, 'iterations'); sys.exit(1)
