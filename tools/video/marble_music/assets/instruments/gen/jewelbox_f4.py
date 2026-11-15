"""Jewelbox Orchestra (珠匣乐团) - family 4 (33-41: brass & saxophones). All folders new and registry-only (tracks_regex NEVER).
Phone-size separation of similar brass: trumpet = gold lacquer, open bell; muted trumpet = SILVER plate + big dark Harmon mute in the bell;
trombone = long slide; tuba = huge upward bell; horn = round coils; brass section = four camera-facing bells.
Saxes lie on their side (body tube = striker): soprano = straight silver, alto = gold J, tenor = bigger black-lacquer J with gold keys."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER
from snippets import H, BRASS

TUBEPINS = [{"x":-0.15,"z":0.0,"y_start":0.03,"radius":0.02},{"x":0.15,"z":0.0,"y_start":0.03,"radius":0.02}]
SRC = HDR + H + BRASS

def lacquer(name, rgb, rough=0.16):
    return f"C.mat('{name}',{rgb},rough={rough},metal=1.0)"
GOLD = (0.92,0.64,0.24); SILVER = (0.9,0.9,0.92); ROSE = (0.9,0.52,0.33); DKGOLD = (0.78,0.5,0.16)

# ------------------------------------------------------------------ trumpet geometry (33 + 36 share it)
TRUMPET = '''
def trumpet(C, mute=False):
    P = []
    P.append(C.prim('cyl', 0, loc=(0,0,0.017), rot=(0,math.pi/2,0), scale=(0.028,0.028,0.62), verts=32))    # bell pipe (top z=0.045)
    P.append(C.prim('cyl', 0, loc=(-0.10,0,-0.022), rot=(0,math.pi/2,0), scale=(0.02,0.02,0.42), verts=24))  # lead pipe
    for x in (-0.08, 0.0, 0.08):                                                                 # piston valves (behind)
        P.append(C.prim('cyl', 0, loc=(x,0.2,-0.03), scale=(0.03,0.03,0.26), verts=24))
        for z in (0.10, -0.16): P.append(C.prim('cyl', 2, loc=(x,0.2,z), scale=(0.034,0.034,0.016), verts=24))
        P.append(C.prim('cyl', 2, loc=(x,0.2,0.13), scale=(0.006,0.006,0.05), verts=8))
        P.append(C.prim('cyl', 1, loc=(x,0.2,0.165), scale=(0.024,0.024,0.014), verts=24))       # pearl finger buttons
    P.append(sweep(C, 0, [(0.08,-0.16),(0.08,-0.22)] + arc_pts(0.02,-0.22,0.06,0.0,-math.pi/2,6)[1:] + [(-0.22,-0.28)] + arc_pts(-0.22,-0.21,0.07,-math.pi/2,-math.pi,6)[1:] + [(-0.29,-0.03)], 0.02, y=0.2))
    P += bell(C, 0, 3, (0.30,0.017), (1,0), 0.30, 0.028, 0.17, y=0.215)
    P.append(sweep(C, 2, [(-0.43,0.017),(-0.38,0.017),(-0.33,0.017)], [0.03,0.012,0.014], y=0.19))  # mouthpiece
    if mute:                                                                                      # Harmon mute in the bell
        prof = [(0.50,0.07),(0.53,0.11),(0.57,0.135),(0.61,0.12),(0.64,0.07),(0.66,0.03),(0.72,0.02),(0.74,0.06),(0.745,0.06)]
        P.append(sweep(C, 4, [(x,0.017) for x,_ in prof], [r for _,r in prof], y=0.215, ymax=0.06, n=32))
        P.append(sweep(C, 2, [(0.525,0.017),(0.545,0.017)], 0.118, y=0.215, ymax=0.058, n=32))   # cork ring
    return P
'''

for folder, sec, num, mute, body_rgb, desc in (
    ('trumpet', 133, 33, False, GOLD, 'Jewelbox 33 Trumpet: bright GOLD-lacquer trumpet lying on its side - bell pipe and lead pipe are the striker; three piston valves with pearl finger buttons, the main tuning slide loop, a silver mouthpiece and an OPEN flared bell behind the marble plane.'),
    ('muted_trumpet', 136, 36, True, SILVER, 'Jewelbox 36 Muted Trumpet: the same trumpet in SILVER plate (gold valve caps and buttons) with a big dark copper-and-black Harmon (wah-wah) mute and cork ring jammed in the bell - unmistakably different from the open gold trumpet (33).')):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=TUBEPINS, description=desc,
      slots=['body','pearl','trim','dark','mute','pin'], flash_slot='body', flash_color=[1.0,0.85,0.5]),
f'''"""{folder} (jewelbox {num})."""
'''+SRC+TRUMPET+f'''
def build(C, variant=None):
    return trumpet(C, mute={mute})
''',
f'''"""{folder} materials"""
def shared(C):
    return {{'pearl': C.mat('{folder}_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), 'trim': {lacquer(folder+'_trim', GOLD if mute else SILVER)},
            'dark': C.mat('{folder}_dark',(0.02,0.015,0.01),rough=0.6), 'mute': C.mat('{folder}_mute',(0.25,0.08,0.03),rough=0.3,metal=0.8)}}
def body(C, name, j, note, variant):
    return {lacquer('name', body_rgb, 0.14).replace("'name'", 'name')}
''')

# ------------------------------------------------------------------ 34 trombone
write('trombone', dict(name='trombone', section=134, tracks_regex=NEVER, pins=TUBEPINS,
  description='Jewelbox 34 Trombone: the inner slide tubes are the striker; the slide continues behind the marble plane to its U-crook, with the '
              'slide brace, a silver mouthpiece, the tuning-slide loop and the bell section below ending in a big flared gold bell facing forward.',
  slots=['body','trim','dark','pin'], flash_slot='body', flash_color=[1.0,0.85,0.5]),
'''"""trombone (jewelbox 34): slide striker + extended slide, tuning loop and big bell."""
'''+SRC+'''
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,z), rot=(0,math.pi/2,0), scale=(0.02,0.02,0.62), verts=24) for z in (0.025, -0.025)]
    P.append(C.prim('cube', 1, loc=(-0.22,0.0,0.0), scale=(0.02,0.03,0.07), bevel=0.004))           # slide brace
    for z in (0.025, -0.025): P.append(sweep(C, 0, [(0.31,z),(0.64,z)], 0.021, y=0.18))
    P.append(sweep(C, 0, arc_pts(0.64,0.0,0.025,math.pi/2,-math.pi/2,10), 0.021, y=0.18))           # crook
    P.append(C.prim('cube', 1, loc=(0.50,0.19,0.0), scale=(0.02,0.03,0.07), bevel=0.004))
    P.append(sweep(C, 1, [(-0.42,0.025),(-0.37,0.025),(-0.32,0.025)], [0.032,0.012,0.016], y=0.19))  # mouthpiece
    P.append(sweep(C, 0, [(-0.31,-0.025),(-0.44,-0.025)] + arc_pts(-0.44,-0.085,0.06,math.pi/2,3*math.pi/2,10)[1:] + [(0.0,-0.145)], 0.019, y=0.21))
    P += bell(C, 0, 2, (0.0,-0.145), (1,0), 0.32, 0.019, 0.16, y=0.215)
    return P
''',
f'''"""trombone materials"""
def shared(C):
    return {{'trim': {lacquer('tb_trim', SILVER)}, 'dark': C.mat('tb_dark',(0.02,0.015,0.01),rough=0.6)}}
def body(C, name, j, note, variant):
    return C.mat(name,{GOLD},rough=0.14,metal=1.0)
''')

# ------------------------------------------------------------------ 35 tuba
write('tuba', dict(name='tuba', section=135, tracks_regex=NEVER, pins=TUBEPINS,
  description='Jewelbox 35 Tuba: a thick deep-gold branch tube is the striker; behind it the tuba stands upright - wide conical body, big bottom '
              'bow and a HUGE bell flaring straight up, four rotary valves with silver levers and coiled valve tubing, mouthpipe from the left.',
  slots=['body','trim','dark','pin'], flash_slot='body', flash_color=[1.0,0.8,0.45]),
'''"""tuba (jewelbox 35): branch-tube striker + upright tuba with huge upward bell."""
'''+SRC+'''
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,0.005), rot=(0,math.pi/2,0), scale=(0.04,0.04,0.62), verts=32)]
    P.append(sweep(C, 0, [(-0.05,-0.03),(-0.05,-0.40)], [0.045,0.065], y=0.22))                      # body
    P.append(sweep(C, 0, arc_pts(0.125,-0.40,0.175,math.pi,2*math.pi,16), [0.065+0.01*k/16 for k in range(17)], y=0.22))   # bottom bow
    P.append(sweep(C, 0, [(0.30,-0.40),(0.30,0.0)], [0.075,0.09], y=0.22))
    P += bell(C, 0, 2, (0.30,0.0), (0,1), 0.30, 0.09, 0.26, y=0.225, ymax=0.06)
    for i, x in enumerate((-0.33,-0.25,-0.17,-0.09)):                                                # rotary valves + levers
        P.append(C.prim('cyl', 0, loc=(x,0.2,-0.20), rot=(math.pi/2,0,0), scale=(0.034,0.034,0.06), verts=24))
        P.append(C.prim('cyl', 1, loc=(x,0.168,-0.20), rot=(math.pi/2,0,0), scale=(0.02,0.02,0.006), verts=16))
        P.append(bar(C, (x,-0.20), (x-0.06,-0.10), 0.012, 0.01, 1, 0.172))
    P.append(sweep(C, 0, arc_pts(-0.21,-0.33,0.10,0.0,2*math.pi,24), 0.02, y=0.21))                 # valve tubing coil
    P.append(sweep(C, 0, [(-0.31,0.005),(-0.40,-0.04),(-0.40,-0.16),(-0.34,-0.20)], 0.022, y=0.21))   # mouthpipe
    P.append(sweep(C, 1, [(-0.50,-0.0),(-0.45,-0.02),(-0.41,-0.035)], [0.035,0.015,0.018], y=0.19))
    return P
''',
f'''"""tuba materials"""
def shared(C):
    return {{'trim': {lacquer('tu_trim', SILVER)}, 'dark': C.mat('tu_dark',(0.02,0.015,0.01),rough=0.6)}}
def body(C, name, j, note, variant):
    return C.mat(name,{DKGOLD},rough=0.16,metal=1.0)
''')

# ------------------------------------------------------------------ 37 french horn
write('french_horn', dict(name='french_horn', section=137, tracks_regex=NEVER, pins=TUBEPINS,
  description='Jewelbox 37 French Horn: rose-brass lead pipe is the striker; behind it the horn\'s ROUND coils (three concentric loops), a cluster '
              'of three rotary valves with silver lever paddles in the middle, and the wide bell flaring out to the lower right.',
  slots=['body','trim','dark','pin'], flash_slot='body', flash_color=[1.0,0.75,0.55]),
'''"""french_horn (jewelbox 37): lead-pipe striker + round coils, rotary valves, side bell."""
'''+SRC+'''
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,0.015), rot=(0,math.pi/2,0), scale=(0.03,0.03,0.62), verts=32)]
    cx, cz = -0.02, -0.27
    for R, r in ((0.21,0.018), (0.175,0.016), (0.14,0.015)):
        P.append(sweep(C, 0, arc_pts(cx,cz,R,0.0,2*math.pi,40), r, y=0.215, n=16))
    for i, x in enumerate((-0.07,-0.01,0.05)):
        P.append(C.prim('cyl', 0, loc=(x,0.2,-0.24), rot=(math.pi/2,0,0), scale=(0.028,0.028,0.07), verts=24))
        P.append(C.prim('cyl', 1, loc=(x,0.163,-0.24), rot=(math.pi/2,0,0), scale=(0.016,0.016,0.006), verts=16))
        P.append(bar(C, (x,-0.24), (x-0.10,-0.16+0.02*i), 0.012, 0.008, 1, 0.168))
        P.append(C.prim('cube', 1, loc=(x-0.10,0.168,-0.16+0.02*i), scale=(0.035,0.01,0.02), bevel=0.004))
    P.append(sweep(C, 0, [(0.31,0.015),(0.36,-0.03),(0.30,-0.07),(0.12,-0.08)], 0.02, y=0.2))          # lead pipe into the coils
    P += bell(C, 0, 2, (0.16,-0.42), (1,-0.35), 0.40, 0.02, 0.19, y=0.225, ymax=0.06)
    return P
''',
f'''"""french_horn materials"""
def shared(C):
    return {{'trim': {lacquer('fh_trim', SILVER)}, 'dark': C.mat('fh_dark',(0.02,0.015,0.01),rough=0.6)}}
def body(C, name, j, note, variant):
    return C.mat(name,{ROSE},rough=0.16,metal=1.0)
''')

# ------------------------------------------------------------------ 38 brass section
write('brass_section', dict(name='brass_section', section=138, tracks_regex=NEVER, pins=[{"x":-0.15,"z":-0.03,"y_start":0.2,"radius":0.022},{"x":0.15,"z":-0.03,"y_start":0.2,"radius":0.022}],
  description='Jewelbox 38 Brass Section: a polished gold music-stand rail is the striker; behind it FOUR bells face the camera (trumpet, trombone, '
              'horn and a big tuba bell, staggered, dark throats), and below a gold music stand holding a white score with staff lines.',
  slots=['body','brass','dark','paper','ink','pin'], flash_slot='body', flash_slots=['body','brass'], flash_color=[1.0,0.85,0.5]),
'''"""brass_section (jewelbox 38): gold rail striker + four camera-facing bells + music stand."""
'''+SRC+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.03)]
    for x, z, r in ((-0.50,0.05,0.10), (-0.25,0.17,0.12), (0.27,0.17,0.13), (0.52,0.03,0.17)):
        P += front_bell(C, 1, 2, x, z, r)
    P.append(C.prim('cyl', 0, loc=(0,0.24,-0.33), scale=(0.012,0.012,0.50), verts=12))              # music stand
    for a in (-0.5, 0.5): P.append(bar(C, (0,-0.58), (0.22*math.sin(a)*2,-0.62), 0.012, 0.012, 0, 0.24))
    P.append(C.prim('cube', 0, loc=(0,0.22,-0.17), rot=(0.25,0,0), scale=(0.46,0.02,0.24), bevel=0.006))
    P.append(C.prim('cube', 3, loc=(0,0.205,-0.165), rot=(0.25,0,0), scale=(0.40,0.006,0.20)))
    for k in range(5):
        for s in range(2): P.append(C.prim('cube', 4, loc=(0,0.199,-0.10-0.09*s+0.012*k), rot=(0.25,0,0), scale=(0.36,0.003,0.003)))
    return P
''',
f'''"""brass_section materials"""
def shared(C):
    return {{'brass': C.mat('bs_brass',{GOLD},rough=0.15,metal=1.0), 'dark': C.mat('bs_dark',(0.02,0.015,0.01),rough=0.6),
            'paper': C.mat('bs_paper',(0.9,0.88,0.82),rough=0.7), 'ink': C.mat('bs_ink',(0.02,0.02,0.02),rough=0.6)}}
def body(C, name, j, note, variant):
    return C.mat(name,{GOLD},rough=0.12,metal=1.0)
''')

# ------------------------------------------------------------------ saxophones
SAX = '''
def sax(C, bell_r=0.15, neck='alto', straight=False, scale=1.0):
    P = [C.prim('cyl', 0, loc=(0,0,0.005), rot=(0,math.pi/2,0), scale=(0.04,0.04,0.62), verts=32)]          # body tube (top z=0.045)
    for i, x in enumerate((-0.24,-0.17,-0.10,0.0,0.07,0.14,0.22)):                                         # pearl-topped key cups (camera side)
        P.append(C.prim('cyl', 1, loc=(x,-0.035,0.005), rot=(math.pi/2,0,0), scale=(0.022,0.022,0.012), verts=20))
        P.append(C.prim('cyl', 2, loc=(x,-0.042,0.005), rot=(math.pi/2,0,0), scale=(0.013,0.013,0.004), verts=16))
    P.append(C.prim('cyl', 1, loc=(0,-0.035,-0.03), rot=(0,math.pi/2,0), scale=(0.004,0.004,0.56), verts=8))   # key rod
    if straight:
        P += bell(C, 0, 3, (0.30,0.005), (1,0), 0.24, 0.04, bell_r, y=0.215)
        P.append(sweep(C, 4, [(-0.44,0.005),(-0.39,0.005),(-0.33,0.005)], [0.012,0.02,0.026], y=0.19))
        return P
    R = 0.12*scale; zb = 0.005 - 2*R
    P.append(sweep(C, 0, arc_pts(0.31,0.005-R,R,math.pi/2,-math.pi/2,16), [0.042+0.008*k/16 for k in range(17)], y=0.215))   # bow
    P.append(sweep(C, 0, [(0.31,zb),(0.06,zb)], [0.05,0.058], y=0.215))
    P += bell(C, 0, 3, (0.06,zb), (-1,-0.25), 0.22*scale, 0.058, bell_r, y=0.222, ymax=0.06)
    P.append(C.prim('cyl', 1, loc=(0.20,0.165,zb), rot=(math.pi/2,0,0), scale=(0.02,0.02,0.008), verts=16))
    if neck == 'tenor':
        pts = [(-0.31,0.005),(-0.37,0.03),(-0.41,0.08),(-0.44,0.125),(-0.49,0.14),(-0.54,0.125)]
    else:
        pts = [(-0.31,0.005),(-0.37,0.025),(-0.42,0.06),(-0.46,0.09)]
    P.append(sweep(C, 0, pts, [0.036,0.03,0.025,0.02,0.018,0.016][:len(pts)], y=0.2))
    ex, ez = pts[-1]; dx, dz = pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]; L = math.hypot(dx, dz)
    P.append(sweep(C, 4, [(ex,ez),(ex+0.09*dx/L, ez+0.09*dz/L)], [0.02,0.012], y=0.2))                     # black mouthpiece
    P.append(C.prim('cyl', 2, loc=(ex+0.02*dx/L,0.2,ez+0.02*dz/L), rot=(0,math.atan2(dx,dz),0), scale=(0.022,0.022,0.012), verts=16))  # ligature
    return P
'''
for folder, sec, num, kw, body_rgb, keys_rgb, desc in (
    ('soprano_sax', 139, 39, "bell_r=0.12, straight=True", SILVER, GOLD,
     'Jewelbox 39 Soprano Sax: a STRAIGHT silver-plated soprano lying on its side - body tube is the striker with pearl-topped key cups on the camera side, a black mouthpiece at the left and the flared bell continuing straight out to the right.'),
    ('alto_sax', 140, 40, "bell_r=0.15, neck='alto'", GOLD, SILVER,
     'Jewelbox 40 Alto Sax: classic gold-lacquer J-shaped alto lying on its side - body tube with pearl key cups is the striker, the U-bow at the right, the bell tube returning under it to a flared bell, short curved neck and black mouthpiece at the left.'),
    ('tenor_sax', 141, 41, "bell_r=0.19, neck='tenor', scale=1.25", (0.02,0.02,0.022), GOLD,
     'Jewelbox 41 Tenor Sax: a BIGGER J-shaped tenor in BLACK lacquer with gold keys and gold-rimmed pearl cups - deeper bow, larger bell, and the tenor\'s pronounced S-curved neck with black mouthpiece.')):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=TUBEPINS, description=desc,
      slots=['body','pearl','keys','dark','mouth','pin'], flash_slot='body', flash_color=[1.0,0.85,0.55]),
f'''"""{folder} (jewelbox {num})."""
'''+SRC+SAX+f'''
def build(C, variant=None):
    return sax(C, {kw})
''',
f'''"""{folder} materials"""
def shared(C):
    return {{'pearl': C.mat('{folder}_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), 'keys': {lacquer(folder+'_keys', keys_rgb)},
            'dark': C.mat('{folder}_dark',(0.02,0.015,0.01),rough=0.6), 'mouth': C.mat('{folder}_mouth',(0.015,0.015,0.015),rough=0.25,coat=0.6)}}
def body(C, name, j, note, variant):
    return C.mat(name,{body_rgb},rough={0.12 if folder != 'tenor_sax' else 0.18},metal={1.0 if folder != 'tenor_sax' else 0.0},coat={0.0 if folder != 'tenor_sax' else 1.0})
''')
print('wrote jewelbox F4 assets')
