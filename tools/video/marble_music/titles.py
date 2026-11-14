"""titles.py - v5 instrument corner-label overlay (compositing pass, no re-render needed for label tweaks).
usage: python titles.py PLAN.json OUT_DIR [--start F0 --end F1] [--res 1080x1920] [--cards] [--no-corner] [--still FRAME --bg render.png --png out.png]
Sections = contiguous runs of one melody track (instrument resolved by track name), so remixed MIDIs where instruments rotate and repeat (e.g. 6 instruments every 16 beats) get one label per run.
Default: only the small top-left label ("01 响板 Castanets", opacity 0.8), shown from the first hit of each section; it fades in over
--label-fade (0.3 s) and cross-fades from the previous section's label at each change. A section starting at t=0 starts at
--first-delay (0.2 s) so nothing pops in on frame 0 (fully visible by 0.5 s).
--cards (opt-in) restores the big per-section title card (label then appears as the card leaves; first-delay 0.4 s).
Writes OUT_DIR/%05d.png RGBA overlays (same numbering as the Blender frames) - identical overlay states are hard-linked, so a full-song
pass is cheap.  Composite with composite.sh (ffmpeg overlay).
Layout (9:16, YouTube-Shorts safe): everything sits in x in [28, 900] (keeps clear of the right-side action buttons, ~15 %),
y in [214, 1536] (below the top ~10 % = 192 px status/search bar, above the bottom ~20 % caption / channel area).
Title card (--cards only; 80 % size, translucent): --place auto (default) projects every striker and the marble with the scene camera for the
frames each card is up and picks ONE safe-area spot that they occupy least (for Jingle Bells: lower-left, y=1342 -> 65-75 % less
overlap than the top); --place section = best spot per section, --place top = fixed top-left.  Fades in 0.3 s at the section's first
hit (the opening card waits --first-delay 0.4 s so it does not pop in on frame 0), holds 1.6 s, fades out 0.4 s.  Corner label: small
pill "05 马林巴 Marimba" top-left at 0.8 opacity whenever no title card is showing (viewers who join mid-section / Shorts loops still
know the instrument).
Font: Noto Sans CJK SC, SIL Open Font License 1.1 - bundled glyph subset fonts/NotoSansSC-{Bold,Regular}-subset.otf (fonts/OFL.txt,
regenerate with fonts/make_subset.sh after adding names), else /usr/share/fonts/opentype/noto/NotoSansCJK-*.ttc index 2 = SC.
All icons are drawn procedurally here with PIL primitives - no third-party images."""
import json, os, re, sys, argparse, math, colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument('plan'); ap.add_argument('out', nargs='?', default='overlay')
ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int, default=-1); ap.add_argument('--res', default='1080x1920')
ap.add_argument('--no-corner', action='store_true'); ap.add_argument('--place', default='auto', choices=['auto', 'section', 'top'], help='auto: ONE safe-area spot for all sections that strikers/marble occupy least while cards are up; section: best spot per section; top: fixed top-left')
ap.add_argument('--cards', action='store_true', help='opt-in: also show the big title card at each section start (default: corner label only)')
ap.add_argument('--card-scale', type=float, default=0.8); ap.add_argument('--card-alpha', type=int, default=150)
ap.add_argument('--first-delay', type=float, default=None, help='a section starting at t<delay starts its label/card at t=delay (no pop-in on frame 0); default 0.2 s for labels, 0.4 s with --cards')
ap.add_argument('--label-fade', type=float, default=0.3, help='corner label fade-in / cross-fade time at section changes (s)')
ap.add_argument('--still', type=int, default=-1); ap.add_argument('--bg', default='')
ap.add_argument('--png', default='', help='with --still: output composite png')
_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
def _dflt(w):   # bundled OFL subset first (portable, e.g. on the Mac), else the system Noto Sans CJK TTC (index 2 = SC)
    b = os.path.join(_FD, f'NotoSansSC-{w}-subset.otf')
    return b if os.path.isfile(b) else f'/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc'
