"""Jewelbox Orchestra (珠匣乐团) - family 2 (13-24: organs, accordion, harmonica, guitars, basses, pizzicato strings, harp).
Reused unchanged: guitar (v5) for 18 Acoustic Guitar Steel. Every other folder is new and registry-only (tracks_regex NEVER).
Stringed instruments follow guitar v5: the striker is the strings (+ bridge / nut inside the contact rectangle) and the
instrument body is seen face-on behind the marble plane, centred on the striker."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER
from snippets import H, IVORY

KEYPINS = [{"x":-0.15,"z":-0.03,"y_start":0.2,"radius":0.022},{"x":0.15,"z":-0.03,"y_start":0.2,"radius":0.022}]
KEYS = dict(variants=['white', 'black'], variant_rule='pitch', pins=KEYPINS)
BODYPINS = [{"x":0.12,"z":-0.12,"y_start":0.24,"radius":0.022},{"x":-0.12,"z":-0.12,"y_start":0.24,"radius":0.022}]


# ------------------------------------------------------------------ 13 drawbar organ
write('drawbar_organ', dict(name='drawbar_organ', section=113, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 13 Drawbar Organ (tonewheel / B3 style): pitch-chosen key with waterfall edge on a walnut key bed, a bank of nine pulled-out '
              'drawbars (brown / white / black tabs on chrome rods) to its left, walnut console with chrome trim, two legs and a fan of wooden bass pedals.',
  slots=['body','walnut','chrome','tab_brown','tab_white','tab_black','pale','pin'], flash_slot='body', flash_color=[1.0,0.8,0.5]),
'''"""drawbar_organ (jewelbox 13): key + drawbar bank + walnut tonewheel console with pedalboard."""
'''+HDR+H+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.70,0.12,0.06), bevel=0.008))          # walnut key bed
    P += stubs(C, variant, 5)
    # drawbar bank (left of the keys): housing + 9 rods pulled to different lengths, tab colours brown brown white white black white black black white
    P.append(C.prim('cube', 1, loc=(-0.50,0.25,0.02), scale=(0.30,0.07,0.10), bevel=0.01))
    cols = [3,3,4,4,5,4,5,5,4]; Ls = [0.08,0.13,0.16,0.06,0.12,0.03,0.10,0.05,0.14]
    for i, (c, L) in enumerate(zip(cols, Ls)):
        x = -0.62 + 0.03*i
        P.append(C.prim('cyl', 2, loc=(x,0.22,0.07+L/2), scale=(0.006,0.006,L), verts=8))
        P.append(C.prim('cube', c, loc=(x,0.22,0.07+L+0.025), scale=(0.024,0.03,0.05), bevel=0.005))
    # console: walnut cabinet, chrome trim, two tapered legs, bass pedalboard
    P.append(C.prim('cube', 1, loc=(0,0.23,-0.19), scale=(1.12,0.12,0.22), bevel=0.02))
    P.append(C.prim('cube', 2, loc=(0,0.168,-0.085), scale=(1.10,0.008,0.012)))
    P.append(C.prim('cube', 1, loc=(0,0.20,-0.20), scale=(0.96,0.06,0.15), bevel=0.01))            # recessed front panel
    for x in (-0.50, 0.50):
        P.append(rod(C, (x,-0.30,0.22), (x*1.05,-0.52), 0.025, 1))
    for i in range(9):                                                                              # pedals fan out toward the player
        x = -0.32 + 0.08*i
        P.append(bar(C, (x*0.6,-0.40), (x,-0.53), 0.05, 0.03, 6 if i % 3 != 1 else 5, 0.20, bevel=0.006))
    P.append(C.prim('cube', 1, loc=(0,0.21,-0.555), scale=(0.84,0.08,0.025), bevel=0.006))
    return P
''',
'''"""drawbar_organ materials"""
def shared(C):
    return {'walnut': C.add_wood(C.mat('do_walnut',(0.2,0.09,0.04),rough=0.3,coat=0.7),(0.10,0.04,0.015),(0.30,0.14,0.06),scale=8.0),
            'chrome': C.mat('do_chrome',(0.9,0.9,0.92),rough=0.1,metal=1.0), 'tab_brown': C.mat('do_tbrown',(0.28,0.10,0.04),rough=0.3,coat=0.6),
            'tab_white': C.mat('do_twhite',(0.9,0.88,0.82),rough=0.3,coat=0.5), 'tab_black': C.mat('do_tblack',(0.015,0.015,0.015),rough=0.3,coat=0.6),
            'pale': C.add_wood(C.mat('do_pale',(0.7,0.5,0.28),rough=0.4),(0.62,0.42,0.22),(0.82,0.62,0.38),scale=7.0)}
'''+IVORY)

# ------------------------------------------------------------------ 14 church organ
write('church_organ', dict(name='church_organ', section=114, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 14 Church Organ: pitch-chosen key on a dark-oak console flanked by rows of ivory stop knobs, with a V-shaped facade of '
              'silver tin pipes (gold mouths, short in the middle so the marble sits in the notch) rising behind it from a carved oak impost '
              'between two gothic towers with gold pinnacles; console and pedalboard below.',
  slots=['body','oak','tin','gold','ivory','dark','pin'], flash_slot='body', flash_color=[1.0,0.9,0.65]),
'''"""church_organ (jewelbox 14): key + stop knobs + V facade of tin pipes in an oak case + console."""
'''+HDR+H+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.70,0.12,0.06), bevel=0.008))          # oak key bed
    P += stubs(C, variant, 5)
    for s in (-1, 1):                                                                               # stop jambs with ivory knobs
        P.append(C.prim('cube', 1, loc=(s*0.45,0.24,0.0), scale=(0.18,0.08,0.20), bevel=0.01))
        for r in range(3):
            for c in range(2):
                P.append(C.prim('cyl', 4, loc=(s*(0.41+0.07*c),0.19,-0.06+0.06*r), rot=(math.pi/2,0,0), scale=(0.017,0.017,0.03), verts=16))
    # impost + V facade of pipes
    P.append(C.prim('cube', 1, loc=(0,0.26,0.10), scale=(1.04,0.05,0.04), bevel=0.008))
    P.append(C.prim('cube', 3, loc=(0,0.234,0.12), scale=(1.04,0.004,0.006)))
    xs = [-0.40 + 0.08*i for i in range(11)]
    for x in xs:
        h = 0.10 + 0.62*abs(x); r = 0.024 + 0.012*abs(x)
        P.append(C.prim('cyl', 2, loc=(x,0.255,0.12+0.04), scale=(r*0.45,r*0.45,0.08), verts=16))      # conical foot (thin)
        P.append(C.prim('cyl', 2, loc=(x,0.255,0.20+h/2), scale=(r,r,h), verts=24))
        P.append(C.prim('cube', 3, loc=(x,0.255-r,0.225), scale=(r*1.1,0.006,0.03)))                 # gold mouth
    for s in (-1, 1):                                                                               # gothic towers
        P.append(C.prim('cube', 1, loc=(s*0.55,0.26,0.27), scale=(0.08,0.05,0.38), bevel=0.01))
        P.append(C.shape_profile('co_spire', [(s*0.51,0.46),(s*0.59,0.46),(s*0.55,0.56)], 0.05, 0.235, 1))
        P.append(C.prim('sphere', 3, loc=(s*0.55,0.235,0.575), scale=(0.02,0.02,0.02), verts=12))
    # console + pedalboard
    P.append(C.prim('cube', 1, loc=(0,0.23,-0.20), scale=(1.06,0.12,0.24), bevel=0.02))
    P.append(C.prim('cube', 3, loc=(0,0.168,-0.09), scale=(1.0,0.008,0.012)))
    for i in range(9):
        x = -0.32 + 0.08*i
        P.append(C.prim('cube', 5 if i % 3 == 1 else 1, loc=(x,0.20,-0.36), scale=(0.055,0.06,0.025), bevel=0.006))
    P.append(C.prim('cube', 1, loc=(0,0.21,-0.385), scale=(0.84,0.08,0.025), bevel=0.006))
    return P
''',
'''"""church_organ materials"""
def shared(C):
    return {'oak': C.add_wood(C.mat('co_oak',(0.22,0.12,0.06),rough=0.4,coat=0.4),(0.12,0.06,0.03),(0.30,0.17,0.08),scale=6.0),
            'tin': C.mat('co_tin',(0.82,0.83,0.86),rough=0.18,metal=1.0), 'gold': C.mat('co_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'ivory': C.mat('co_ivory',(0.9,0.86,0.76),rough=0.25,coat=0.5), 'dark': C.mat('co_dark',(0.015,0.012,0.01),rough=0.4,coat=0.5)}
'''+IVORY)

# ------------------------------------------------------------------ 15 accordion
write('accordion', dict(name='accordion', section=115, tracks_regex=NEVER, **KEYS,
  description='Jewelbox 15 Accordion: pitch-chosen key on a red-pearl key bed, in front of a face-on piano accordion: red pearloid treble box with '
              'a chrome diamond-lattice grille, black/white pleated bellows with chrome corner guards, bass box with a grid of buttons and a strap.',
  slots=['body','pearl','chrome','bel_dark','bel_white','button','pin'], flash_slot='body', flash_color=[1.0,0.7,0.6]),
'''"""accordion (jewelbox 15): key + face-on red pearl accordion (grille, bellows, bass buttons)."""
'''+HDR+H+'''
def build(C, variant='white'):
    P = [key(C, variant)]
    P.append(C.prim('cube', 1, loc=(0,0.235,-0.035), scale=(0.70,0.12,0.06), bevel=0.008))          # red pearl key bed
    P += stubs(C, variant, 3)
    zc, hz = -0.25, 0.34
    # treble box (left) with grille
    P.append(C.prim('cube', 1, loc=(-0.42,0.23,zc), scale=(0.30,0.12,hz), bevel=0.025))
    P.append(C.prim('cube', 3, loc=(-0.42,0.168,zc), scale=(0.24,0.006,hz-0.07)))
    X0, X1, Z0, Z1 = -0.53, -0.31, zc-0.13, zc+0.13                                                # diamond lattice clipped to the grille
    for sgn in (1, -1):
        for k in range(-8, 9):
            c = 0.05*k; seg = []                                                                    # line z - zc = sgn*(x - (-0.42)) + c
            for x in (X0, X1):
                z = zc + sgn*(x+0.42) + c
                if Z0 <= z <= Z1: seg.append((x, z))
            for z in (Z0, Z1):
                x = -0.42 + sgn*(z - zc - c)
                if X0 <= x <= X1: seg.append((x, z))
            seg = sorted(set((round(x,5), round(z,5)) for x, z in seg))
            if len(seg) >= 2 and math.hypot(seg[-1][0]-seg[0][0], seg[-1][1]-seg[0][1]) > 0.02:
                P.append(bar(C, seg[0], seg[-1], 0.008, 0.008, 2, 0.163))
    # trim the lattice visually with a chrome frame
    P.append(C.prim('cube', 2, loc=(-0.42,0.162,zc+hz/2-0.03), scale=(0.25,0.006,0.012)))
    P.append(C.prim('cube', 2, loc=(-0.42,0.162,zc-hz/2+0.03), scale=(0.25,0.006,0.012)))
    # bellows: alternating pleats
    for i in range(13):
        x = -0.255 + 0.04*i
        P.append(C.prim('cube', 3 if i % 2 == 0 else 4, loc=(x,0.22,zc), scale=(0.04,0.10,hz-0.02), bevel=0.004))
    for x in (-0.25, 0.23):
        for z in (zc+hz/2-0.02, zc-hz/2+0.02):
            P.append(C.prim('cube', 2, loc=(x,0.168,z), scale=(0.03,0.01,0.03), bevel=0.004))
    # bass box (right) with buttons + strap
    P.append(C.prim('cube', 1, loc=(0.40,0.23,zc), scale=(0.28,0.12,hz), bevel=0.025))
    for r in range(5):
        for c in range(4):
            P.append(C.prim('sphere', 5 if (r+c) % 3 else 3, loc=(0.32+0.05*c+0.012*r,0.168,zc-0.11+0.055*r), scale=(0.016,0.01,0.016), verts=12))
    P.append(C.prim('cube', 3, loc=(0.54,0.16,zc), scale=(0.025,0.01,hz-0.06), bevel=0.004))       # strap
    return P
''',
'''"""accordion materials (pearl = red pearloid celluloid)"""
def shared(C):
    return {'pearl': C.mat('ac_pearl',(0.55,0.02,0.03),rough=0.12,coat=1.0), 'chrome': C.mat('ac_chrome',(0.9,0.9,0.92),rough=0.1,metal=1.0),
            'bel_dark': C.mat('ac_bdark',(0.02,0.02,0.025),rough=0.5), 'bel_white': C.mat('ac_bwhite',(0.85,0.84,0.8),rough=0.5),
            'button': C.mat('ac_button',(0.92,0.9,0.85),rough=0.2,coat=0.6)}
'''+IVORY)

# ------------------------------------------------------------------ 16 harmonica
write('harmonica', dict(name='harmonica', section=116, tracks_regex=NEVER, pins=KEYPINS,
  description='Jewelbox 16 Harmonica: the striker IS a ten-hole diatonic harmonica - polished chrome cover plates top and bottom with screws, '
              'a honey pear-wood comb in between showing ten dark holes toward the camera - lying on an open red tin case with a blue velvet bed, '
              'gold rims and a second (smaller) harmonica in the case.',
  slots=['body','comb','dark','tin','velvet','gold','pin'], flash_slot='body', flash_color=[0.75,0.85,1.0]),
'''"""harmonica (jewelbox 16): chrome-covered ten-hole harmonica striker + open red tin case."""
'''+HDR+H+'''
def build(C, variant=None):
    P = []
    P.append(C.prim('cube', 0, loc=(0,0,0.0315), scale=(0.62,0.30,0.027), bevel=0.01))              # top cover (contact top z=0.045)
    P.append(C.prim('cube', 0, loc=(0,0,-0.0315), scale=(0.62,0.30,0.027), bevel=0.01))             # bottom cover
    P.append(C.prim('cube', 1, loc=(0,0.005,0.0), scale=(0.56,0.28,0.036)))                          # comb
    for i in range(10):                                                                             # holes on the camera side
        P.append(C.prim('cube', 2, loc=(-0.243+0.054*i,-0.133,0.0), scale=(0.03,0.012,0.022)))
    for x in (-0.27, 0.27):                                                                         # cover screws
        P.append(C.prim('cyl', 5, loc=(x,-0.06,0.042), scale=(0.012,0.012,0.004), verts=12))
    # open tin case below (camera-facing), velvet bed, gold rims, spare harmonica
    P.append(C.prim('cube', 3, loc=(0,0.24,-0.22), scale=(0.84,0.09,0.24), bevel=0.02))
    P.append(C.prim('cube', 4, loc=(0,0.19,-0.22), scale=(0.76,0.02,0.18), bevel=0.01))
    P.append(C.prim('cube', 5, loc=(0,0.183,-0.22), scale=(0.80,0.006,0.012)))
    P.append(C.prim('cube', 5, loc=(0,0.183,-0.105), scale=(0.84,0.006,0.012)))
    P.append(C.prim('cube', 5, loc=(0,0.183,-0.335), scale=(0.84,0.006,0.012)))
    P.append(C.prim('cube', 0, loc=(0.05,0.172,-0.27), scale=(0.46,0.02,0.035), bevel=0.006))       # spare harmonica (front face)
    P.append(C.prim('cube', 1, loc=(0.05,0.166,-0.27), scale=(0.42,0.006,0.016)))
    for i in range(8):
        P.append(C.prim('cube', 2, loc=(-0.12+0.048*i,0.162,-0.27), scale=(0.022,0.004,0.01)))
    P.append(C.prim('sphere', 5, loc=(-0.36,0.175,-0.16), scale=(0.025,0.01,0.025), verts=12))       # case latch
    return P
''',
'''"""harmonica materials"""
def shared(C):
    return {'comb': C.add_wood(C.mat('hm_comb',(0.6,0.38,0.16),rough=0.4,coat=0.4),(0.5,0.3,0.12),(0.72,0.48,0.22),scale=10.0),
            'dark': C.mat('hm_dark',(0.01,0.01,0.01),rough=0.8), 'tin': C.mat('hm_tin',(0.6,0.03,0.03),rough=0.25,metal=0.4,coat=0.8),
            'velvet': C.mat('hm_velvet',(0.03,0.06,0.3),rough=0.95), 'gold': C.mat('hm_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.88,0.89,0.92),rough=0.08,metal=1.0)
''')

# ------------------------------------------------------------------ 17 nylon guitar
write('nylon_guitar', dict(name='nylon_guitar', section=117, tracks_regex=NEVER, pins=BODYPINS,
  description='Jewelbox 17 Acoustic Guitar Nylon (classical): three clear-white nylon trebles and three silver-wound basses (the striker) over a '
              'pale spruce classical body face-on - wide figure-of-eight outline with rosewood binding, green/gold mosaic rosette, tie-block bridge - '
              'cedar neck and a slotted headstock with white rollers and side tuners (adapted from guitar v5, which keeps the steel-string sunburst).',
  slots=['body','nylon','wound','rosewood','dark','mosaic','pin'], flash_slot='body', flash_slots=['body','nylon','wound'], flash_color=[1.0,0.9,0.65]),
'''"""nylon_guitar (jewelbox 17): nylon/wound strings + pale spruce classical guitar with slotted headstock."""
'''+HDR+H+'''
def build(C, variant=None):
    yb = 0.19
    ins = lambda x, z: math.hypot(x-0.12, z) < 0.235 or math.hypot(x+0.19, z) < 0.185 or (abs(x+0.03) < 0.13 and abs(z) < 0.165)
    P = [plate(C, 'ng_top', ins, yb, 0.06, 0, cx=-0.02)]
    P.append(plate(C, 'ng_bind', lambda x, z: ins(x, z), yb+0.004, 0.05, 3, cx=-0.02, bevel=0.0))
    P[-1].scale = (1.03, 1.0, 1.03)
    P.append(C.prim('cyl', 4, loc=(-0.12,yb-0.004,0.0), rot=(math.pi/2,0,0), scale=(0.066,0.066,0.006), verts=48))   # sound hole
    P.append(C.prim('torus', 5, loc=(-0.12,yb-0.005,0.0), rot=(math.pi/2,0,0), scale=(0.088,0.014), verts=64))      # mosaic rosette
    P.append(C.prim('torus', 3, loc=(-0.12,yb-0.005,0.0), rot=(math.pi/2,0,0), scale=(0.108,0.005), verts=64))
    P.append(C.prim('cube', 3, loc=(0.2,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))           # tie-block bridge (in the contact rectangle)
    P.append(C.prim('cube', 1, loc=(0.2,0.0,0.036), scale=(0.01,0.24,0.006)))
    P.append(C.prim('cube', 1, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))                   # nut
    P.append(C.prim('cube', 3, loc=(-0.49,yb-0.006,0.0), scale=(0.40,0.05,0.085), bevel=0.008))     # neck / fingerboard
    for x in (-0.36,-0.41,-0.46,-0.51,-0.56,-0.61,-0.66): P.append(C.prim('cube', 2, loc=(x,yb-0.028,0.0), scale=(0.006,0.006,0.09)))
    P.append(C.prim('cube', 3, loc=(-0.78,yb,0.0), scale=(0.18,0.05,0.11), bevel=0.012))           # slotted headstock
    for z in (-0.025, 0.025):
        P.append(C.prim('cube', 4, loc=(-0.78,yb-0.022,z), scale=(0.13,0.02,0.018)))
        for x in (-0.82,-0.78,-0.74): P.append(C.prim('cyl', 1, loc=(x,yb-0.024,z), scale=(0.008,0.008,0.016), verts=8))
    for x in (-0.82,-0.78,-0.74):
        for s in (-1, 1): P.append(C.prim('cyl', 2, loc=(x,yb,s*0.075), scale=(0.012,0.012,0.04), verts=12))
    P += strings(C, (-0.095,-0.057,-0.019,0.019,0.057,0.095), [2,2,2,1,1,1], 0.0135, 0.0009)
    return P
''',
'''"""nylon_guitar materials"""
def shared(C):
    return {'nylon': C.mat('ng_nylon',(0.92,0.9,0.84),rough=0.25,coat=0.6), 'wound': C.mat('ng_wound',(0.75,0.72,0.66),rough=0.3,metal=1.0),
            'rosewood': C.add_wood(C.mat('ng_rose',(0.08,0.03,0.015),rough=0.35,coat=0.5),(0.04,0.015,0.008),(0.14,0.06,0.025),scale=9.0),
            'dark': C.mat('ng_dark',(0.006,0.004,0.003),rough=0.9), 'mosaic': C.mat('ng_mosaic',(0.06,0.25,0.12),rough=0.4,coat=0.5)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.72,0.5,0.24),rough=0.35,coat=0.6),(0.62,0.4,0.17),(0.84,0.62,0.32),scale=6.0)
''')

# ------------------------------------------------------------------ 19 electric guitar (clean)
STRAT = [(0.36,0.0),(0.35,0.12),(0.30,0.20),(0.20,0.23),(0.08,0.20),(0.00,0.15),(-0.08,0.17),(-0.18,0.21),(-0.25,0.18),(-0.20,0.11),(-0.12,0.065),
         (-0.12,-0.065),(-0.15,-0.08),(-0.21,-0.13),(-0.17,-0.18),(-0.06,-0.15),(0.02,-0.17),(0.12,-0.23),(0.26,-0.21),(0.34,-0.12)]
write('electric_guitar', dict(name='electric_guitar', section=119, tracks_regex=NEVER, pins=BODYPINS,
  description='Jewelbox 19 Electric Guitar Clean: six nickel strings (the striker) over a sky-blue double-cutaway solid body with a white pickguard, '
              'three white single-coil pickups, white knobs and a chrome tremolo bridge, maple neck with dot inlays and a six-in-line headstock.',
  slots=['body','nickel','guard','maple','dark','chrome','pin'], flash_slot='body', flash_slots=['body','nickel'], flash_color=[0.6,0.85,1.0]),
'''"""electric_guitar (jewelbox 19): nickel strings + sky-blue double-cutaway solid body, white guard, maple neck."""
'''+HDR+H+'''
STRAT = '''+repr(STRAT)+'''
def build(C, variant=None):
    yb = 0.19
    P = [C.shape_profile('eg_body', STRAT, 0.05, yb, 0, bevel=0.02)]
    guard = [(0.04+(x-0.04)*0.78, z*0.78) for x, z in STRAT]
    P.append(C.shape_profile('eg_guard', [(x, z) for x, z in guard if x < 0.27], 0.006, yb-0.006, 2, bevel=0.002))
    for x in (-0.03, 0.06, 0.15):                                                                   # single coils
        P.append(C.prim('cube', 2, loc=(x,yb-0.012,0.0), rot=(0,0.08 if x > 0.1 else 0,0), scale=(0.035,0.01,0.15), bevel=0.012))
    for x, z in ((0.20,-0.10),(0.25,-0.06),(0.29,-0.13)):
        P.append(C.prim('cyl', 2, loc=(x,yb-0.014,z), rot=(math.pi/2,0,0), scale=(0.02,0.02,0.016), verts=16))
    P.append(C.prim('cube', 5, loc=(0.24,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))          # tremolo bridge (in the contact rectangle)
    P.append(C.prim('cube', 3, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))                   # nut
    P.append(C.prim('cube', 3, loc=(-0.45,yb-0.006,0.0), scale=(0.66,0.05,0.08), bevel=0.008))     # maple neck
    for x in (-0.33,-0.40,-0.47,-0.54,-0.61,-0.68): P.append(C.prim('cube', 5, loc=(x,yb-0.029,0.0), scale=(0.005,0.005,0.085)))
    for x in (-0.365,-0.435,-0.505,-0.645): P.append(C.prim('cyl', 4, loc=(x,yb-0.029,0.0), rot=(math.pi/2,0,0), scale=(0.01,0.01,0.004), verts=12))
    P.append(C.shape_profile('eg_head', [(-0.77,-0.04),(-0.92,-0.03),(-0.97,0.03),(-0.92,0.085),(-0.80,0.08),(-0.77,0.04)], 0.05, yb, 3, bevel=0.01))
    for i in range(6): P.append(C.prim('cyl', 5, loc=(-0.79-0.028*i,yb,0.085+0.004*i), scale=(0.009,0.009,0.04), verts=10))
    P += strings(C, (-0.095,-0.057,-0.019,0.019,0.057,0.095), 1, 0.012, 0.0012)
    return P
''',
'''"""electric_guitar materials"""
def shared(C):
    return {'nickel': C.mat('eg_nickel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'guard': C.mat('eg_guard',(0.92,0.9,0.86),rough=0.3,coat=0.5),
            'maple': C.add_wood(C.mat('eg_maple',(0.8,0.6,0.32),rough=0.3,coat=0.7),(0.74,0.54,0.28),(0.9,0.72,0.42),scale=7.0),
            'dark': C.mat('eg_dark',(0.02,0.015,0.01),rough=0.5), 'chrome': C.mat('eg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.12,0.42,0.75),rough=0.15,coat=1.0)
''')

# ------------------------------------------------------------------ 20 distortion guitar
VEE = [(-0.22,0.06),(-0.22,-0.06),(0.42,-0.27),(0.49,-0.205),(0.13,0.0),(0.49,0.205),(0.42,0.27)]
write('distortion_guitar', dict(name='distortion_guitar', section=120, tracks_regex=NEVER,
  pins=[{"x":0.0,"z":0.05,"y_start":0.24,"radius":0.022},{"x":0.0,"z":-0.05,"y_start":0.24,"radius":0.022}],
  description='Jewelbox 20 Distortion Guitar: six chrome strings (the striker) over a glossy red V-shaped rock guitar with white binding, two black '
              'humbuckers with chrome poles, black arrow headstock on a rosewood neck, plugged by a coiled cable into a black mini amp stack with '
              'a gold-framed grille and chrome knobs below it.',
  slots=['body','chrome','black','white','rosewood','gold','grille','pin'], flash_slot='body', flash_slots=['body','chrome'], flash_color=[1.0,0.35,0.25]),
'''"""distortion_guitar (jewelbox 20): chrome strings + red V guitar + mini amp stack."""
'''+HDR+H+'''
VEE = '''+repr(VEE)+'''
def build(C, variant=None):
    yb = 0.19
    P = [C.shape_profile('dg_body', VEE, 0.05, yb, 0, bevel=0.015)]
    P.append(C.shape_profile('dg_bind', VEE, 0.04, yb+0.005, 3, bevel=0.0)); P[-1].scale = (1.025, 1.0, 1.04)
    for x in (-0.12, -0.02):                                                                        # humbuckers
        P.append(C.prim('cube', 2, loc=(x,yb-0.012,0.0), scale=(0.06,0.012,0.16), bevel=0.008))
        for z in (-0.05,-0.017,0.017,0.05): P.append(C.prim('cyl', 1, loc=(x,yb-0.019,z), rot=(math.pi/2,0,0), scale=(0.008,0.008,0.004), verts=8))
    for x, z in ((0.25,-0.14),(0.33,-0.18),(0.25,0.14)):
        P.append(C.prim('cyl', 1, loc=(x,yb-0.012,z), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.014), verts=16))
    P.append(C.prim('cube', 1, loc=(0.10,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))          # tune-o-matic bridge
    P.append(C.prim('cube', 3, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P.append(C.prim('cube', 4, loc=(-0.47,yb-0.006,0.0), scale=(0.60,0.05,0.075), bevel=0.008))
    for x in (-0.33,-0.40,-0.47,-0.54,-0.61,-0.68): P.append(C.prim('cube', 1, loc=(x,yb-0.029,0.0), scale=(0.005,0.005,0.08)))
    P.append(C.shape_profile('dg_head', [(-0.76,-0.045),(-0.98,-0.07),(-0.92,0.0),(-0.98,0.07),(-0.76,0.045)], 0.05, yb, 2, bevel=0.008))
    for i in range(3):
        for s in (-1, 1): P.append(C.prim('cyl', 1, loc=(-0.80-0.05*i,yb,s*(0.065+0.008*i)), scale=(0.009,0.009,0.03), verts=10))
    # coiled cable from the lower wing to the amp
    for i in range(7): P.append(C.prim('torus', 2, loc=(0.44,yb-0.01,-0.27-0.028*i), rot=(0.3,0,0), scale=(0.02,0.006), verts=14))
    # mini amp stack
    P.append(C.prim('cube', 2, loc=(0.12,0.24,-0.42), scale=(0.46,0.09,0.20), bevel=0.015))
    P.append(C.prim('cube', 5, loc=(0.12,0.193,-0.44), scale=(0.40,0.006,0.13), bevel=0.003))
    P.append(C.prim('cube', 6, loc=(0.12,0.19,-0.44), scale=(0.37,0.006,0.11)))
    for i in range(6): P.append(C.prim('cyl', 1, loc=(-0.06+0.06*i,0.19,-0.345), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.01), verts=12))
    P += strings(C, (-0.095,-0.057,-0.019,0.019,0.057,0.095), 1, 0.012, 0.0012)
    return P
''',
'''"""distortion_guitar materials"""
def shared(C):
    return {'chrome': C.mat('dg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0), 'black': C.mat('dg_black',(0.012,0.012,0.012),rough=0.3,coat=0.6),
            'white': C.mat('dg_white',(0.9,0.88,0.84),rough=0.3,coat=0.5),
            'rosewood': C.add_wood(C.mat('dg_rose',(0.08,0.03,0.015),rough=0.35,coat=0.5),(0.04,0.015,0.008),(0.14,0.06,0.025),scale=9.0),
            'gold': C.mat('dg_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0), 'grille': C.mat('dg_grille',(0.05,0.045,0.04),rough=0.9)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.6,0.01,0.015),rough=0.1,coat=1.0)
''')

# ------------------------------------------------------------------ 21 acoustic (upright) bass
write('upright_bass', dict(name='upright_bass', section=121, tracks_regex=NEVER, pins=BODYPINS,
  description='Jewelbox 21 Acoustic Bass (jazz upright, plucked): four thick gut strings (the striker) over a large dark-amber violin-family body '
              'face-on - sloping upper bouts, C-bouts, f-holes, ebony fingerboard, tall maple bridge, black tailpiece and chrome end-pin - with a '
              'long neck ending in a carved scroll and four brass tuning machines. No bow (the orchestral contrabass, 28, gets one).',
  slots=['body','gut','ebony','maple','dark','brass','pin'], flash_slot='body', flash_slots=['body','gut'], flash_color=[1.0,0.75,0.4]),
'''"""upright_bass (jewelbox 21): gut strings + honey violin-family body, scroll, end-pin (no bow)."""
'''+HDR+H+'''
def build(C, variant=None):
    yb = 0.19; L = 0.78; ox = 0.06
    P = [plate(C, 'ub_body', violin_inside(L, ox), yb, 0.07, 0, cx=ox, n=200)]
    P.append(plate(C, 'ub_edge', violin_inside(L, ox), yb+0.006, 0.06, 4, cx=ox, n=200, bevel=0.0)); P[-1].scale = (1.02, 1.0, 1.03)
    for s in (-1, 1):                                                                              # f-holes
        P.append(bar(C, (ox+0.02,s*0.07), (ox+0.13,s*0.10), 0.012, 0.006, 4, yb-0.004))
        P.append(C.prim('cyl', 4, loc=(ox+0.02,yb-0.004,s*0.065), rot=(math.pi/2,0,0), scale=(0.014,0.014,0.006), verts=12))
        P.append(C.prim('cyl', 4, loc=(ox+0.14,yb-0.004,s*0.105), rot=(math.pi/2,0,0), scale=(0.014,0.014,0.006), verts=12))
    P.append(C.prim('cube', 3, loc=(0.15,0.04,0.015), scale=(0.03,0.30,0.035), bevel=0.004))       # tall maple bridge (in the contact rectangle)
    P.append(C.shape_profile('ub_tail', [(0.30,-0.06),(0.46,-0.035),(0.46,0.035),(0.30,0.06)], 0.02, yb-0.02, 2, bevel=0.006))
    P.append(C.prim('cyl', 5, loc=(0.52,yb,0.0), rot=(0,math.pi/2,0), scale=(0.012,0.012,0.12), verts=12))        # end-pin
    P.append(C.prim('cube', 2, loc=(-0.25,yb-0.02,0.0), scale=(0.70,0.03,0.07), bevel=0.006))      # ebony fingerboard
    P.append(C.prim('cube', 0, loc=(-0.72,yb,0.0), scale=(0.22,0.05,0.06), bevel=0.01))            # neck / pegbox
    P.append(C.prim('torus', 0, loc=(-0.86,yb,0.0), rot=(math.pi/2,0,0), scale=(0.035,0.018), verts=24))         # scroll
    P.append(C.prim('sphere', 0, loc=(-0.86,yb,0.0), scale=(0.025,0.03,0.025), verts=16))
    for x in (-0.66,-0.74):
        for s in (-1, 1): P.append(C.prim('cyl', 5, loc=(x,yb,s*0.06), scale=(0.012,0.012,0.06), verts=10))
    P += strings(C, (-0.075,-0.025,0.025,0.075), 1, 0.017, 0.0015)
    return P
''',
'''"""upright_bass materials"""
def shared(C):
    return {'gut': C.mat('ub_gut',(0.55,0.42,0.25),rough=0.45), 'ebony': C.mat('ub_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5),
            'maple': C.mat('ub_maple',(0.82,0.7,0.5),rough=0.4), 'dark': C.mat('ub_dark',(0.05,0.02,0.008),rough=0.6),
            'brass': C.mat('ub_brass',(0.9,0.68,0.3),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.36,0.13,0.03),rough=0.25,coat=0.8),(0.26,0.08,0.02),(0.5,0.2,0.05),scale=6.0)
''')

# ------------------------------------------------------------------ 22 fretless bass
JAZZ = [(0.40,0.0),(0.39,0.14),(0.32,0.23),(0.20,0.25),(0.09,0.20),(0.0,0.155),(-0.09,0.18),(-0.19,0.23),(-0.27,0.20),(-0.21,0.11),(-0.12,0.06),
        (-0.12,-0.06),(-0.16,-0.08),(-0.24,-0.12),(-0.20,-0.18),(-0.08,-0.165),(0.03,-0.20),(0.15,-0.26),(0.30,-0.24),(0.38,-0.14)]
write('fretless_bass', dict(name='fretless_bass', section=122, tracks_regex=NEVER, pins=BODYPINS,
  description='Jewelbox 22 Fretless Bass: four thick roundwound strings (the striker) over a deep-violet offset-waist solid bass with a tortoiseshell '
              'pickguard, two black pickups, chrome control plate and knobs, a long ebony fingerboard with fret LINES but no frets, and a big '
              'four-in-line headstock with chrome tuners.',
  slots=['body','steel','tort','ebony','line','chrome','pin'], flash_slot='body', flash_slots=['body','steel'], flash_color=[0.8,0.6,1.0]),
'''"""fretless_bass (jewelbox 22): 4 strings + violet offset-waist bass, tortoise guard, lined fretless ebony board."""
'''+HDR+H+'''
JAZZ = '''+repr(JAZZ)+'''
def build(C, variant=None):
    yb = 0.19
    P = [C.shape_profile('fb_body', JAZZ, 0.05, yb, 0, bevel=0.02)]
    guard = [(0.0+(x-0.0)*0.8, z*0.8) for x, z in JAZZ]
    P.append(C.shape_profile('fb_guard', [(x, z) for x, z in guard if x < 0.24], 0.006, yb-0.006, 2, bevel=0.002))
    for x in (0.0, 0.14): P.append(C.prim('cube', 4, loc=(x,yb-0.012,0.0), scale=(0.04,0.01,0.16), bevel=0.01))
    P.append(bar(C, (0.20,-0.15), (0.34,-0.09), 0.06, 0.008, 5, yb-0.01, bevel=0.01))
    for x, z in ((0.23,-0.14),(0.31,-0.10)): P.append(C.prim('cyl', 5, loc=(x,yb-0.018,z), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.016), verts=16))
    P.append(C.prim('cube', 5, loc=(0.24,0.04,0.02), scale=(0.07,0.30,0.03), bevel=0.006))          # bridge
    P.append(C.prim('cube', 4, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P.append(C.prim('cube', 3, loc=(-0.52,yb-0.006,0.0), scale=(0.80,0.05,0.075), bevel=0.008))     # long ebony fretless board
    for i in range(10): P.append(C.prim('cube', 4, loc=(-0.20-0.07*i,yb-0.029,0.0), scale=(0.004,0.004,0.08)))
    P.append(C.shape_profile('fb_head', [(-0.92,-0.04),(-1.14,-0.03),(-1.18,0.03),(-1.12,0.09),(-0.96,0.085),(-0.92,0.04)], 0.05, yb, 0, bevel=0.012))
    for i in range(4):
        P.append(C.prim('cyl', 5, loc=(-0.97-0.05*i,yb,0.10+0.004*i), scale=(0.014,0.014,0.05), verts=12))
        P.append(C.prim('cyl', 5, loc=(-0.97-0.05*i,yb-0.03,0.04), rot=(math.pi/2,0,0), scale=(0.015,0.015,0.01), verts=12))
    P += strings(C, (-0.075,-0.025,0.025,0.075), 1, 0.016, 0.0018)
    return P
''',
'''"""fretless_bass materials (line = the white fret-position lines on the fretless board)"""
def shared(C):
    m = C.mat('fb_tort',(0.25,0.08,0.02),rough=0.2,coat=0.8); C.add_wood(m,(0.06,0.02,0.005),(0.45,0.16,0.04),scale=14.0)
    return {'steel': C.mat('fb_steel',(0.75,0.75,0.74),rough=0.3,metal=1.0), 'tort': m,
            'ebony': C.mat('fb_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'line': C.mat('fb_line',(0.9,0.9,0.86),rough=0.3),
            'chrome': C.mat('fb_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.18,0.04,0.34),rough=0.15,coat=1.0)
''')

# ------------------------------------------------------------------ 23 pizzicato strings
write('pizzicato', dict(name='pizzicato', section=123, tracks_regex=NEVER,
  pins=[{"x":0.0,"z":-0.12,"y_start":0.24,"radius":0.022},{"x":0.0,"z":0.12,"y_start":0.24,"radius":0.022}],
  description='Jewelbox 23 Pizzicato Strings: four gut strings (the striker, plucked - no bow anywhere) over a string SECTION: three small violins '
              'fanned out face-on (golden, orange and red-brown varnish, black fingerboards, f-holes, scrolls) behind the marble plane.',
  slots=['body','gut','ebony','v2','v3','dark','pin'], flash_slot='body', flash_slots=['body','gut'], flash_color=[1.0,0.8,0.45]),
'''"""pizzicato (jewelbox 23): gut strings + three fanned small violins (string section, no bow)."""
'''+HDR+H+'''
def violin(C, cx, cz, ang, y, mi, L=0.48):
    import mathutils
    parts = [plate(C, 'pz_v', violin_inside(L, 0.0), y, 0.035, mi, n=140, bevel=0.008)]
    parts.append(C.prim('cube', 2, loc=(-0.26*L/0.4,y-0.008,0.0), scale=(0.40*L/0.4,0.012,0.04), bevel=0.004))
    for s in (-1, 1): parts.append(bar(C, (0.0,s*0.035), (0.06,s*0.05), 0.008, 0.004, 5, y-0.003))
    parts.append(C.prim('torus', mi, loc=(-0.42*L/0.4,y,0.0), rot=(math.pi/2,0,0), scale=(0.022,0.011), verts=20))
    parts.append(C.prim('cube', 2, loc=(0.17*L/0.4,y-0.008,0.0), scale=(0.08,0.012,0.04), bevel=0.004))    # tailpiece
    o = C.join(parts, 'pz_violin'); o.rotation_euler = (0, -ang, 0); o.location = (cx, 0, cz)
    C._activate(o); __import__('bpy').ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
def build(C, variant=None):
    P = [violin(C, 0.05, 0.12, 0.35, 0.235, 3), violin(C, 0.08, -0.12, -0.35, 0.215, 4), violin(C, -0.02, 0.0, 0.0, 0.19, 0)]
    P.append(C.prim('cube', 3, loc=(0.18,0.04,0.015), scale=(0.025,0.30,0.035), bevel=0.004))       # bridge (in the contact rectangle)
    P.append(C.prim('cube', 2, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))
    P += strings(C, (-0.075,-0.025,0.025,0.075), 1, 0.010, 0.001)
    return P
''',
'''"""pizzicato materials: body = front violin (golden), v2/v3 = the two behind"""
def shared(C):
    return {'gut': C.mat('pz_gut',(0.7,0.58,0.38),rough=0.4), 'ebony': C.mat('pz_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5),
            'v2': C.add_wood(C.mat('pz_v2',(0.55,0.22,0.06),rough=0.25,coat=0.8),(0.42,0.15,0.04),(0.68,0.3,0.1),scale=6.0),
            'v3': C.add_wood(C.mat('pz_v3',(0.32,0.09,0.03),rough=0.25,coat=0.8),(0.22,0.06,0.02),(0.42,0.13,0.05),scale=6.0),
            'dark': C.mat('pz_dark',(0.02,0.01,0.005),rough=0.7)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.75,0.45,0.12),rough=0.25,coat=0.8),(0.62,0.34,0.08),(0.88,0.58,0.2),scale=6.0)
''')

# ------------------------------------------------------------------ 24 orchestral harp
write('harp', dict(name='harp', section=124, tracks_regex=NEVER, pins=KEYPINS,
  description='Jewelbox 24 Orchestral Harp: the gilt carved harp neck is the striker; below it a concert harp in side elevation - fluted gold column '
              'with a crown on the left, maple soundboard slanting down to the gilt base with pedals, and a fan of strings (red C strings, blue F '
              'strings, the rest cream) from the neck to the soundboard.',
  slots=['body','gold','maple','s_cream','s_red','s_blue','pin'], flash_slot='body', flash_slots=['body','gold'], flash_color=[1.0,0.85,0.45]),
'''"""harp (jewelbox 24): gilt neck striker + concert harp (column, soundboard, coloured strings, base)."""
'''+HDR+H+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.02)]                                    # gilt neck (contact)
    P.append(bar(C, (0.30,0.0), (0.46,-0.05), 0.08, 0.10, 1, 0.21, bevel=0.02))                    # neck sweeps down to the soundboard top
    P.append(bar(C, (-0.30,0.0), (-0.44,0.05), 0.08, 0.10, 1, 0.21, bevel=0.02))                   # and up into the crown
    P.append(C.prim('cyl', 1, loc=(-0.44,0.21,-0.27), scale=(0.035,0.035,0.62), verts=24))         # column
    for z in (-0.02, -0.52): P.append(C.prim('torus', 1, loc=(-0.44,0.21,z), scale=(0.042,0.012), verts=24))
    P.append(C.prim('sphere', 1, loc=(-0.44,0.21,0.09), scale=(0.055,0.05,0.055), verts=24))       # crown
    P.append(C.prim('cyl', 1, loc=(-0.44,0.21,0.14), scale=(0.03,0.03,0.04), verts=16))
    sb0, sb1 = (0.46,-0.07), (-0.30,-0.58)                                                        # soundboard
    P.append(bar(C, sb0, sb1, 0.09, 0.08, 2, 0.235, bevel=0.012))
    P.append(C.prim('cube', 1, loc=(-0.30,0.22,-0.60), scale=(0.34,0.12,0.06), bevel=0.012))       # gilt base
    for x in (-0.40,-0.33,-0.26,-0.19): P.append(C.prim('cube', 1, loc=(x,0.17,-0.62), scale=(0.025,0.02,0.012)))
    def sbz(x): return sb0[1] + (sb1[1]-sb0[1])*(sb0[0]-x)/(sb0[0]-sb1[0])
    for i in range(17):
        x = -0.38 + 0.047*i; z1 = sbz(x) + 0.03
        c = 4 if i % 7 == 0 else (5 if i % 7 == 3 else 3)
        P.append(C.prim('cyl', c, loc=(x,0.19,(-0.045+z1)/2), scale=(0.004,0.004,-0.045-z1), verts=8))
    return P
''',
'''"""harp materials"""
def shared(C):
    return {'gold': C.mat('hp_gold',(0.95,0.72,0.35),rough=0.22,metal=1.0),
            'maple': C.add_wood(C.mat('hp_maple',(0.72,0.5,0.26),rough=0.35,coat=0.6),(0.64,0.42,0.2),(0.85,0.64,0.36),scale=6.0),
            's_cream': C.mat('hp_scream',(0.88,0.84,0.72),rough=0.35), 's_red': C.mat('hp_sred',(0.7,0.03,0.03),rough=0.35),
            's_blue': C.mat('hp_sblue',(0.04,0.08,0.45),rough=0.35)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.95,0.74,0.36),rough=0.2,metal=1.0)
''')
print('wrote jewelbox F2 assets')
