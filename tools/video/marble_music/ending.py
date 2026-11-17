"""Conclusive ending (v2): after the last hit the marble arcs onto a gold FINISH pad (END marker, held by a wall bracket),
hits it (impact SFX), hops toward the camera across the pad, rolls to a stop on its front-centre (lower-middle of frame) and
holds there (= the hand-off frame for image-to-video tools). Optional --subscribe: the second contact becomes the LAST bounce -
the marble springs off the front of the pad and, while it falls, turns gold, bursts and morphs into 3D gold text
(SUBSCRIBE / @handle); the camera follows it down to a clean stretch of empty wall where the text lands and settles.
--subscribe-style rise (default, = ending v2) / fall (= ending v3).
Edits a copy of the plan (marble/camera lists are extended; 'marble_y' + 'ending' are added; scene.py builds pad / text from
P['ending'] via ending_pad.py) and writes the SFX cues to <out>.sfx.json (used by ending_sfx.py).
usage: python ending.py plan.json out_plan.json [--hold 0.5] [--subscribe [--line1 SUBSCRIBE --line2 @LucaMarbleMusic --font F.ttf --text-color '#9E610F']]
  --land-after  seconds from the last hit to the pad contact     --pad-dx  pad centre x (world; 0 = screen centre)
  --pad-drop    pad top below the marble centre at the last hit  --cam-drop  camera eases this far down to frame the pad"""
import json, argparse, math, os
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('out')
ap.add_argument('--land-after', type=float, default=0.53); ap.add_argument('--hold', type=float, default=0.5, help='clean hold after the marble stops')
ap.add_argument('--pad-dx', type=float, default=0.0); ap.add_argument('--pad-drop', type=float, default=1.28)
ap.add_argument('--pad-r', type=float, default=0.50); ap.add_argument('--pad-h', type=float, default=0.22)
ap.add_argument('--pad-y', type=float, default=-0.26, help='pad centre y (wall face is at y=KD/2+0.12); leaves a gap the bracket spans')
ap.add_argument('--cam-drop', type=float, default=0.35); ap.add_argument('--cam-ease', type=float, default=0.8)
ap.add_argument('--rest-y', type=float, default=-0.52, help='marble rest y on the pad (toward the camera)')
ap.add_argument('--subscribe', action='store_true')
ap.add_argument('--line1', default='SUBSCRIBE', help='subscribe text, line 1 (big)'); ap.add_argument('--line2', default='@LucaMarbleMusic', help="line 2 (smaller); '' = one line only (rise style)")
ap.add_argument('--line2-width', type=float, default=0.80, help='second line width as a fraction of the frame')
ap.add_argument('--font', default='', help='TTF/OTF for the 3D text (default Poppins ExtraBold, fallback DejaVu Sans Bold)')
ap.add_argument('--text-color', default='', help="text base colour as hex, e.g. '#9E610F' (default: v4 warm gold)")
ap.add_argument('--subscribe-style', choices=['rise', 'fall'], default='rise', help='rise (v2): settle + hold on the pad, then the marble lifts and bursts '
                'into the text above the pad; fall (v3): the 2nd contact is the last bounce, the marble falls off the pad and morphs into the text, '
                'camera follows down to empty wall')
ap.add_argument('--look', choices=['v2', 'v4'], default='v4', help='ending look: v4 (default) = gold marble glow, deeper gold text 0.15 m off the wall, refined bracket; v2 = ending v2 exactly')
ap.add_argument('--sub-wait', type=float, default=0.3, help='rise: pause after the hold'); ap.add_argument('--sub-rise', type=float, default=0.5, help='rise: lift time')
ap.add_argument('--sub-burst', type=float, default=0.40, help='s after the last bounce when the falling marble bursts into the text')
ap.add_argument('--sub-land', type=float, default=0.70, help='s from the burst until the text lands on the wall')
ap.add_argument('--sub-hold', type=float, default=None, help='hold on the text at the end (default 1.1 rise / 1.2 fall)'); ap.add_argument('--sub-cam', type=float, default=1.2, help='camera follow time')
ap.add_argument('--sub-cam-drop', type=float, default=5.3, help='camera drop below its pad framing (must clear pad + bracket)')
ap.add_argument('--sub-screen-y', type=float, default=0.42, help='text block centre, fraction of frame height from the top')
a = ap.parse_args()
if a.sub_hold is None: a.sub_hold = 1.1 if a.subscribe_style == 'rise' else 1.2
FALL = a.subscribe and a.subscribe_style == 'fall'
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
cx0, cz0 = C[f0]; C = C[:f0 + 1]; fe = a.cam_ease * fps
def cam_pad(f):                                                   # ease (smoothstep) down by cam-drop from the last hit, then hold
    u = min(1.0, (f - f0) / fe); s = u * u * (3 - 2 * u); return [cx0, cz0 - a.cam_drop * s]