ap.add_argument('--font-bold', default=_dflt('Bold')); ap.add_argument('--font-regular', default=_dflt('Regular'))
ap.add_argument('--font-index', type=int, default=2, help='face index inside a .ttc (2 = SC in Noto Sans CJK); ignored for .otf')
a = ap.parse_args()
if a.first_delay is None: a.first_delay = 0.4 if a.cards else 0.2
W, H = map(int, a.res.split('x')); S = W / 1080.0          # all layout numbers below are for 1080x1920
FIN, HOLD, FOUT = 0.3, 1.6, 0.4
NAMES = {   # section no -> (zh, en, accent rgb)
 1: ('响板', 'Castanets', (196, 92, 52)),   2: ('钢琴', 'Piano', (236, 228, 210)),     3: ('颤音琴', 'Vibraphone', (170, 190, 220)),
 4: ('管钟', 'Tubular Bells', (232, 176, 80)), 5: ('马林巴', 'Marimba', (200, 120, 60)), 6: ('卡林巴', 'Kalimba', (190, 196, 206)),
 7: ('长笛', 'Flute', (214, 220, 230)),      8: ('木琴', 'Xylophone', (240, 120, 90)),  9: ('陶笛', 'Ocarina', (70, 170, 130)),
 10: ('钟琴', 'Glockenspiel', (220, 60, 60)), 11: ('钢鼓', 'Steel Drums', (200, 205, 215)), 12: ('吉他', 'Guitar', (226, 150, 60)),
 # hook50 (50 s Shorts hook cut) instruments
 13: ('管钟+响板', 'Tubular Bells & Castanets', (232, 176, 80)), 14: ('八音盒', 'Music Box', (220, 70, 80)), 15: ('古筝', 'Koto', (200, 110, 60)),
 16: ('8-bit 方波', '8-Bit Square Lead', (70, 225, 240)), 17: ('风笛', 'Bagpipe', (210, 50, 55)), 18: ('齐奏终章', 'Grand Tutti Finale', (255, 205, 90))}

def font(bold, px):
    fn = a.font_bold if bold else a.font_regular
    return ImageFont.truetype(fn, int(px*S), index=a.font_index if fn.lower().endswith('.ttc') else 0)

