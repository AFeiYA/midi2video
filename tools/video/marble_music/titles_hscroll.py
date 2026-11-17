"""titles_hscroll.py - 16:9 overlay draft for the horizontal long-scroll layout (plan layout 'hscroll').
usage: python titles_hscroll.py PLAN.json OUT_DIR [--res 1920x1080] [--start F0 --end F1] [--still F --bg frame.png --png out.png]
       (also reachable as: titles.py PLAN.json OUT_DIR --layout hscroll; titles.py auto-delegates when the plan layout is hscroll)
Layout (1920x1080 reference, scaled to --res; everything inside the 5 % title-safe area x 96..1824, y 54..1026):
- lower third (default bottom-left; per instrument it moves to the safe-area corner that the projected strikers + marble cover
  least - bottom-left/right, top-left/right): translucent pill with the family-colour accent bar, big instrument number, Chinese name, English
  name and a small family chip. Slides in (+fade) over 0.35 s at each instrument change while the previous one fades out.
  v1 reserves the lower frame; v2 can use both rows, so placement minimizes projected overlap per instrument.
- family progress bar along the bottom: one segment per family (F1..F6 + finale) sized by its instrument count, a tick per
  instrument, filled up to the current point of the relay (interpolated inside the current instrument); current family label
  bright, others dim; a small marble dot rides the fill edge.
Names come from assets/instruments/registry.py (zh/en/family), so every jewelbox marker resolves without a NAMES table.
Writes OUT_DIR/%05d.png RGBA (same numbering as the Blender frames); composite with composite.sh."""
import json, os, sys, argparse
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'assets', 'instruments')); import registry
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('out', nargs='?', default='overlay_hs')
ap.add_argument('--res', default='1920x1080'); ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int, default=-1)
ap.add_argument('--first-delay', type=float, default=0.25); ap.add_argument('--fade', type=float, default=0.35)
ap.add_argument('--still', type=int, default=-1); ap.add_argument('--bg', default=''); ap.add_argument('--png', default='')
ap.add_argument('--layout', default='hscroll', help=argparse.SUPPRESS)
a = ap.parse_args()
P = json.load(open(a.plan)); fps = P['fps']; W, H = map(int, a.res.split('x')); S = W/1920
SYS = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
def font(bold, px):
    fn = SYS.format('Bold' if bold else 'Regular')
    if os.path.isfile(fn): return ImageFont.truetype(fn, int(px*S), index=2)
    return ImageFont.truetype(os.path.join(HERE, 'fonts', f"NotoSansSC-{'Bold' if bold else 'Regular'}-subset.otf"), int(px*S))
FB = {px: font(True, px) for px in (22, 26, 58, 66)}; FR = {px: font(False, px) for px in (22, 30)}
FAMC = {'F1': (238, 214, 160), 'F2': (236, 172, 104), 'F3': (236, 146, 168), 'F4': (244, 204, 92), 'F5': (146, 214, 166),
        'F6': (112, 184, 244), 'finale': (196, 156, 252)}
DB = registry.db(); FAMN = dict(DB['families']); FAMN['finale'] = {'zh': '终章', 'en': 'Finale'}
ENT = [e for e in registry.instrument_set(P.get('instrument_set') or 'jewelbox')]
FAMS = []
for e in sorted(ENT, key=lambda e: e['num']):
    f = e['family'] if e['family'] in FAMC else 'finale'
    if not FAMS or FAMS[-1][0] != f: FAMS.append([f, []])
    FAMS[-1][1].append(e['num'])
NTOT = sum(len(x[1]) for x in FAMS)
# bar geometry: segments proportional to instrument count, 10 px gaps
BX0, BX1, BY, BH, GAP = 96, 1824, 1004, 12, 10
usable = (BX1 - BX0) - GAP*(len(FAMS)-1); slot = usable/NTOT; SEG = []; x = BX0
for f, nums in FAMS:
    w = slot*len(nums); SEG.append((f, x, x + w, nums)); x += w + GAP
def bar_x(num, frac):
    for f, x0, x1, nums in SEG:
        if num in nums: return x0 + (nums.index(num) + frac)*slot
    return BX0
INST = P.get('instruments') or []
def entry(track):
    e = registry.resolve_track(track); return e
def inst_at(t):
    cur = None
    for q, it in enumerate(INST):
        t0 = max(it['t0'], a.first_delay) if it['t0'] < a.first_delay else it['t0']
        if t >= t0 - 1e-9: cur = q
    return cur