if not FALL:
    if a.subscribe:                                               # v2 'rise' morph (frames/timings exactly as ending v2)
        f_m0 = f_hold_end - int(round(a.hold * fps)) + int(round(a.sub_wait * fps)); f_flash = f_m0 + int(round(a.sub_rise * fps))
        N = f_flash + 12 + int(round(a.sub_hold * fps)) + 1
        E['subscribe'] = {'style': 'rise', 'frame_morph': f_m0, 'frame_flash': f_flash, 'line1': a.line1, 'line2': a.line2,
                          'screen': [0.5, 0.255], 'wall_gap': 0.3 if a.look == 'v2' else 0.15, 'width_frac': a.line2_width}
    for f in range(fc + 1, N):
        x, y, z = path((f - fc) / fps); M.append([x, z]); Y.append(y)
    for f in range(f0 + 1, N): C.append(cam_pad(f))
else:
    # hop 1 as above, then the LAST bounce at the 2nd contact: spring off the front edge and fall past the pad
    f_lb = int(round(t_c[1] * fps)); tl = (f_lb - fc) / fps
    xl, yl, zl = path(tl); zl = zc; vyb, vzb = -2.6, 2.8; vxb = (xr - xl) * 1.5
    f_b = f_lb + int(round(a.sub_burst * fps)); f_land = f_b + int(round(a.sub_land * fps))
    f_cam = f_lb + int(round(a.sub_cam * fps)); N = f_land + 10 + int(round(a.sub_hold * fps)) + 1
    for f in range(fc + 1, f_lb + 1):
        x, y, z = path((f - fc) / fps); M.append([x, z]); Y.append(y)
    def ball(t): return [xl + vxb * t, yl + vyb * t, zl + vzb * t - 0.5 * g * t * t]
    for f in range(f_lb + 1, N):
        t = min((f - f_lb) / fps, (f_b + 3 - f_lb) / fps); b = ball(t); M.append([b[0], b[2]]); Y.append(b[1])   # hidden after the burst
    for f in range(f0 + 1, f_lb + 1): C.append(cam_pad(f))
    ca = cam_pad(f_lb); ct = [ca[0], cz0 - a.cam_drop - a.sub_cam_drop]
    for f in range(f_lb + 1, N):                                  # follow the falling marble down to empty wall
        u = min(1.0, (f - f_lb) / (f_cam - f_lb)); s = u * u * u * (u * (6 * u - 15) + 10); C.append([ca[0], ca[1] + (ct[1] - ca[1]) * s])
    # text block landing point on the wall at the final camera (scene.py v2+ rig: offset (0.5,-5.3,1.0), aim (0,0,-0.9), lens 40, sensor 36 vertical)
    def sub(u_, v_): return [u_[i] - v_[i] for i in range(3)]
    def nrm(v_): l_ = math.sqrt(sum(c * c for c in v_)); return [c / l_ for c in v_]
    def crs(u_, v_): return [u_[1]*v_[2]-u_[2]*v_[1], u_[2]*v_[0]-u_[0]*v_[2], u_[0]*v_[1]-u_[1]*v_[0]]
    off = [0.5, -5.3, 1.0]; fw = nrm(sub([0, 0, -0.9], off)); rt = nrm(crs(fw, [0, 0, 1])); up = crs(rt, fw)
    tv = 18.0 / 40.0; th = tv * 9 / 16; cam = [ct[0] + off[0], off[1], ct[1] + off[2]]
    ray = [fw[i] + (0.5 - a.sub_screen_y) * 2 * tv * up[i] for i in range(3)]; wall_y = P['KD'] / 2 + 0.12
    D = (wall_y - 0.15 - cam[1]) / ray[1]; Pc = [cam[i] + D * ray[i] for i in range(3)]
    B = ball((f_b - f_lb) / fps); vB = [vxb, vyb, vzb - g * (f_b - f_lb) / fps]; Tm = (f_land - f_b) / fps
    v1 = [0, 0, -2.0]; tpath = {}
    for f in range(f_b, N):                                       # Hermite fall into place (still moving down on arrival) + damped settle
        t = (f - f_b) / fps
        if t <= Tm:
            u = t / Tm; h00, h10, h01, h11 = 2*u**3 - 3*u**2 + 1, u**3 - 2*u**2 + u, -2*u**3 + 3*u**2, u**3 - u**2
            p = [h00 * B[i] + h10 * Tm * vB[i] * 0.45 + h01 * Pc[i] + h11 * Tm * v1[i] for i in range(3)]
        else:
            tt = t - Tm; w = 2 * math.pi * 3.2; p = [Pc[0], Pc[1], Pc[2] + (v1[2] / w) * math.exp(-7 * tt) * math.sin(w * tt)]
        tpath[f] = p
    E['subscribe'] = {'style': 'fall', 'frame_release': f_lb, 'frame_burst': f_b, 'frame_land': f_land, 'line1': a.line1, 'line2': a.line2,
                      'center': Pc, 'D': D, 'full_w': 2 * D * th, 'width_frac': a.line2_width, 'path': {str(k): v for k, v in tpath.items()}}
    E['frame_release'] = f_lb; hops = hops[:1]; f_stop = f_hold_end = None