# ------------------------------------------------------------------ procedural icons (drawn at 4x in a unit box, then downsampled)
def rainbow(i, n): r, g, b = colorsys.hsv_to_rgb(i/n, 0.7, 0.95); return (int(r*255), int(g*255), int(b*255), 255)
PH = [0.0, 0.08, 0.15, 0.33, 0.5, 0.62, 0.77]   # same pitch-class hues as assets/instruments/_common.PITCH_HUE (C..B)
def ph(i): r, g, b = colorsys.hsv_to_rgb(PH[i % 7], 0.72, 0.95); return (int(r*255), int(g*255), int(b*255), 255)
def icon(sec, px):
    N = px*4; im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(x, y): return (x*N, y*N)
    def R(x0, y0, x1, y1, fill, r=0.0, outline=None, w=0): d.rounded_rectangle([x0*N, y0*N, x1*N, y1*N], radius=r*N, fill=fill, outline=outline, width=int(w*N))
    def E(cx, cy, rx, ry, fill, outline=None, w=0): d.ellipse([(cx-rx)*N, (cy-ry)*N, (cx+rx)*N, (cy+ry)*N], fill=fill, outline=outline, width=int(w*N))
    def L(pts, fill, w): d.line([P(*p) for p in pts], fill=fill, width=int(w*N), joint='curve')
    WHITE = (245, 240, 228, 255); DARK = (25, 22, 20, 255); GOLD = (232, 176, 80, 255); STEEL = (200, 206, 216, 255); WOOD = (160, 96, 48, 255)
    if sec == 1:      # castanets: two shells + cord
        E(0.40, 0.56, 0.25, 0.25, (120, 50, 25, 255), outline=(60, 20, 10, 255), w=0.02); E(0.60, 0.50, 0.25, 0.25, (176, 82, 40, 255), outline=(70, 25, 12, 255), w=0.02)
        E(0.60, 0.50, 0.10, 0.10, (150, 66, 30, 255)); d.arc([0.30*N, 0.06*N, 0.62*N, 0.40*N], 180, 360, fill=(220, 40, 40, 255), width=int(0.035*N))
    elif sec == 2:    # piano keyboard
        R(0.08, 0.25, 0.92, 0.80, DARK, r=0.04)
        for i in range(7): R(0.11+i*0.115, 0.28, 0.215+i*0.115, 0.77, WHITE, r=0.015)
        for i in (0, 1, 3, 4, 5): R(0.19+i*0.115, 0.28, 0.25+i*0.115, 0.56, DARK, r=0.01)
    elif sec in (3, 5, 8):   # mallet bars: vibraphone (metal + tubes), marimba (wood + long resonators), xylophone (rainbow + mallets)
        n = 6
        for i in range(n):
            x = 0.12 + i*0.13; L_ = 0.50 - i*0.05; y0 = 0.18 + i*0.025
            col = STEEL if sec == 3 else (WOOD if sec == 5 else ph(i))
            if sec != 8: R(x+0.025, y0+L_*0.55, x+0.075, y0+L_*0.55 + (0.28 if sec == 5 else 0.18) - i*0.02, GOLD if sec == 3 else (90, 90, 96, 255), r=0.02)
            R(x, y0, x+0.10, y0+L_*0.6, col, r=0.02, outline=(40, 30, 25, 255), w=0.008)
        if sec == 8:
            L([(0.22, 0.95), (0.42, 0.62)], WHITE, 0.025); E(0.42, 0.60, 0.05, 0.05, (220, 60, 60, 255))
            L([(0.82, 0.95), (0.62, 0.62)], WHITE, 0.025); E(0.62, 0.60, 0.05, 0.05, (220, 60, 60, 255))
    elif sec == 4:    # tubular bells: frame + graded hanging tubes
        R(0.08, 0.08, 0.92, 0.14, (110, 80, 40, 255), r=0.02)
        for i in range(6):
            x = 0.14 + i*0.125; L_ = 0.78 - i*0.08
            L([(x+0.035, 0.14), (x+0.035, 0.18)], (80, 70, 60, 255), 0.01)
            R(x, 0.18, x+0.07, 0.18+L_, GOLD, r=0.02, outline=(120, 80, 30, 255), w=0.008); R(x-0.008, 0.18, x+0.078, 0.22, (200, 140, 50, 255), r=0.01)
    elif sec == 6:    # kalimba: rounded board + fan of tines
        R(0.12, 0.12, 0.88, 0.90, (130, 76, 36, 255), r=0.16); E(0.50, 0.75, 0.07, 0.07, DARK)
        R(0.14, 0.30, 0.86, 0.36, STEEL, r=0.02)
        n = 9
        for i in range(n):
            x = 0.20 + i*0.075; L_ = 0.42 - 0.26*abs(i-(n-1)/2)/((n-1)/2)
            R(x-0.018, 0.14, x+0.018, 0.14+L_, (225, 230, 238, 255), r=0.015)
    elif sec == 7:    # flute: long diagonal tube with keys
        L([(0.08, 0.82), (0.92, 0.18)], STEEL, 0.085); L([(0.08, 0.82), (0.92, 0.18)], (230, 234, 240, 255), 0.03)
        for i in range(6):
            t = 0.32 + i*0.09; E(0.08+0.84*t, 0.82-0.64*t, 0.035, 0.035, GOLD, outline=(110, 80, 30, 255), w=0.008)
        E(0.08+0.84*0.12, 0.82-0.64*0.12, 0.045, 0.028, (160, 166, 176, 255)); E(0.08+0.84*0.12, 0.82-0.64*0.12, 0.018, 0.012, DARK)
    elif sec == 9:    # ocarina: sweet-potato with mouthpiece + holes
        d.polygon([P(0.66, 0.40), P(0.94, 0.36), P(0.95, 0.50), P(0.68, 0.56)], fill=(50, 140, 105, 255))
        E(0.46, 0.55, 0.36, 0.26, (60, 160, 120, 255), outline=(30, 90, 65, 255), w=0.015)
        for x, y in ((0.26, 0.50), (0.38, 0.45), (0.50, 0.45), (0.62, 0.50)): E(x, y, 0.04, 0.04, (12, 24, 18, 255))
        R(0.70, 0.40, 0.76, 0.46, (12, 24, 18, 255), r=0.01)
    elif sec == 10:   # glockenspiel: red case + graded steel bars
        d.polygon([P(0.06, 0.14), P(0.94, 0.14), P(0.80, 0.88), P(0.20, 0.88)], fill=(200, 30, 30, 255))
        for i in range(6):
            y = 0.20 + i*0.11; hw = 0.38 - i*0.045
            R(0.5-hw, y, 0.5+hw, y+0.075, STEEL, r=0.015, outline=(90, 95, 105, 255), w=0.006)
            E(0.5-hw+0.04, y+0.037, 0.013, 0.013, GOLD); E(0.5+hw-0.04, y+0.037, 0.013, 0.013, GOLD)
    elif sec == 11:   # steel pan face-on
        E(0.5, 0.52, 0.42, 0.42, (150, 156, 168, 255)); E(0.5, 0.52, 0.37, 0.37, (205, 210, 220, 255), outline=(90, 95, 105, 255), w=0.012)
        E(0.5, 0.52, 0.11, 0.09, (230, 234, 240, 255), outline=(70, 75, 85, 255), w=0.01)
        for k in range(6):
            t = k*math.pi/3 + 0.3; E(0.5+0.24*math.cos(t), 0.52+0.22*math.sin(t), 0.075, 0.06, (232, 236, 242, 255), outline=(70, 75, 85, 255), w=0.01)
    elif sec == 12:   # acoustic guitar
        R(0.42, 0.06, 0.58, 0.18, (70, 40, 20, 255), r=0.03); R(0.46, 0.16, 0.54, 0.50, (60, 34, 18, 255))
        for i in range(5): L([(0.46, 0.22+i*0.055), (0.54, 0.22+i*0.055)], (220, 220, 210, 255), 0.006)
        E(0.50, 0.73, 0.25, 0.22, (210, 130, 50, 255)); E(0.50, 0.49, 0.18, 0.16, (210, 130, 50, 255)); R(0.36, 0.54, 0.64, 0.68, (210, 130, 50, 255))
        E(0.50, 0.73, 0.25, 0.22, None, outline=(80, 36, 12, 255), w=0.02); E(0.50, 0.49, 0.18, 0.16, None, outline=(80, 36, 12, 255), w=0.02)
        R(0.37, 0.55, 0.63, 0.67, (210, 130, 50, 255)); E(0.50, 0.57, 0.075, 0.075, (30, 16, 8, 255), outline=(240, 220, 180, 255), w=0.012)
        R(0.40, 0.80, 0.60, 0.84, (50, 26, 12, 255), r=0.01)
        for x in (0.47, 0.49, 0.51, 0.53): L([(x, 0.16), (x, 0.82)], (235, 235, 225, 220), 0.004)
    elif sec == 13:   # tubular bells + castanets: brass rail, graded tubes, castanet pair
        R(0.06, 0.08, 0.70, 0.14, (110, 80, 40, 255), r=0.02)
        for i in range(5):
            x = 0.10 + i*0.12; L_ = 0.72 - i*0.09
            R(x, 0.16, x+0.07, 0.16+L_, GOLD, r=0.02, outline=(120, 80, 30, 255), w=0.008); R(x-0.008, 0.16, x+0.078, 0.20, (200, 140, 50, 255), r=0.01)
        E(0.78, 0.66, 0.15, 0.15, (120, 50, 25, 255), outline=(60, 20, 10, 255), w=0.02); E(0.84, 0.60, 0.15, 0.15, (176, 82, 40, 255), outline=(70, 25, 12, 255), w=0.02)
        L([(0.70, 0.12), (0.80, 0.45)], (220, 40, 40, 255), 0.025)
    elif sec == 14:   # music box: open red-velvet lid, walnut box, brass comb, winding key
        R(0.10, 0.10, 0.86, 0.46, (110, 55, 28, 255), r=0.03); R(0.15, 0.14, 0.81, 0.42, (190, 25, 40, 255), r=0.02)
        R(0.10, 0.52, 0.86, 0.90, (120, 62, 30, 255), r=0.04, outline=(70, 35, 15, 255), w=0.012)
        R(0.16, 0.46, 0.80, 0.53, GOLD, r=0.01)
        for i in range(10): R(0.18+i*0.062, 0.53, 0.205+i*0.062, 0.60-i*0.004, GOLD)
        E(0.48, 0.74, 0.03, 0.03, (40, 25, 10, 255)); E(0.93, 0.62, 0.05, 0.05, None, outline=GOLD, w=0.02)
    elif sec == 15:   # koto: long dark board, strings, diagonal ivory bridges
        d.polygon([P(0.06, 0.78), P(0.80, 0.08), P(0.94, 0.22), P(0.20, 0.92)], fill=(95, 50, 22, 255))
        for i in range(6):
            o = -0.05 + i*0.025; L([(0.13+o, 0.85-o), (0.87+o, 0.15-o)], (235, 220, 180, 255), 0.006)
        for i in range(6):
            t = 0.30 + i*0.08; o = -0.05 + i*0.025; cx = 0.13+o + 0.74*t; cy = 0.85-o - 0.70*t
            d.polygon([P(cx-0.03, cy+0.02), P(cx+0.03, cy+0.02), P(cx, cy-0.03)], fill=(250, 245, 230, 255))
    elif sec == 16:   # 8-bit: pixel eighth note in cyan + pixel blocks
        bm = ["....XXXX", "....X..X", "....X...", "..XXX...", ".XXXX...", ".XXXX...", "..XX...."]
        for r_, row in enumerate(bm):
            for c_, ch in enumerate(row):
                if ch == 'X': R(0.14+c_*0.09, 0.06+r_*0.09, 0.225+c_*0.09, 0.145+r_*0.09, (70, 235, 245, 255))
        for i, col in enumerate(((230, 40, 60, 255), (245, 160, 30, 255), (250, 220, 40, 255), (60, 200, 90, 255), (60, 120, 240, 255))):
            R(0.06+i*0.18, 0.76, 0.22+i*0.18, 0.92, col, r=0.01)
    elif sec == 17:   # bagpipe: tartan bag, drones, chanter
        for (a_, b_) in (((0.40, 0.42), (0.18, 0.04)), ((0.48, 0.40), (0.34, 0.02)), ((0.56, 0.40), (0.52, 0.04))): L([a_, b_], DARK, 0.04); E(b_[0], b_[1]+0.02, 0.035, 0.03, WHITE)
        E(0.52, 0.58, 0.32, 0.24, (190, 25, 30, 255), outline=(90, 10, 12, 255), w=0.015)
        for k in range(3): L([(0.28+k*0.16, 0.38), (0.28+k*0.16, 0.80)], (20, 80, 40, 230), 0.035); L([(0.22, 0.48+k*0.1), (0.82, 0.48+k*0.1)], (20, 80, 40, 230), 0.03)
        L([(0.70, 0.76), (0.82, 0.98)], DARK, 0.04)
    elif sec == 18:   # finale: gold star + jingle bells
        pts = [P(0.5 + (0.40 if i % 2 == 0 else 0.17)*math.cos(-math.pi/2 + i*math.pi/5), 0.45 + (0.40 if i % 2 == 0 else 0.17)*math.sin(-math.pi/2 + i*math.pi/5)) for i in range(10)]
        d.polygon(pts, fill=(250, 195, 60, 255), outline=(170, 110, 20, 255))
        for x in (0.18, 0.82): E(x, 0.84, 0.11, 0.11, GOLD, outline=(140, 90, 20, 255), w=0.012); L([(x-0.08, 0.86), (x+0.08, 0.86)], DARK, 0.015)
        E(0.5, 0.86, 0.06, 0.045, (200, 20, 40, 255))
    return im.resize((px, px), Image.LANCZOS)