def frac_in(q, t):
    it = INST[q]; tn = INST[q+1]['t0'] if q + 1 < len(INST) else it['t1'] + (it['t1'] - it['t0'])/max(1, it['i1'] - it['i0'])
    return max(0.0, min(1.0, (t - it['t0'])/max(1e-6, tn - it['t0'])))
def rr(d, box, r, fill): d.rounded_rectangle([int(v*S) for v in box], radius=int(r*S), fill=fill)
# ---- lower-third placement: project strikers + marble with the plan camera and pick, per instrument, the safe-area corner they
#      cover least (bottom-left preferred; ties/near-ties keep the previous slot so the panel does not jump around)
import numpy as np
CR = P.get('cam_rig') or {'off': [0.0, -4.3, 0.8], 'aim': [0.0, 0.0, -0.35], 'lens': 40, 'sensor': 36}
def project(pts, f):
    cx, cz = P['camera'][min(f, len(P['camera'])-1)]
    C = np.array([cx + CR['off'][0], CR['off'][1], cz + CR['off'][2]]); A = np.array([cx + CR['aim'][0], CR['aim'][1], cz + CR['aim'][2]])
    fw = (A - C)/np.linalg.norm(A - C); rt = np.cross(fw, [0, 0, 1.0]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
    d = np.asarray(pts, float) - C; zc = d @ fw; k = CR.get('lens', 40)/CR.get('sensor', 36)*1080
    return np.c_[960 + (d @ rt)/zc*k, 540 - (d @ up)/zc*k]            # 1920x1080 reference pixels
KB = []
for k in P['keys']:
    nx, nz = k['nx'], k['nz']; tx, tz = nz, -nx; c = np.array([k['x'], k['z']])
    KB.append(np.array([[c[0] + s_*tx + h*nx, 0.0, c[1] + s_*tz + h*nz] for s_ in (-0.5, 0.5) for h in (-0.6, 0.2)]))
PANEL_H = 150
def slots(w):
    return {'bl': (96, 806, 96 + w, 956), 'br': (1824 - w, 806, 1824, 956), 'tl': (96, 64, 96 + w, 214), 'tr': (1824 - w, 64, 1824, 214)}
BIAS = {'bl': 0.0, 'br': 0.08, 'tl': 0.15, 'tr': 0.2}
_SLOT = {}
def panel_w(q):
    it = INST[q]; e = entry(it['track']) or {'zh': it['track'], 'en': '', 'family': 'F1'}
    d = ImageDraw.Draw(Image.new('L', (8, 8))); fam = e['family'] if e['family'] in FAMC else 'finale'
    return max(d.textlength(e['zh'], font=FB[58])/S, d.textlength(e['en'], font=FR[30])/S, d.textlength(fam + ' ' + FAMN[fam]['zh'], font=FB[22])/S + 20) + 250
def slot_of(q):
    if q in _SLOT: return _SLOT[q]
    it = INST[q]; f0 = int(it['t0']*fps); f1 = int((INST[q+1]['t0'] if q + 1 < len(INST) else P['duration'])*fps)
    w = panel_w(q); cost = {k_: 0.0 for k_ in slots(w)}; nfr = 0
    for f in range(max(0, f0), min(len(P['camera']) - 1, f1) + 1, 3):
        nfr += 1; mx, mz = P['marble'][f]; m = project([[mx, 0, mz]], f)[0]
        boxes = [(*m - 22, *m + 22, 3.0)]
        for kb in KB:
            pr = project(kb, f); lo, hi = pr.min(0), pr.max(0)
            if hi[0] < 0 or lo[0] > 1920 or hi[1] < 0 or lo[1] > 1080: continue
            boxes.append((lo[0], lo[1], hi[0], hi[1], 1.0))
        for k_, (x0, y0, x1, y1) in slots(w).items():
            ar = (x1 - x0)*(y1 - y0)
            for bx0, by0, bx1, by1, wt in boxes:
                ox = max(0, min(x1, bx1) - max(x0, bx0)); oy = max(0, min(y1, by1) - max(y0, by0)); cost[k_] += wt*ox*oy/ar
    best = min(cost, key=lambda k_: cost[k_]/max(1, nfr) + BIAS[k_])
    prev = _SLOT.get(q - 1)
    if prev and cost[prev]/max(1, nfr) + BIAS[prev] <= cost[best]/max(1, nfr) + BIAS[best] + 0.03: best = prev
    _SLOT[q] = best; print(f'lower third {q} ({it["track"][:24]}): {best}  cover ' + ' '.join(f'{k_}={cost[k_]/max(1,nfr):.2f}' for k_ in cost), flush=True)
    return best
def lower_third(img, q, alpha, dx):
    it = INST[q]; e = entry(it['track']) or {'num': it.get('num', 0), 'zh': it['track'], 'en': '', 'family': it.get('family', 'F1')}
    fam = e['family'] if e['family'] in FAMC else 'finale'; col = FAMC[fam]
    L = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    zh, en = e['zh'], e['en']; num = f"{e['num']:02d}" if e.get('num') else ''
    wz = d.textlength(zh, font=FB[58])/S; we = d.textlength(en, font=FR[30])/S
    fz = f"{fam if fam != 'finale' else ''} {FAMN[fam]['zh']}".strip(); wf = d.textlength(fz, font=FB[22])/S
    w = max(wz, we, wf + 20) + 250; sx0, sy0, _, _ = slots(w)[slot_of(q)]; x0, y0 = sx0 + dx, sy0
    rr(d, (x0, y0, x0 + w, y0 + 150), 22, (14, 14, 18, 150))
    rr(d, (x0, y0, x0 + 10, y0 + 150), 5, (*col, 255))
    d.text((int((x0 + 34)*S), int((y0 + 30)*S)), num, font=FB[66], fill=(*col, 255))
    tx = x0 + 160
    d.text((int(tx*S), int((y0 + 6)*S)), fz, font=FB[22], fill=(*col, 230))
    d.text((int(tx*S), int((y0 + 30)*S)), zh, font=FB[58], fill=(255, 255, 255, 255))
    d.text((int(tx*S), int((y0 + 100)*S)), en, font=FR[30], fill=(226, 226, 230, 235))
    if alpha < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v*alpha)))
    img.alpha_composite(L)
