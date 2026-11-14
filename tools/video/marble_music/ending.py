"""Conclusive ending: after the last hit the marble arcs onto a gold FINISH pad (END marker), hits it (impact SFX cue), then
bounces off toward the camera and down out of the bottom-centre of the frame while the camera settles on the pad.
Edits a copy of the plan (marble/camera lists are extended; 'marble_y' + 'ending' are added; scene.py builds the pad from
P['ending']) and writes the SFX cue times to <out>.sfx.json (used by ending_sfx.py).
usage: python ending.py plan.json out_plan.json [--land-after 0.53] [--tail 2.1] [--pad-dx -0.1] [--pad-drop 1.28]
  --land-after  seconds from the last hit to the pad contact     --tail  seconds of video after the last hit (new length)
  --pad-dx      pad centre x (world; 0 = screen centre)      --pad-drop  pad top below the marble centre at the last hit
  --cam-drop    camera eases this far down to frame the pad      --restitution / --vy  bounce-off vertical factor / speed toward camera"""
import json, argparse, math
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('out')
ap.add_argument('--land-after', type=float, default=0.53); ap.add_argument('--tail', type=float, default=2.63)
ap.add_argument('--pad-dx', type=float, default=0.0); ap.add_argument('--pad-drop', type=float, default=1.28)
ap.add_argument('--pad-r', type=float, default=0.46); ap.add_argument('--pad-h', type=float, default=0.22)
ap.add_argument('--cam-drop', type=float, default=0.35); ap.add_argument('--cam-ease', type=float, default=0.8)
ap.add_argument('--restitution', type=float, default=0.55); ap.add_argument('--vy', type=float, default=-5.5)
a = ap.parse_args()
P = json.load(open(a.plan)); fps = P['fps']; g = P['g']; R = P['R']; M = P['marble']; C = P['camera']
last = max(P['keys'], key=lambda k: k['t']); f0 = int(round(last['t'] * fps))
x0, z0 = M[f0]; T = a.land_after; fc = f0 + int(round(T * fps)); T = (fc - f0) / fps
pad_top = z0 - a.pad_drop; zc = pad_top + R                     # marble centre on contact
px = a.pad_dx; vx = (px - x0) / T; vz = (zc - z0 + 0.5 * g * T * T) / T
N = f0 + int(round(a.tail * fps)) + 1                             # new frame count
M = M[:f0 + 1]; Y = [0.0] * (f0 + 1)
for f in range(f0 + 1, fc + 1):                                   # arc onto the pad
    t = (f - f0) / fps; M.append([x0 + vx * t, z0 + vz * t - 0.5 * g * t * t]); Y.append(0.0)
vz_in = vz - g * T; vz2 = -vz_in * a.restitution                  # bounce: up a little, toward the camera (-y), drift to screen centre
cam_x = 0.5                                                       # scene.py v2+ camera offset x (rig local)
vy = a.vy; vx2 = cam_x * (-vy) / 5.3 * 0.6
for f in range(fc + 1, N):
    t = (f - fc) / fps; z = zc + vz2 * t - 0.5 * g * t * t
    M.append([px + vx2 * t, max(z, zc - 30)]); Y.append(vy * t)
# camera: ease (smoothstep) from where it is at the last hit down by cam-drop, then hold
cx0, cz0 = C[f0]; C = C[:f0 + 1]; fe = a.cam_ease * fps
for f in range(f0 + 1, N):
    u = min(1.0, (f - f0) / fe); s = u * u * (3 - 2 * u); C.append([cx0, cz0 - a.cam_drop * s])
P['marble'] = M; P['camera'] = C; P['marble_y'] = Y; P['duration'] = round(N / fps, 3); P['camera_hold_from'] = f0
P['ending'] = {'frame_last_hit': f0, 'frame_contact': fc, 't_contact': fc / fps, 'pad': {'x': px, 'z_top': pad_top, 'r': a.pad_r, 'h': a.pad_h}}
# SFX cues: main clack at contact; faint second tick when the (off-screen) marble would land ~1.6 m lower
t2 = (vz2 + math.sqrt(vz2 * vz2 + 2 * g * 1.6)) / g
sfx = {'contact': fc / fps, 'bounce2': fc / fps + t2, 'v_impact': abs(vz_in), 'last_hit': last['t'], 'duration': N / fps}
json.dump(P, open(a.out, 'w')); json.dump(sfx, open(a.out.rsplit('.', 1)[0] + '.sfx.json', 'w'), indent=1)
print(f"last hit f{f0} t={last['t']:.3f}s; contact f{fc} t={fc/fps:.3f}s (+{T:.2f}s); impact v={abs(vz_in):.1f}; frames {N} ({N/fps:.2f}s); bounce2 {sfx['bounce2']:.3f}s; pad x={px} top={pad_top:.3f}")