# ------------------------------------------------------------------ sections from the plan
# A section = one contiguous run of hits by the same melody track (time order), so an instrument may come back many times
# (e.g. the remix: 6 instruments rotating every 16 beats -> 36 sections).  The instrument (name / icon / accent colour) is
# resolved from the track NAME (keywords below), the label number is the track's own "NN." prefix; the old 12-track MIDI
# (one contiguous section per track, numbered like NAMES) gives exactly the same sections as before.
INST_KEYS = [('castanet', 1), ('piano', 2), ('vibra', 3), ('tubular', 4), ('marimba', 5), ('kalimba', 6), ('flute', 7),
             ('xylo', 8), ('ocarina', 9), ('glock', 10), ('steel drum', 11), ('guitar', 12)]
HOOK_KEYS = [('tutti', 18), ('finale', 18), ('music box', 14), ('koto', 15), ('8-bit', 16), ('square lead', 16), ('bagpipe', 17)]   # hook50 (checked first)
def inst_of(track):
    t = track.lower()
    if 'tubular' in t and 'castanet' in t: return 13
    for kw, i in HOOK_KEYS:
        if kw in t: return i
    for kw, i in INST_KEYS:
        if kw in t: return i
    m = re.match(r'\s*(\d+)(?:/\d+)?\.', track); return int(m.group(1)) if m and int(m.group(1)) in NAMES else None
