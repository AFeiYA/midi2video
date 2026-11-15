"""Jewelbox Orchestra (珠匣乐团, registry series 'jewelbox') - family 1 (01-12: pianos, bells & mallets): new / adapted strikers.
Reused unchanged from the library: glockenspiel (v5), music_box, marimba (v5), tubular_bells (v5).
All new folders use tracks_regex NEVER -> they are reached only through registry.py, so older songs keep their mapping."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER

KEYS = dict(variants=['white', 'black'], variant_rule='pitch', pins=[{"x":-0.15,"z":-0.03,"y_start":0.2,"radius":0.022},{"x":0.15,"z":-0.03,"y_start":0.2,"radius":0.022}])
# striker key shared by the keyboard instruments: natural = bevelled slab, sharp = taller tapered black-key profile (as piano v5)
KEY = '''
def key(C, variant, mi=0):
    if variant == 'black':
        return C.shape_profile('blackkey', [(-0.31,-0.07),(0.31,-0.07),(0.31,-0.0),(0.27,0.045),(-0.27,0.045),(-0.31,-0.0)], 0.22, -0.11, mi, bevel=0.01)
    return C.prim('cube', mi, loc=(0,0,0), scale=(0.62,0.30,0.09), bevel=0.012)
def stubs(C, variant, mi):
    """two black-key stubs on the key bed behind the marble plane (natural keys only) so a C-major melody still reads as a keyboard"""
    return [] if variant == 'black' else [C.prim('cube', mi, loc=(x,0.225,0.03), scale=(0.11,0.13,0.07), bevel=0.012) for x in (-0.25, 0.25)]
def rod(C, a, b, r, mi, verts=16):
    """cylinder from (x,z) a to b at local y = a[2]"""
    import math
    (x0, z0, y), (x1, z1) = a, b; L = math.hypot(x1-x0, z1-z0)
    return C.prim('cyl', mi, loc=((x0+x1)/2, y, (z0+z1)/2), rot=(0, math.atan2(x1-x0, z1-z0), 0), scale=(r, r, L), verts=verts)
'''
IVORY = '''
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
'''

# ------------------------------------------------------------------ 01 acoustic grand piano
write('grand_piano', dict(name='grand_piano', section=101, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 01 Acoustic Grand Piano: ivory/ebony striker key chosen by pitch class, in front of a black-lacquer concert grand '
              'in side elevation (gold-rimmed case, lid propped open on a gold stick with gold strings showing, three turned legs on brass casters, lyre pedals).',
  slots=['body','lacquer','gold','felt','dark','pin'], flash_slot='body', flash_color=[1.0,0.85,0.55]),
'''"""grand_piano (jewelbox 01): pitch-chosen ivory/ebony key + black lacquer grand piano profile behind the marble plane."""
'''+HDR+KEY+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.008))          # key bed (lacquer)
    P.append(C.prim('cube', 3, loc=(0,0.235,0.0), scale=(0.64,0.10,0.012), bevel=0.003))            # red felt
    P += stubs(C, variant, 1)
    # case (side elevation): straight spine on the left, rounded tail on the right
    P.append(C.shape_profile('gp_case', [(-0.58,-0.07),(0.46,-0.07),(0.57,-0.10),(0.61,-0.15),(0.58,-0.21),(0.48,-0.24),(-0.58,-0.24)], 0.07, 0.19, 1, bevel=0.012))
    P.append(C.prim('cube', 2, loc=(0.0,0.185,-0.075), scale=(1.14,0.012,0.012), bevel=0.003))     # gold rims
    P.append(C.prim('cube', 2, loc=(-0.05,0.185,-0.235), scale=(1.04,0.012,0.01), bevel=0.003))
    # lid propped open (hinged near the keys, rising to the tail), gold prop stick, gold strings under it
    P.append(C.prim('cube', 1, loc=(0.307,0.262,0.098), rot=(0,-0.5,0), scale=(0.70,0.04,0.02), bevel=0.006))
    P.append(C.prim('cube', 2, loc=(0.307,0.24,0.093), rot=(0,-0.5,0), scale=(0.66,0.004,0.008)))
    P.append(rod(C, (0.50,-0.07,0.235), (0.50,0.19), 0.009, 2))
    for i in range(6):
        P.append(rod(C, (0.05,-0.062,0.205+0.012*i), (0.58,-0.062-0.012*i), 0.0035, 2, verts=8))
    # legs with brass casters, lyre + pedals
    for x in (-0.50, 0.46):
        P.append(C.prim('cyl', 1, loc=(x,0.215,-0.37), scale=(0.038,0.038,0.24), verts=20))
        P.append(C.prim('cyl', 1, loc=(x,0.215,-0.265), scale=(0.055,0.055,0.04), verts=20))
        P.append(C.prim('sphere', 2, loc=(x,0.215,-0.505), scale=(0.038,0.038,0.03), verts=16))
    for x in (-0.03, 0.03):
        P.append(rod(C, (x,-0.24,0.215), (x*1.6,-0.43), 0.008, 2))
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.445), scale=(0.16,0.05,0.035), bevel=0.008))
    for x in (-0.04, 0.0, 0.04):
        P.append(C.prim('cube', 2, loc=(x,0.18,-0.455), scale=(0.018,0.05,0.008), bevel=0.002))
    return P
''',
'''"""grand_piano materials: ivory/ebony key by pitch class, black lacquer case, gold trim"""
def shared(C):
    return {'lacquer': C.mat('gp_lacquer',(0.012,0.012,0.014),rough=0.12,coat=1.0), 'gold': C.mat('gp_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'felt': C.mat('gp_felt',(0.45,0.03,0.05),rough=0.95), 'dark': C.mat('gp_dark',(0.03,0.03,0.03),rough=0.5)}
'''+IVORY)

# ------------------------------------------------------------------ 02 electric grand piano
write('electric_grand', dict(name='electric_grand', section=102, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 02 Electric Grand Piano (CP-80 style): pitch-chosen key on a black key bed with red felt, in front of a compact pearl-white '
              'stage grand with a short angled tail and a closed flat lid, red stripe, chrome knob, chrome X-stand and a coiled black cable.',
  slots=['body','case','chrome','red','dark','pin'], flash_slot='body', flash_color=[1.0,0.55,0.45]),
'''"""electric_grand (jewelbox 02): key + pearl-white compact stage grand on a chrome X-stand."""
'''+HDR+KEY+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 4, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.01))           # black key bed
    P.append(C.prim('cube', 3, loc=(0,0.235,0.0), scale=(0.64,0.10,0.012), bevel=0.003))            # red felt
    P += stubs(C, variant, 4)
    P.append(C.shape_profile('eg_case', [(-0.48,-0.07),(0.18,-0.07),(0.44,-0.11),(0.44,-0.19),(-0.48,-0.19)], 0.08, 0.18, 1, bevel=0.015))
    P.append(C.shape_profile('eg_lid', [(-0.49,-0.062),(0.19,-0.062),(0.46,-0.10),(0.46,-0.085),(0.19,-0.048),(-0.49,-0.048)], 0.06, 0.20, 1, bevel=0.004))
    P.append(C.prim('cube', 3, loc=(-0.02,0.175,-0.13), scale=(0.84,0.01,0.025), bevel=0.003))      # red stripe
    P.append(C.prim('sphere', 2, loc=(-0.42,0.17,-0.165), scale=(0.016,0.012,0.016), verts=16))      # chrome knob
    # chrome X-stand
    for a, b in (((-0.34,-0.19,0.215), (0.26,-0.46)), ((0.26,-0.19,0.215), (-0.34,-0.46))):
        P.append(C.prim('cube', 2, loc=((a[0]+b[0])/2, 0.215, (a[1]+b[1])/2), rot=(0, __import__('math').atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(0.035,0.04,0.66), bevel=0.01))
    P.append(C.prim('sphere', 4, loc=(-0.04,0.19,-0.325), scale=(0.03,0.03,0.03), verts=16))          # pivot knob
    for x in (-0.34, 0.26):
        P.append(C.prim('cube', 4, loc=(x,0.215,-0.465), scale=(0.14,0.06,0.025), bevel=0.008))      # rubber feet
    # coiled cable from the tail down to the floor
    for i in range(9):
        P.append(C.prim('torus', 4, loc=(0.47,0.21,-0.17-0.03*i), rot=(0.25,0,0), scale=(0.022,0.006), verts=16))
    return P
''',
'''"""electric_grand materials"""
def shared(C):
    return {'case': C.mat('eg_case',(0.82,0.80,0.76),rough=0.15,coat=1.0), 'chrome': C.mat('eg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0),
            'red': C.mat('eg_red',(0.7,0.02,0.02),rough=0.4), 'dark': C.mat('eg_dark',(0.01,0.01,0.01),rough=0.6)}
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.02,0.02,0.022),rough=0.2,coat=0.8)
    return C.mat(name,(0.90,0.90,0.88),rough=0.2,coat=0.5)
''')

# ------------------------------------------------------------------ 03 electric piano 1 / rhodes
write('rhodes', dict(name='rhodes', section=103, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 03 Electric Piano 1 / Rhodes: pitch-chosen key in front of a suitcase piano: black tolex body with a silver sparkle-top lid, brushed-silver '
              'name rail, red logo plates, silver lid seam and latches, four splayed chrome legs and a chrome sustain pedal on a cable.',
  slots=['body','tolex','silver','red','dark','sparkle','pin'], flash_slot='body', flash_color=[1.0,0.65,0.35]),
'''"""rhodes (jewelbox 03): key + black tolex suitcase electric piano on splayed chrome legs."""
'''+HDR+KEY+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 2, loc=(0,0.235,-0.03), scale=(0.66,0.12,0.05), bevel=0.01))            # brushed silver name rail
    P.append(C.prim('cube', 3, loc=(-0.2,0.172,-0.03), scale=(0.12,0.01,0.03), bevel=0.003))        # red logo plate on the rail
    P += stubs(C, variant, 4)
    # suitcase: the top ~0.06 below the key hides behind it from the camera, so the silver lid band starts at z=-0.09
    P.append(C.prim('cube', 1, loc=(0,0.22,-0.215), scale=(0.98,0.12,0.19), bevel=0.04))            # black tolex suitcase (lower)
    P.append(C.prim('cube', 5, loc=(0,0.222,-0.10), scale=(0.98,0.12,0.09), bevel=0.03))            # silver 'sparkle top' lid
    P.append(C.prim('cube', 2, loc=(0,0.161,-0.145), scale=(0.94,0.006,0.012)))                      # silver lid seam
    P.append(C.prim('cube', 3, loc=(-0.28,0.162,-0.22), scale=(0.20,0.008,0.05), bevel=0.006))      # red logo plate on the case front
    for x in (0.12, 0.34):
        P.append(C.prim('cube', 2, loc=(x,0.166,-0.165), scale=(0.06,0.012,0.035), bevel=0.004))    # latches
    for x in (-0.46, 0.46):
        P.append(C.prim('sphere', 2, loc=(x,0.172,-0.30), scale=(0.02,0.012,0.02), verts=12))        # corner caps
    # splayed chrome legs (tapered: two cylinders) + pedal
    for x, dx in ((-0.36,-0.1), (0.36,0.1)):
        P.append(rod(C, (x,-0.31,0.20), (x+dx*0.6,-0.43), 0.022, 2))
        P.append(rod(C, (x+dx*0.6,-0.43,0.20), (x+dx,-0.55), 0.015, 2))
    P.append(C.prim('cube', 2, loc=(0.0,0.20,-0.53), scale=(0.12,0.06,0.025), bevel=0.008))         # sustain pedal
    P.append(rod(C, (0.06,-0.53,0.21), (0.3,-0.30), 0.006, 4, verts=8))                             # pedal cable
    return P
''',
'''"""rhodes materials"""
def shared(C):
    return {'tolex': C.mat('rh_tolex',(0.02,0.02,0.02),rough=0.85), 'silver': C.mat('rh_silver',(0.8,0.8,0.82),rough=0.3,metal=1.0,aniso=0.6),
            'red': C.mat('rh_red',(0.75,0.08,0.03),rough=0.35,coat=0.5), 'dark': C.mat('rh_dark',(0.01,0.01,0.01),rough=0.6),
            'sparkle': C.mat('rh_sparkle',(0.62,0.62,0.66),rough=0.35,metal=0.25,coat=0.6)}
'''+IVORY)

# ------------------------------------------------------------------ 04 harpsichord
write('harpsichord', dict(name='harpsichord', section=104, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 04 Harpsichord: reversed key colours (ebony naturals, bone sharps) chosen by pitch, a second (upper) manual of tiny reversed keys '
              'behind it, a long red-lacquer wing case with gold trim, the open lid painted sky-blue inside with a gold border, and gilt turned legs.',
  slots=['body','lacquer','gold','bone','ebony','paint','pin'], flash_slot='body', flash_color=[1.0,0.8,0.5]),
'''"""harpsichord (jewelbox 04): reversed keys + upper manual + red lacquer case with painted lid and turned gilt legs."""
'''+HDR+KEY+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.66,0.12,0.06), bevel=0.008))          # key bed (red lacquer)
    # upper manual: one octave of tiny reversed keys (naturals ebony, sharps bone) behind the striker
    nat = [-0.27 + 0.09*i for i in range(7)]
    for x in nat: P.append(C.prim('cube', 4, loc=(x,0.235,0.04), scale=(0.082,0.10,0.03), bevel=0.004))
    for x in (nat[0]+0.045, nat[1]+0.045, nat[3]+0.045, nat[4]+0.045, nat[5]+0.045):
        P.append(C.prim('cube', 3, loc=(x,0.215,0.065), scale=(0.045,0.06,0.03), bevel=0.004))
    P.append(C.prim('cube', 1, loc=(0,0.27,0.07), scale=(0.66,0.04,0.09), bevel=0.008))             # name board behind the upper manual
    P.append(C.prim('cube', 2, loc=(0,0.248,0.11), scale=(0.66,0.01,0.01)))
    # long wing case with angled bentside, gold trim
    P.append(C.shape_profile('hc_case', [(-0.52,-0.07),(0.58,-0.07),(0.58,-0.11),(0.30,-0.17),(-0.52,-0.17)], 0.07, 0.19, 1, bevel=0.01))
    P.append(C.prim('cube', 2, loc=(0.03,0.185,-0.072), scale=(1.10,0.012,0.012)))
    P.append(C.prim('cube', 2, loc=(-0.11,0.185,-0.168), scale=(0.82,0.012,0.012)))
    # open lid: lacquer outside, painted panel inside facing the camera, gold border
    import math
    lid = dict(loc=(0.30,0.265,0.03), rot=(0,-0.36,0))
    P.append(C.prim('cube', 1, scale=(0.60,0.03,0.30), bevel=0.01, **lid))
    P.append(C.prim('cube', 2, loc=(0.30,0.248,0.03), rot=(0,-0.36,0), scale=(0.56,0.006,0.26)))
    P.append(C.prim('cube', 5, loc=(0.30,0.244,0.03), rot=(0,-0.36,0), scale=(0.52,0.006,0.22)))
    # gilt turned legs: column + rings + ball feet
    for x in (-0.44, 0.0, 0.44):
        P.append(C.prim('cyl', 2, loc=(x,0.215,-0.31), scale=(0.018,0.018,0.26), verts=16))
        for z in (-0.20, -0.30, -0.40): P.append(C.prim('sphere', 2, loc=(x,0.215,z), scale=(0.032,0.032,0.026), verts=16))
        P.append(C.prim('sphere', 2, loc=(x,0.215,-0.45), scale=(0.03,0.03,0.022), verts=16))
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.36), scale=(0.90,0.025,0.02), bevel=0.004))          # stretcher
    return P
''',
'''"""harpsichord materials: reversed keys (natural shape = ebony, sharp shape = bone)"""
def shared(C):
    return {'lacquer': C.mat('hc_lacquer',(0.42,0.025,0.02),rough=0.18,coat=1.0), 'gold': C.mat('hc_gold',(0.95,0.72,0.35),rough=0.22,metal=1.0),
            'bone': C.mat('hc_bone',(0.9,0.86,0.76),rough=0.25,coat=0.4), 'ebony': C.mat('hc_ebony',(0.015,0.012,0.012),rough=0.2,coat=0.8),
            'paint': C.mat('hc_paint',(0.32,0.55,0.62),rough=0.6)}
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.9,0.86,0.76),rough=0.22,coat=0.5)
    return C.mat(name,(0.015,0.012,0.012),rough=0.14,coat=1.0)
''')

# ------------------------------------------------------------------ 05 celesta
write('celesta', dict(name='celesta', section=105, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 05 Celesta: pitch-chosen key (ivory/ebony) set in a honey-wood upright cabinet that rises behind it with an arched top, '
              'a gilt slatted fretwork panel and gold crest, standing on a gilt lyre with a pedal and two ball-foot legs.',
  slots=['body','wood','gold','dark','pin'], flash_slot='body', flash_color=[1.0,0.9,0.6]),
'''"""celesta (jewelbox 05): key + honey-wood upright cabinet with arched top and a gilt fretwork panel."""
'''+HDR+KEY+'''
def build(C, variant='white'):
    import math
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.03), scale=(0.70,0.10,0.06), bevel=0.01))            # key slip
    P += stubs(C, variant, 3)
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.25), scale=(0.74,0.09,0.36), bevel=0.02))            # lower cabinet
    P.append(C.prim('cube', 2, loc=(0,0.188,-0.25), scale=(0.62,0.004,0.26), bevel=0.002))          # gold panel frame
    P.append(C.prim('cube', 1, loc=(0,0.185,-0.25), scale=(0.58,0.004,0.22), bevel=0.002))
    P.append(C.prim('cube', 1, loc=(0,0.255,0.14), scale=(0.74,0.06,0.34), bevel=0.02))             # upper cabinet behind the key
    P.append(C.prim('cyl', 1, loc=(0,0.255,0.31), rot=(math.pi/2,0,0), scale=(0.37,0.12,0.06), verts=48))   # arched top
    P.append(C.prim('sphere', 2, loc=(0,0.23,0.43), scale=(0.035,0.02,0.035), verts=16))            # crest finial
    P.append(C.prim('cube', 3, loc=(0,0.222,0.17), scale=(0.56,0.004,0.13), bevel=0.002))          # fretwork panel: dark backing
    P.append(C.prim('cube', 2, loc=(0,0.22,0.17), scale=(0.58,0.006,0.15), bevel=0.004))            # gilt frame (outer)
    P.append(C.prim('cube', 3, loc=(0,0.217,0.17), scale=(0.54,0.006,0.11)))
    for k in range(11):                                                                             # gilt slats with a lozenge in the middle
        x = -0.25 + 0.05*k; P.append(C.prim('cube', 2, loc=(x,0.215,0.17), scale=(0.012,0.006,0.11)))
    P.append(C.prim('cube', 2, loc=(0,0.213,0.17), rot=(0,math.pi/4,0), scale=(0.07,0.006,0.07)))
    # gilt lyre with pedal, ball-foot legs
    for x in (-0.05, 0.05):
        P.append(rod(C, (x,-0.43,0.215), (x*1.8,-0.55), 0.009, 2))
    P.append(C.prim('cube', 2, loc=(0,0.19,-0.555), scale=(0.08,0.06,0.012), bevel=0.003))
    for x in (-0.33, 0.33):
        P.append(C.prim('cyl', 1, loc=(x,0.23,-0.48), scale=(0.03,0.03,0.12), verts=16))
        P.append(C.prim('sphere', 2, loc=(x,0.23,-0.55), scale=(0.035,0.035,0.03), verts=16))
    return P
''',
'''"""celesta materials"""
def shared(C):
    return {'wood': C.add_wood(C.mat('ce_wood',(0.55,0.32,0.12),rough=0.3,coat=0.7),(0.42,0.22,0.08),(0.70,0.45,0.20),scale=7.0),
            'gold': C.mat('ce_gold',(0.95,0.74,0.36),rough=0.18,metal=1.0), 'dark': C.mat('ce_dark',(0.05,0.03,0.02),rough=0.7)}
'''+IVORY)

# ------------------------------------------------------------------ 08 vibraphone (jewelbox)
TUBES = [(-0.47, 0.46), (0.0, 0.40), (0.47, 0.34)]
write('jb_vibraphone', dict(name='jb_vibraphone', section=108, tracks_regex=NEVER,
  description='Jewelbox 08 Vibraphone: brushed-aluminium bar on maroon cords, two smaller neighbour bars, black frame rail, three gold resonator tubes '
              'hanging world-vertical (meta.hanging) with black fan discs on a chrome motor shaft and a small motor box at the end.',
  slots=['body','cord','resonator','dark','chrome','pin'], flash_slot='body', flash_color=[0.45,0.7,1.0],
  pins=[{"x":-0.14,"z":0.0,"y_start":0.17,"radius":0.022},{"x":0.14,"z":0.0,"y_start":0.17,"radius":0.022}],
  hanging=[{"attach":[x,0.222,-0.075],"radius":0.058,"inner":0.048,"length":L,"role":"resonator"} for x, L in TUBES]),
'''"""jb_vibraphone (jewelbox 08): aluminium bar + neighbour bars, gold resonators (meta.hanging) with fan discs on a motor shaft."""
'''+HDR+'''
TUBES = '''+repr([x for x, _ in TUBES])+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.016)]
    P += [C.prim('cyl', 1, loc=(x,0.06,0), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.46), verts=12) for x in (-0.14,0.14)]
    for x in (-0.47, 0.47):                                                                          # neighbour bars (behind the marble plane)
        P.append(C.prim('cube', 0 if False else 4, loc=(x,0.2,0.0), scale=(0.26,0.07,0.06), bevel=0.012))
    P.append(C.prim('cube', 3, loc=(0,0.245,-0.035), scale=(1.30,0.05,0.04), bevel=0.008))          # frame rail
    P.append(C.prim('cyl', 4, loc=(0,0.222,-0.09), rot=(0,math.pi/2,0), scale=(0.008,0.008,1.12), verts=12))   # motor shaft
    for x in TUBES:
        P.append(C.prim('cyl', 3, loc=(x,0.222,-0.09), rot=(0,math.pi/2,0), scale=(0.046,0.046,0.006), verts=24))  # fan discs
    P.append(C.prim('cube', 3, loc=(0.62,0.222,-0.10), scale=(0.08,0.07,0.06), bevel=0.01))         # motor box
    P.append(C.prim('cyl', 4, loc=(0.62,0.185,-0.10), rot=(math.pi/2,0,0), scale=(0.015,0.015,0.006), verts=16))
    return P
''',
'''"""jb_vibraphone materials (body = the struck bar; neighbour bars use the 'chrome' slot in a satin finish)"""
def shared(C):
    return {'cord': C.mat('jv_cord',(0.35,0.03,0.05),rough=0.8), 'resonator': C.mat('jv_res',(0.9,0.66,0.28),rough=0.22,metal=1.0),
            'dark': C.mat('jv_dark',(0.02,0.02,0.022),rough=0.45), 'chrome': C.mat('jv_alu2',(0.78,0.8,0.84),rough=0.28,metal=1.0,aniso=0.5)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.82,0.84,0.88),rough=0.24,metal=1.0,aniso=0.6)
''')

# ------------------------------------------------------------------ 10 xylophone (jewelbox)
write('jb_xylophone', dict(name='jb_xylophone', section=110, tracks_regex=NEVER,
  description='Jewelbox 10 Xylophone: rainbow bar coloured by pitch class (same scheme as piano/xylophone v5) with silver nail heads, in front of a '
              'kid-style rainbow xylophone icon: eight graded rainbow bars nailed on two converging maple rails, with two crossed red-ball mallets.',
  slots=['body','maple','rainbow0','rainbow1','silver','red','pin'], flash_slot='body', flash_color=[1.0,0.95,0.8],
  pins=[{"x":-0.2,"z":0.0,"y_start":0.17,"radius":0.022},{"x":0.2,"z":0.0,"y_start":0.17,"radius":0.022}]),
'''"""jb_xylophone (jewelbox 10): pitch-rainbow bar + rainbow xylophone icon (graded bars on maple rails, crossed mallets)."""
'''+HDR+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.014)]
    for x in (-0.2, 0.2): P.append(C.prim('sphere', 4, loc=(x,-0.0,0.04), scale=(0.018,0.018,0.005), verts=12))   # nail heads (flush)
    # rainbow icon below: 8 graded bars (vertical in the icon), maple rails behind them
    n = 8; X = [-0.42 + 0.84*i/(n-1) for i in range(n)]
    def railz(x, top): return (-0.11 if top else -0.43 + 0.16*(x+0.46)/0.92)
    for top in (True, False):
        za, zb = railz(-0.48, top), railz(0.48, top); L = math.hypot(0.96, zb-za)
        P.append(C.prim('cube', 1, loc=(0,0.245,(za+zb)/2), rot=(0,-math.atan2(zb-za,0.96),0), scale=(L,0.05,0.04), bevel=0.01))
    for i, x in enumerate(X):
        z0, z1 = railz(x, True) + 0.035, railz(x, False) - 0.035
        P.append(C.prim('cube', 2 + (i % 2), loc=(x,0.20,(z0+z1)/2), scale=(0.085,0.03,z0-z1), bevel=0.01))
        for z in (railz(x, True), railz(x, False)): P.append(C.prim('sphere', 4, loc=(x,0.183,z), scale=(0.011,0.006,0.011), verts=10))
    # crossed mallets in front of the icon
    for a, b in (((-0.30,-0.50), (0.20,-0.24)), ((0.30,-0.50), (-0.20,-0.24))):
        L = math.hypot(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 1, loc=((a[0]+b[0])/2,0.175,(a[1]+b[1])/2), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.008,0.008,L), verts=10))
        P.append(C.prim('sphere', 5, loc=(b[0],0.18,b[1]), scale=(0.024,0.022,0.024), verts=16))
    return P
''',
'''"""jb_xylophone materials: body by pitch class; icon bars alternate two rainbow ramps along x (object-space gradient)"""
def _ramp(C, name, offset):
    m = C.mat(name,(1,1,1),rough=0.35,coat=0.5); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); mp = nt.nodes.new('ShaderNodeMapRange')
    mp.inputs['From Min'].default_value = -0.46; mp.inputs['From Max'].default_value = 0.46
    mp.inputs['To Min'].default_value = 0.0; mp.inputs['To Max'].default_value = 0.8
    hsv = nt.nodes.new('ShaderNodeCombineColor'); hsv.mode = 'HSV'; hsv.inputs[1].default_value = 0.85; hsv.inputs[2].default_value = 0.6
    L = nt.links.new; L(tc.outputs['Object'], sep.inputs[0]); L(sep.outputs[0], mp.inputs['Value']); L(mp.outputs[0], hsv.inputs[0]); L(hsv.outputs[0], b.inputs['Base Color'])
    return m
def shared(C):
    return {'maple': C.add_wood(C.mat('jx_maple',(0.7,0.5,0.28),rough=0.4,coat=0.3),(0.62,0.42,0.22),(0.82,0.62,0.38),scale=7.0),
            'rainbow0': _ramp(C,'jx_rb0',0), 'rainbow1': _ramp(C,'jx_rb1',0), 'silver': C.mat('jx_silver',(0.85,0.85,0.88),rough=0.2,metal=1.0),
            'red': C.mat('jx_red',(0.7,0.04,0.04),rough=0.35,coat=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,C.pitch_rgb(note),rough=0.32,coat=0.6)
''')

# ------------------------------------------------------------------ 12 hammered dulcimer
write('dulcimer', dict(name='dulcimer', section=112, tracks_regex=NEVER,
  description='Jewelbox 12 Hammered Dulcimer (扬琴): walnut rail striker with five silver strings across its top, in front of a trapezoid spruce '
              'soundboard in a walnut frame with two gold rosettes, a dozen silver string courses, two dark bridges, and two crossed wooden hammers.',
  slots=['body','spruce','walnut','silver','gold','dark','pin'], flash_slot='body', flash_color=[1.0,0.8,0.5],
  pins=[{"x":-0.15,"z":-0.03,"y_start":0.2,"radius":0.022},{"x":0.15,"z":-0.03,"y_start":0.2,"radius":0.022}]),
'''"""dulcimer (jewelbox 12): string-topped walnut rail + trapezoid hammered dulcimer behind the marble plane."""
'''+HDR+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,-0.005), scale=(0.62,0.30,0.08), bevel=0.01)]                  # walnut rail, top z=0.035
    for y in (-0.10,-0.05,0.0,0.05,0.10):                                                           # strings across the top: top z = 0.045
        P.append(C.prim('cyl', 3, loc=(0,y,0.039), rot=(0,math.pi/2,0), scale=(0.006,0.006,0.60), verts=10))
    for x in (-0.27, 0.27):                                                                         # end bridges under the strings
        P.append(C.prim('cube', 5, loc=(x,0,0.034), scale=(0.02,0.27,0.012)))
    # trapezoid dulcimer below (long side at the bottom)
    def hw(z): return 0.32 + 0.18*(-0.07 - z)/0.33
    P.append(C.shape_profile('dc_frame', [(-0.55,-0.43),(0.55,-0.43),(0.35,-0.045),(-0.35,-0.045)], 0.05, 0.215, 2, bevel=0.012))
    P.append(C.shape_profile('dc_board', [(-hw(-0.40),-0.40),(hw(-0.40),-0.40),(hw(-0.07),-0.07),(-hw(-0.07),-0.07)], 0.02, 0.20, 1))
    for k in range(12):
        z = -0.095 - 0.025*k; h = hw(z) - 0.02
        P.append(C.prim('cyl', 3, loc=(0,0.195,z), rot=(0,math.pi/2,0), scale=(0.0035,0.0035,2*h), verts=8))
    for x0, x1 in ((-0.14,-0.18), (0.18,0.24)):                                                    # bridges (perpendicular to the strings)
        P.append(C.prim('cube', 5, loc=((x0+x1)/2,0.19,-0.235), rot=(0,math.atan2(x1-x0,0.30),0), scale=(0.02,0.014,0.31), bevel=0.003))
    for x, z in ((-0.33,-0.25), (0.02,-0.24)):                                                      # gold rosettes
        P.append(C.prim('torus', 4, loc=(x,0.198,z), rot=(math.pi/2,0,0), scale=(0.045,0.008), verts=32))
        P.append(C.prim('cyl', 5, loc=(x,0.199,z), rot=(math.pi/2,0,0), scale=(0.038,0.038,0.003), verts=24))
    # crossed hammers (thin canes with flat heads) lying in front
    for a, b in (((-0.42,-0.52), (0.10,-0.30)), ((0.42,-0.52), (-0.10,-0.30))):
        L = math.hypot(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 2, loc=((a[0]+b[0])/2,0.17,(a[1]+b[1])/2), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.006,0.006,L), verts=8))
        P.append(C.prim('cube', 2, loc=(b[0],0.168,b[1]), rot=(0,math.atan2(b[0]-a[0],b[1]-a[1]),0), scale=(0.05,0.022,0.018), bevel=0.006))
    return P
''',
'''"""dulcimer materials"""
def shared(C):
    return {'spruce': C.add_wood(C.mat('dc_spruce',(0.75,0.58,0.36),rough=0.45,coat=0.3),(0.68,0.50,0.30),(0.85,0.68,0.45),scale=5.0),
            'walnut': C.add_wood(C.mat('dc_walnut',(0.22,0.11,0.05),rough=0.35,coat=0.6),(0.12,0.05,0.02),(0.32,0.16,0.07),scale=8.0),
            'silver': C.mat('dc_silver',(0.88,0.88,0.9),rough=0.15,metal=1.0), 'gold': C.mat('dc_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'dark': C.mat('dc_dark',(0.06,0.03,0.02),rough=0.6)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.25,0.12,0.06),rough=0.3,coat=0.7),(0.14,0.06,0.025),(0.36,0.18,0.08),scale=8.0)
''')
print('wrote jewelbox F1 assets')
