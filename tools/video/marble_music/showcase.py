"""Instrument showcase: a synthetic plan that shows each instrument on its own stretch of wall (3 strikers in the usual
zigzag, the middle one being hit by the marble), one rendered frame per instrument (camera held still for 3 frames around it so there is no motion blur),
for instrument sheets / close-ups. The frames to render are listed in plan['showcase_frames'] (= 3*i+1).
usage: python showcase.py out_plan.json "01. Acoustic Grand Piano" "02. Electric Grand Piano" ...   (track names, as in a MIDI)
       python showcase.py out_plan.json --set jewelbox:F1          (names from the instrument registry)
then:  blender -b -P scene.py -- --look v5 --plan out_plan.json --out frames/ --samples 12 --frames $(python showcase.py --frames out_plan.json)
       python showcase.py --sheet out_plan.json frames/ sheet.png [--closeups closeups.png]"""
import json, math, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, R, SPACING = 30, 0.15, 9.0
NOTES = [67, 66, 72]                                    # G (white), F# (black, the hit one), C (white): keyboards show both key shapes

def plan(names):
    keys, marble, camera = [], [], []
    for n, tr in enumerate(names):
        z0 = -n * SPACING
        for j, (side, dz) in enumerate([(-1, 0.0), (1, -0.85), (-1, -1.7)]):
            ang = 0.55 if side < 0 else -0.55; x = 0.68 * side
            t = (3 * n + 1) / FPS if j == 1 else -100.0               # only the middle key flashes on this instrument's frame
            keys.append(dict(i=len(keys), x=x, z=z0 + dz, nx=math.sin(ang), nz=math.cos(ang), ang=ang, tilt=math.degrees(abs(ang)),
                             t=t, t_audio=t, note=NOTES[j], track=tr, drum=False, side=side, cx=0.6 * side, cz=z0 + dz))
        k = keys[-2]; d = 0.045 + R
        for _ in range(3): marble.append([k['x'] + k['nx'] * d, k['z'] + k['nz'] * d]); camera.append([0.0, z0 - 0.5])
    return dict(fps=FPS, duration=len(names) / FPS, R=R, KW=0.62, KD=0.36, KH=0.09, g=30.0, layout='zigzag', keys=keys,
                marble=marble, camera=camera, showcase=names, showcase_frames=[3 * n + 1 for n in range(len(names))])

def sheet(plan_path, fd, out, closeups=None, cols=4, labels=None):
    from PIL import Image, ImageDraw, ImageFont
    P = json.load(open(plan_path)); names = P['showcase']; labels = labels or {}
    if not labels:                                   # default labels from the instrument registry: "NN Name" / "中文 · GM n · asset"
        sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments')); import registry
        for tr in names:
            e = registry.get_instrument(tr)
            if e: labels[tr] = (f"{e['num']:02d}  {e['en']}" if e['num'] else e['en'],
                                f"{e['zh']}  ·  GM {e['gm'] if e['gm'] is not None else '-'}  ·  {e['asset']}")
    try:
        FB = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 26, index=2)
        FR = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 18, index=2)
    except Exception: FB = FR = ImageFont.load_default()
    tw, th, hd = 360, 640, 70; rows = (len(names) + cols - 1) // cols
    S = Image.new('RGB', (cols * tw, rows * (th + hd)), (18, 18, 18)); d = ImageDraw.Draw(S); crops = []
    for i, tr in enumerate(names):
        p = f'{fd}/{P["showcase_frames"][i]:05d}.png'; x = (i % cols) * tw; y = (i // cols) * (th + hd)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB'); S.paste(im.resize((tw, th)), (x, y + hd))
            W, H = im.size; y0 = int(H * 0.04); c = im.crop((0, y0, W, y0 + int(W * 1.2))); crops.append((tr, c))   # full width x 1.2W: all three strikers + backdrops, nothing clipped
        l1, l2 = labels.get(tr, (tr, ''))
        while d.textlength(l1, font=FB) > tw - 16 and len(l1) > 4: l1 = l1[:-2] + '…' if not l1.endswith('…') else l1[:-2] + '…'
        d.text((x + 10, y + 6), l1, fill=(255, 255, 255), font=FB); d.text((x + 10, y + 42), l2, fill=(190, 190, 190), font=FR)
    S.save(out); print('saved', out)
    if closeups and crops:
        cw = 560; ch = int(cw * 1.2); rows = (len(crops) + cols - 1) // cols; C_ = Image.new('RGB', (cols * cw, rows * (ch + 44)), (18, 18, 18)); d = ImageDraw.Draw(C_)
        for i, (tr, c) in enumerate(crops):
            x = (i % cols) * cw; y = (i // cols) * (ch + 44); C_.paste(c.resize((cw, ch)), (x, y + 44)); d.text((x + 8, y + 6), labels.get(tr, (tr, ''))[0], fill=(255, 255, 255), font=FB)
        C_.save(closeups); print('saved', closeups)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--frames': print(','.join(map(str, json.load(open(a[1]))['showcase_frames']))); sys.exit()
    if a and a[0] == '--sheet':
        cl = a[a.index('--closeups') + 1] if '--closeups' in a else None
        lab = json.load(open(a[a.index('--labels') + 1])) if '--labels' in a else None
        sheet(a[1], a[2], a[3], cl, labels=lab); sys.exit()
    out = a[0]; names = a[1:]
    if names and names[0] == '--set':
        sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments')); import registry
        iset = names[1]; names = [e['track'] for e in registry.instrument_set(iset)]
        P = plan(names); P['instrument_set'] = iset
    else: P = plan(names)
    json.dump(P, open(out, 'w')); print('showcase plan', out, len(names), 'instruments')