P = json.load(open(a.plan)); fps = P['fps']; nfr = len(P['marble'])
SEC = []                                       # section index -> (start t, instrument id (NAMES key), label number, subtitle)
for k in sorted(P['keys'], key=lambda k: k['t']):
    m = re.match(r'\s*(\d+)(?:/\d+)?\.', k['track']); inst = inst_of(k['track'])
    if not m or inst is None: continue
    if SEC and SEC[-1][4] == k['track']: continue
    sub = re.search(r'\(([^)]*)\)', k['track'])
    SEC.append((k['t'], inst, int(m.group(1)), sub.group(1) if sub else '', k['track']))
secs = {n: (S_[0], S_[3]) for n, S_ in enumerate(SEC)}
order = list(range(len(SEC)))
INST = {n: SEC[n][1] for n in order}; NUM = {n: SEC[n][2] for n in order}

def title_card(n, sub):
    zh, en, acc = NAMES[INST[n]]; cw, ch = int(820*S), int(196*S)
    im = Image.new('RGBA', (cw + int(40*S), ch + int(40*S)), (0, 0, 0, 0)); ox = oy = int(20*S)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([ox, oy+int(6*S), ox+cw, oy+ch+int(6*S)], radius=int(40*S), fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10*S))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([ox, oy, ox+cw, oy+ch], radius=int(40*S), fill=(16, 16, 22, a.card_alpha), outline=acc + (220,), width=max(2, int(3*S)))
    isz = int(156*S); d.ellipse([ox+int(18*S), oy+int(20*S), ox+int(18*S)+isz, oy+int(20*S)+isz], fill=(255, 255, 255, 34), outline=acc + (160,), width=max(1, int(2*S)))
    ic = icon(INST[n], int(124*S)); im.alpha_composite(ic, (ox+int(34*S), oy+int(36*S)))
    tx = ox + int(200*S)
    d.text((tx, oy+int(18*S)), f'{NUM[n]:02d}  ·  {sub}', font=font(False, 26), fill=acc + (235,))
    fz = font(True, 72); d.text((tx, oy+int(46*S)), zh, font=fz, fill=(255, 255, 255, 255))
    zw = d.textlength(zh, font=fz); d.text((tx + zw + int(22*S), oy+int(78*S)), en, font=font(True, 40), fill=(235, 235, 240, 235))
    if a.card_scale != 1: im = im.resize((int(im.width*a.card_scale), int(im.height*a.card_scale)), Image.LANCZOS)
    return im