P['marble'] = M; P['camera'] = C; P['marble_y'] = Y; P['duration'] = round(N / fps, 3); P['camera_hold_from'] = f0
E.update({'frame_last_hit': f0, 'frame_contact': fc, 'frames_hop': [int(round(t * fps)) for t in t_c[1:len(hops) + 1]], 'frame_stop': f_stop,
          'frame_hold_end': f_hold_end, 't_contact': fc / fps, 'rest': list(path(t_tot)),
          'pad': {'x': px, 'y': a.pad_y, 'z_top': pad_top, 'r': a.pad_r, 'h': a.pad_h}})
if a.look != 'v2': E['look'] = a.look
if a.subscribe and a.font: E['subscribe']['font'] = os.path.abspath(a.font)
if a.subscribe and a.text_color:
    h_ = a.text_color.lstrip('#'); E['subscribe']['color'] = [(int(h_[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4)]   # sRGB hex -> linear
P['ending'] = E
sfx = {'contact': fc / fps, 'hops': [[t, 10 ** (-(9 + 8 * i) / 20)] for i, t in enumerate(t_c[1:len(hops) + 1])], 'v_impact': vz_in,
       'last_hit': last['t'], 'duration': N / fps}
if a.subscribe and not FALL: sfx['whoosh'] = [E['subscribe']['frame_morph'] / fps, E['subscribe']['frame_flash'] / fps]; sfx['chime'] = E['subscribe']['frame_flash'] / fps
if FALL:
    S_ = E['subscribe']; sfx['whoosh'] = [S_['frame_release'] / fps, S_['frame_burst'] / fps]; sfx['chime'] = S_['frame_burst'] / fps; sfx['settle'] = S_['frame_land'] / fps
json.dump(P, open(a.out, 'w')); json.dump(sfx, open(a.out.rsplit('.', 1)[0] + '.sfx.json', 'w'), indent=1)
print(f"last hit f{f0} t={last['t']:.3f}s; contact f{fc} t={fc/fps:.3f}s (+{T:.2f}s); hops at {sfx['hops']}; stop f{f_stop}; hold end f{f_hold_end}; frames {N} ({N/fps:.2f}s)"
      + (f"; last bounce f{E['subscribe']['frame_release']} burst f{E['subscribe']['frame_burst']} land f{E['subscribe']['frame_land']}" if FALL else '')
      + (f"; morph f{E['subscribe']['frame_morph']} flash f{E['subscribe']['frame_flash']}" if a.subscribe and not FALL else ''))