def progress(img, num, frac, fam_cur):
    d = ImageDraw.Draw(img); xf = bar_x(num, frac)
    for f, x0, x1, nums in SEG:
        col = FAMC[f]; cur = (f == fam_cur)
        rr(d, (x0, BY, x1, BY + BH), 6, (255, 255, 255, 70 if cur else 46))
        if xf > x0: rr(d, (x0, BY, min(x1, xf), BY + BH), 6, (*col, 240))
        for k in range(1, len(nums)):
            xt = x0 + k*slot; d.line([(int(xt*S), int((BY + 2)*S)), (int(xt*S), int((BY + BH - 2)*S))], fill=(20, 20, 24, 90), width=max(1, int(2*S)))
        lab = f"{f} {FAMN[f]['zh']}" if f != 'finale' else FAMN[f]['zh']
        fn = FB[22] if cur else FR[22]
        if d.textlength(lab, font=fn)/S > (x1 - x0) - 6: lab = f if f != 'finale' else '终'
        d.text((int((x0 + 2)*S), int((BY - 34)*S)), lab, font=fn, fill=(*col, 255) if cur else (235, 235, 240, 120))
    r = 10; cx, cy = xf, BY + BH/2
    d.ellipse([int((cx - r)*S), int((cy - r)*S), int((cx + r)*S), int((cy + r)*S)], fill=(40, 200, 110, 255), outline=(255, 255, 255, 220), width=max(1, int(2*S)))
def frame(f):
    t = f/fps; img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    q = inst_at(t)
    if q is None:
        it0 = INST[0] if INST else None
        if it0: progress(img, (entry(it0['track']) or {'num': 1})['num'], 0.0, it0.get('family'))
        return img
    it = INST[q]; t0 = max(it['t0'], a.first_delay); u = (t - t0)/a.fade
    e = entry(it['track']) or {'num': it.get('num', 1), 'family': it.get('family', 'F1')}
    progress(img, e['num'], frac_in(q, t), e['family'] if e['family'] in FAMC else 'finale')
    if q > 0 and u < 1:
        lower_third(img, q - 1, max(0.0, 1 - u/0.7), 0)
    ease = 1 - (1 - min(1.0, max(0.0, u)))**3
    lower_third(img, q, ease, -40*(1 - ease))
    return img
for _q in range(len(INST)): slot_of(_q)        # in order, so the 'keep previous slot' rule is the same for stills and sequences
if a.still >= 0:
    im = frame(a.still)
    if a.bg: bg = Image.open(a.bg).convert('RGBA').resize((W, H)); bg.alpha_composite(im); im = bg
    im.save(a.png or f'still_{a.still:05d}.png'); sys.exit(0)
os.makedirs(a.out, exist_ok=True)
end = a.end if a.end >= 0 else len(P['marble']) - 1
for f in range(a.start, end + 1): frame(f).save(os.path.join(a.out, f'{f:05d}.png'))
print('overlays', a.start, '..', end, '->', a.out)