def corner(n):
    zh, en, acc = NAMES[INST[n]]; f1, f2 = font(True, 30), font(False, 24)
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1))); w = int(64*S + tmp.textlength(f'{NUM[n]:02d}', font=f2) + 14*S + tmp.textlength(zh, font=f1) + 12*S + tmp.textlength(en, font=f2) + 26*S); h = int(56*S)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w-1, h-1], radius=h//2, fill=(16, 16, 22, 170), outline=acc + (200,), width=max(1, int(2*S)))
    im.alpha_composite(icon(INST[n], int(44*S)), (int(10*S), int(6*S))); x = int(62*S)
    d.text((x, int(12*S)), f'{NUM[n]:02d}', font=f2, fill=acc + (255,)); x += int(tmp.textlength(f'{NUM[n]:02d}', font=f2) + 14*S)
    d.text((x, int(6*S)), zh, font=f1, fill=(255, 255, 255, 255)); x += int(tmp.textlength(zh, font=f1) + 12*S)
    d.text((x, int(12*S)), en, font=f2, fill=(225, 225, 232, 235))
    return im

_LK = {}
for n in order: _LK.setdefault((INST[n], NUM[n], secs[n][1]), n)
LBL = {n: _LK[(INST[n], NUM[n], secs[n][1])] for n in order}   # canonical section per distinct label
CARD = {n: title_card(n, secs[n][1]) for n in set(LBL.values())}; CARD = {n: CARD[LBL[n]] for n in order}
PILL = {n: corner(n) for n in set(LBL.values())}; PILL = {n: PILL[LBL[n]] for n in order}
PILL_XY = (int(48*S), int(222*S))
START = {n: max(secs[n][0], a.first_delay) for n in order}          # card start time per section (first section delayed)

