"""Conclusive ending (v2): after the last hit the marble arcs onto a gold FINISH pad (END marker, held by a wall bracket),
hits it (impact SFX), hops toward the camera across the pad, rolls to a stop on its front-centre (lower-middle of frame) and
holds there (= the hand-off frame for image-to-video tools). Optional --subscribe: after settling, the marble lifts, glows
and bursts into 3D gold text (SUBSCRIBE / @handle), then holds.
Edits a copy of the plan (marble/camera lists are extended; 'marble_y' + 'ending' are added; scene.py builds pad / text from
P['ending'] via ending_pad.py) and writes the SFX cues to <out>.sfx.json (used by ending_sfx.py).
usage: python ending.py plan.json out_plan.json [--hold 0.5] [--subscribe [--line1 SUBSCRIBE --line2 @LucaMarbleMusic]]
  --land-after  seconds from the last hit to the pad contact     --pad-dx  pad centre x (world; 0 = screen centre)
  --pad-drop    pad top below the marble centre at the last hit  --cam-drop  camera eases this far down to frame the pad"""
import json, argparse, math
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('out')
ap.add_argument('--land-after', type=float, default=0.53); ap.add_argument('--hold', type=float, default=0.5, help='clean hold after the marble stops')
ap.add_argument('--pad-dx', type=float, default=0.0); ap.add_argument('--pad-drop', type=float, default=1.28)
ap.add_argument('--pad-r', type=float, default=0.50); ap.add_argument('--pad-h', type=float, default=0.22)
ap.add_argument('--pad-y', type=float, default=-0.26, help='pad centre y (wall face is at y=KD/2+0.12); leaves a gap the bracket spans')
ap.add_argument('--cam-drop', type=float, default=0.35); ap.add_argument('--cam-ease', type=float, default=0.8)
ap.add_argument('--rest-y', type=float, default=-0.52, help='marble rest y on the pad (toward the camera)')
ap.add_argument('--subscribe', action='store_true'); ap.add_argument('--line1', default='SUBSCRIBE'); ap.add_argument('--line2', default='@LucaMarbleMusic')
ap.add_argument('--sub-wait', type=float, default=0.3); ap.add_argument('--sub-rise', type=float, default=0.5); ap.add_argument('--sub-hold', type=float, default=1.1)
a = ap.parse_args()
P = json.load(open(a.plan)); fps = P['fps']; g = P['g']; R = P['R']; M = P['marble']; C = P['camera']
last = max(P['keys'], key=lambda k: k['t']); f0 = int(round(last['t'] * fps))
x0, z0 = M[f0]; T = a.land_after; fc = f0 + int(round(T * fps)); T = (fc - f0) / fps
pad_top = z0 - a.pad_drop; zc = pad_top + R + 0.006                # marble centre resting on the chequered inlay
px = a.pad_dx; vx = (px - x0) / T; vz = (zc - z0 + 0.5 * g * T * T) / T
M = M[:f0 + 1]; Y = [0.0] * (f0 + 1)
for f in range(f0 + 1, fc + 1):                                   # arc onto the (rear of the) pad
    t = (f - f0) / fps; M.append([x0 + vx * t, z0 + vz * t - 0.5 * g * t * t]); Y.append(0.0)
# hops toward the camera, then roll to a stop at rest-y; positions in (x, y, z) sampled per frame
vz_in = abs(vz - g * T); xr = px + 0.04                            # rest slightly right of pad centre = screen centre
hops = [(vz_in * 0.36,), (vz_in * 0.36 * 0.35,)]
ty = [];  t_c = [fc / fps]
for (v,) in hops: d = 2 * v / g; ty.append(d); t_c.append(t_c[-1] + d)
t_roll = 0.32; t_tot = sum(ty) + t_roll
def path(t):                                                      # t: seconds after first contact
    u = min(1.0, t / t_tot); s = 1 - (1 - u) ** 2.2                 # y/x progress with deceleration (friction)
    y = a.rest_y * s; x = px + (xr - px) * s; z = zc; acc = 0.0
    for (v,), d in zip(hops, ty):
        if acc <= t < acc + d: tt = t - acc; z = zc + v * tt - 0.5 * g * tt * tt
        acc += d
    return x, y, z
f_stop = fc + int(math.ceil(t_tot * fps)); f_hold_end = f_stop + int(round(a.hold * fps))
N = f_hold_end + 1; E = {}
if a.subscribe:
    f_m0 = f_hold_end - int(round(a.hold * fps)) + int(round(a.sub_wait * fps)); f_flash = f_m0 + int(round(a.sub_rise * fps))
    N = f_flash + 12 + int(round(a.sub_hold * fps)) + 1
    E['subscribe'] = {'frame_morph': f_m0, 'frame_flash': f_flash, 'line1': a.line1, 'line2': a.line2,
                      'screen': [0.5, 0.255], 'wall_gap': 0.3, 'width_frac': 0.80}
for f in range(fc + 1, N):
    x, y, z = path((f - fc) / fps); M.append([x, z]); Y.append(y)
# camera: ease (smoothstep) from where it is at the last hit down by cam-drop, then hold
cx0, cz0 = C[f0]; C = C[:f0 + 1]; fe = a.cam_ease * fps
for f in range(f0 + 1, N):
    u = min(1.0, (f - f0) / fe); s = u * u * (3 - 2 * u); C.append([cx0, cz0 - a.cam_drop * s])
P['marble'] = M; P['camera'] = C; P['marble_y'] = Y; P['duration'] = round(N / fps, 3); P['camera_hold_from'] = f0
E.update({'frame_last_hit': f0, 'frame_contact': fc, 'frames_hop': [int(round(t * fps)) for t in t_c[1:]], 'frame_stop': f_stop,
          'frame_hold_end': f_hold_end, 't_contact': fc / fps, 'rest': list(path(t_tot)),
          'pad': {'x': px, 'y': a.pad_y, 'z_top': pad_top, 'r': a.pad_r, 'h': a.pad_h}})
P['ending'] = E
sfx = {'contact': fc / fps, 'hops': [[t, 10 ** (-(9 + 8 * i) / 20)] for i, t in enumerate(t_c[1:])], 'v_impact': vz_in,
       'last_hit': last['t'], 'duration': N / fps}
if a.subscribe: sfx['whoosh'] = [E['subscribe']['frame_morph'] / fps, E['subscribe']['frame_flash'] / fps]; sfx['chime'] = E['subscribe']['frame_flash'] / fps
json.dump(P, open(a.out, 'w')); json.dump(sfx, open(a.out.rsplit('.', 1)[0] + '.sfx.json', 'w'), indent=1)
print(f"last hit f{f0} t={last['t']:.3f}s; contact f{fc} t={fc/fps:.3f}s (+{T:.2f}s); hops at {[round(t,3) for t in t_c[1:]]}s; stop f{f_stop}; "
      f"hold end f{f_hold_end} ({f_hold_end/fps:.2f}s); frames {N} ({N/fps:.2f}s)" + (f"; morph f{E['subscribe']['frame_morph']} flash f{E['subscribe']['frame_flash']}" if a.subscribe else ''))
