"""Ease the camera to a stop after the last hit so the closing frames keep the last strikers in view (the marble drops out of
frame) instead of following the marble down an empty wall.
usage: python hold_camera_end.py plan.json [--after 0.0] [--decay 0.6]   (edits the plan in place)"""
import json, argparse
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('--after', type=float, default=0.0, help='seconds after the last hit to start easing')
ap.add_argument('--decay', type=float, default=0.6, help='per-frame camera velocity factor while easing'); a = ap.parse_args()
P = json.load(open(a.plan)); fps = P['fps']; C = P['camera']
f0 = int(round((max(k['t'] for k in P['keys']) + a.after) * fps))
if 1 <= f0 < len(C) - 1:
    vx, vz = C[f0][0] - C[f0-1][0], C[f0][1] - C[f0-1][1]; x, z = C[f0]
    for f in range(f0 + 1, len(C)):
        vx *= a.decay; vz *= a.decay; x += vx; z += vz; C[f] = [x, z]
    P['camera_hold_from'] = f0
    json.dump(P, open(a.plan, 'w')); print('camera eased to a stop from frame', f0, 'final', [round(v, 3) for v in C[-1]])
else: print('nothing to do')