# ------------------------------------------------------------------ v5b: per-section card placement from projected striker / marble positions
def place_cards():
    import numpy as np
    off = np.array([0.5, -5.3, 1.0]); aim = np.array([0, 0, -0.9])   # scene.py v2+ camera rig (lens 40, sensor 36 vertical fit)
    fw = (aim-off)/np.linalg.norm(aim-off); rt = np.cross(fw, [0, 0, 1]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw); FPX = 40/36*H
    cam = np.array(P['camera']); mar = np.array(P['marble']); K = P['keys']; KX = np.array([[k['x'], 0, k['z']] for k in K])
    def proj(fr, pts):
        C = np.array([cam[fr][0], 0, cam[fr][1]]) + off; d = pts - C; z = d @ fw
        return np.c_[W/2 + (d @ rt)/z*FPX, H/2 - (d @ up)/z*FPX], z
    cw, ch = CARD[order[0]].size; pad = int(20*S*a.card_scale)       # card image includes a shadow margin
    xs = [x for x in (int(28*S), int(120*S), int(220*S)) if x + cw - pad <= int(900*S)]
    ys = list(range(int(214*S), int(1536*S) - ch + pad, int(24*S)))
    out = {}
    for n in order:
        f0 = int(round(START[n]*fps)); f1 = min(len(cam)-1, int(round((START[n]+FIN+HOLD+FOUT)*fps)))
        cost = {}
        for fr in range(f0, f1+1, 2):
            kp, kz = proj(fr, KX); vis = (kz > 0) & (kp[:,1] > -300) & (kp[:,1] < H+300); kp = kp[vis]; kr = 0.45*FPX/kz[vis]   # striker incl. silhouette ~0.45 m
            mp, mz = proj(fr, np.array([[mar[fr][0], 0, mar[fr][1]]])); mr = (0.15*FPX/mz[0]) + 40*S
            for x in xs:
                for y in ys:
                    x0, y0, x1, y1 = x+pad, y+pad, x+cw-pad, y+ch-pad
                    def pen(c, r):
                        dx = np.maximum(np.maximum(x0-c[:,0], 0), c[:,0]-x1); dy = np.maximum(np.maximum(y0-c[:,1], 0), c[:,1]-y1)
                        return np.maximum(0, r - np.hypot(dx, dy))
                    cst = pen(kp, kr).sum() + 6*pen(mp, mr).sum() + 0.05*(y - ys[0])   # small preference for the top
                    cost[(x, y)] = cost.get((x, y), 0) + cst
        out[n] = cost
    if a.place == 'auto':                                            # one consistent spot: minimum of the summed cost
        tot = {c: sum(out[n][c] for n in order) for c in out[order[0]]}; g = min(tot, key=tot.get)
        return {n: (g, out[n][g], out[n][(xs[0], int(214*S))]) for n in order}
    return {n: (min(out[n], key=out[n].get), min(out[n].values()), out[n][(xs[0], int(214*S))]) for n in order}
if a.cards and a.place in ('auto', 'section'):
    PL = place_cards(); CARDXY = {n: PL[n][0] for n in order}
    for n in order: print(f'  card {n:02d} at {PL[n][0]}  overlap cost {PL[n][1]:.0f} (fixed top would be {PL[n][2]:.0f})')
else:
    CARDXY = {n: (int(28*S), int(214*S)) for n in order}
def state(f):
    """(section, card alpha, label alpha, previous section, previous label alpha) - quantised so identical frames are hard-linked"""
    t = f / fps; cur = None
    for n in order:
        if secs[n][0] <= t + 1e-6: cur = n
    if cur is None: return (None, 0, 0, None, 0)
    q = lambda v: round(v*20)/20
    dt = t - START[cur]; i = order.index(cur); prev = order[i-1] if i > 0 else None
    if a.cards:                                                      # opt-in: big card first, label fades in as the card leaves
        if dt < 0: return (cur, 0, 0, None, 0)
        ca = min(1, dt/FIN) if dt < FIN else (1 if dt < FIN+HOLD else max(0, 1-(dt-FIN-HOLD)/FOUT))
        pa = 0 if a.no_corner else 0.8*min(1, max(0, (dt-FIN-HOLD-FOUT*0.5)/0.4))
        return (cur, q(ca), q(pa), None, 0)
    # default: corner label only, visible from the start of each section; cross-fades from the previous section's label
    if a.no_corner: return (cur, 0, 0, None, 0)
    u = 1.0 if a.label_fade <= 0 else min(1, max(0, dt/a.label_fade))
    pp = (1-u) if prev is not None else 0
    return (LBL[cur], 0, q(0.8*u), LBL[prev] if pp > 0 else None, q(0.8*pp))
def overlay(st):
    n, ca, pa, pn, ppa = st; im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if n is None: return im
    layers = [(PILL[pn], ppa, PILL_XY, False)] if pn is not None and ppa > 0 else []
    if a.cards: layers.append((CARD[n], ca, CARDXY[n], True))
    layers.append((PILL[n], pa, PILL_XY, False))
    for src, al, xy, is_card in layers:
        if al <= 0: continue
        s = src.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v*al))); y = xy[1] + (int((1-al)*-18*S) if is_card else 0)
        im.alpha_composite(s, (xy[0], max(0, y)))
    return im

if a.still >= 0:
    st = state(a.still)
    if a.cards and st[2] == 0: st = (st[0], max(st[1], 1.0), st[2], st[3], st[4])   # preview: show the card at full strength
    ov = overlay(st)
    bg = Image.open(a.bg).convert('RGBA').resize((W, H)) if a.bg else Image.new('RGBA', (W, H), (90, 90, 90, 255))
    out = Image.alpha_composite(bg, ov); out.convert('RGB').save(a.png or 'title_still.png'); print('wrote', a.png or 'title_still.png', st); sys.exit()
os.makedirs(a.out, exist_ok=True); end = (a.end if a.end >= 0 else nfr-1); cache = {}
for f in range(a.start, end+1):
    st = state(f); fn = os.path.join(a.out, f'{f:05d}.png')
    if os.path.exists(fn): os.remove(fn)
    if st in cache: os.link(cache[st], fn)
    else: overlay(st).save(fn, optimize=False, compress_level=3); cache[st] = fn
print('overlay frames', a.start, '-', end, 'unique', len(cache), '->', a.out)
for n in order: print(f'  section {n+1:02d}: {NUM[n]:02d} {NAMES[INST[n]][0]} {NAMES[INST[n]][1]} at {secs[n][0]:.2f}s (frame {round(secs[n][0]*fps)})')
