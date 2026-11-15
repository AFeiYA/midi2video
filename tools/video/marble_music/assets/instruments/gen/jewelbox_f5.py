"""Jewelbox Orchestra (珠匣乐团) - family 5 (42-52: reeds, flutes & pipes). Reuses flute (v5) and ocarina (v5) as is.
New folders are registry-only (tracks_regex NEVER). The body tube lies in the marble slab (= striker); joints, bells, reeds and
decorations continue in the backplate band. Phone-size separation:
  oboe = slim warm reddish-brown wood, dense silver keys, tan double reed with orange thread;
  english horn = lighter cocobolo wood, PEAR-shaped bulb bell + bent silver crook with reed;
  bassoon = big orange-red maple, folded double tube, ivory bell ring, S-shaped silver bocal;
  clarinet = jet-black grenadilla, silver rings & keys, barrel + black beak mouthpiece + flared black bell (soprano sax is straight SILVER metal);
  piccolo = slender complete silver piccolo + its open blue-velvet case (flute is thick and runs past the paddle);
  recorder = honey boxwood with chocolate turned rings and a beak, no keys;
  pan flute = row of graded bamboo pipes behind a red-corded crossbar; shakuhachi = thick green-gold bamboo with nodes, root bulb, purple tassel;
  tin whistle = thin nickel tube with a green fipple head and a shamrock."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER
from snippets import H, BRASS, WOOD

TUBEPINS = [{"x":-0.15,"z":0.0,"y_start":0.03,"radius":0.02},{"x":0.15,"z":0.0,"y_start":0.03,"radius":0.02}]
SRC = HDR + H + BRASS + WOOD
SILVER = (0.9,0.9,0.92)
def metal(name, rgb, rough=0.12):
    return f"C.mat('{name}',{rgb},rough={rough},metal=1.0)"
def wood(name, base, c1, c2, rough=0.25, coat=0.8, scale=6.0):
    return f"C.add_wood(C.mat('{name}',{base},rough={rough},coat={coat}),{c1},{c2},scale={scale})"
def wood_body(base, c1, c2, rough=0.25, coat=0.8, scale=6.0):
    return f"C.add_wood(C.mat(name,{base},rough={rough},coat={coat}),{c1},{c2},scale={scale})"

def asset(folder, sec, num, desc, slots, flash, build, shared, body, pins=TUBEPINS):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=pins, description=desc, slots=slots+['pin'],
                       flash_slot='body', flash_color=flash),
          f'"""{folder} (jewelbox {num})."""\n' + SRC + build,
          f'"""{folder} materials"""\ndef shared(C):\n    return {{{shared}}}\ndef body(C, name, j, note, variant):\n    return {body}\n')

# ------------------------------------------------------------------ 42 oboe
asset('oboe', 142, 42,
  'Jewelbox 42 Oboe: slim warm reddish-brown (violet-wood) oboe on its side - the body is the striker, crowded with silver key cups, rods and '
  'ferrules; a small flared bell at the right and the tan cane DOUBLE REED with orange thread wrap and cork at the left.',
  ['body','keys','dark','cork','thread','cane'], [1.0,0.85,0.7], '''
def build(C, variant=None):
    r = 0.032; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.30, -0.06, 0.30): P.append(ferrule(C, 1, x, r, zc))
    for x in (-0.24,-0.20,-0.15,-0.11,-0.02,0.03,0.08,0.13,0.18,0.23,0.27): P += keycup(C, 1, x, r, zc, rc=0.012)
    for x in (-0.175,0.105): P.append(hole(C, 2, x, r, zc, 0.007))
    P.append(keyrod(C, 1, r, zc, dz=-0.55)); P.append(keyrod(C, 1, r, zc, -0.26, 0.20, dz=0.35, rr=0.0028))
    for x in (-0.22,-0.13,0.0,0.10,0.20): P.append(C.prim('cube', 1, loc=(x,-r*0.85,zc-0.012), scale=(0.004,0.006,0.02)))   # posts
    o, (bx, by) = chain(C, 0, 1, zc, r, 0.195); P.append(o)                                                # body folds back into the bell
    P += bell(C, 0, 2, (bx,zc), (1,0), 0.09, r, 0.05, y=by, ymax=0.036, power=2.5)
    P.append(sweep(C, 1, [(bx+0.085,zc),(bx+0.093,zc)], 0.052, y=by, ymax=0.037, smooth=1))
    o, (mx, my) = chain(C, 0, -1, zc, r, 0.195); P.append(o)
    P.append(collar(C, 1, mx-0.003, zc, my, 0.035, w=0.012, ymax=0.036))
    P.append(sweep(C, 1, [(mx,zc),(mx-0.03,zc)], [0.018,0.012], y=my))                                     # reed well
    P += double_reed(C, 3, 4, 5, mx-0.03, zc, y=my, scale=1.15)
    return P
''',
  f"'keys': {metal('ob_keys', SILVER)}, 'dark': C.mat('ob_dark',(0.01,0.008,0.006),rough=0.6), "
  f"'cork': C.mat('ob_cork',(0.55,0.38,0.22),rough=0.8), 'thread': C.mat('ob_thread',(0.95,0.35,0.05),rough=0.6), "
  f"'cane': C.mat('ob_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)",
  wood_body((0.03,0.009,0.005),(0.018,0.005,0.003),(0.05,0.016,0.008)))

# ------------------------------------------------------------------ 43 english horn
asset('english_horn', 143, 43,
  'Jewelbox 43 English Horn (cor anglais): a longer, thicker oboe in lighter orange-brown cocobolo with silver keys - unmistakable PEAR-shaped '
  'bulb bell at the right, and a BENT silver crook (bocal) rising from the left end into the double reed.',
  ['body','keys','dark','cork','thread','cane'], [1.0,0.8,0.6], '''
def build(C, variant=None):
    r = 0.037; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.30, -0.02, 0.30): P.append(ferrule(C, 1, x, r, zc))
    for x in (-0.24,-0.19,-0.13,-0.08,0.04,0.09,0.15,0.21,0.26): P += keycup(C, 1, x, r, zc, rc=0.014)
    P.append(keyrod(C, 1, r, zc, dz=-0.55))
    prof = [(0.30,0.037),(0.33,0.042),(0.36,0.056),(0.40,0.066),(0.44,0.064),(0.475,0.05),(0.49,0.034),(0.497,0.026)]
    o, (bx, by) = chain(C, 0, 1, zc, r, 0.215, cont=[(x,zc) for x,_ in prof], radii=[rr for _,rr in prof], n=32); P.append(o)   # body -> pear bulb bell, one piece
    P.append(sweep(C, 2, [(0.497,zc),(0.499,zc)], 0.02, y=by, ymax=0.02, smooth=1))
    P.append(collar(C, 1, 0.318, zc, by, 0.042, w=0.014))
    o, (mx, my) = chain(C, 0, -1, zc, r, 0.2); P.append(o)
    P.append(collar(C, 1, mx-0.004, zc, my, 0.02, w=0.018))                                                 # crook receiver
    crook = [(mx,zc),(-0.35,zc+0.004),(-0.39,zc+0.02),(-0.42,zc+0.05),(-0.44,zc+0.09),(-0.45,zc+0.13)]
    P.append(sweep(C, 1, crook, [0.009,0.0075,0.007,0.0065,0.006,0.006], y=my, n=12))
    P += double_reed(C, 3, 4, 5, -0.45, zc+0.13, y=my, dirx=-0.15, dirz=1.0, scale=1.15)                    # reed on top of the crook
    return P
''',
  f"'keys': {metal('eh_keys', SILVER)}, 'dark': C.mat('eh_dark',(0.01,0.008,0.006),rough=0.6), "
  f"'cork': C.mat('eh_cork',(0.55,0.38,0.22),rough=0.8), 'thread': C.mat('eh_thread',(0.1,0.25,0.75),rough=0.6), "
  f"'cane': C.mat('eh_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)",
  wood_body((0.1,0.035,0.012),(0.06,0.02,0.007),(0.15,0.055,0.02)))

# ------------------------------------------------------------------ 44 bassoon
asset('bassoon', 144, 44,
  'Jewelbox 44 Bassoon: big orange-red flamed-maple bassoon on its side - the wing joint is the striker; behind it the parallel bass joint runs '
  'further left to the bell with an IVORY ring, joined at the right by the black-capped boot (U-bend); silver keys and an S-curved silver bocal with reed.',
  ['body','keys','dark','ivory','cork','thread','cane'], [1.0,0.75,0.5], '''
def build(C, variant=None):
    r = 0.04; zc = 0.045 - r; zb = -0.12; rb = 0.052
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.30, 0.30): P.append(ferrule(C, 1, x, r, zc))
    for x in (-0.20,-0.12,0.05,0.13): P.append(hole(C, 2, x, r, zc, 0.01))
    for x in (-0.24,-0.16,0.0,0.09,0.20,0.26): P += keycup(C, 1, x, r, zc, rc=0.015)
    P.append(keyrod(C, 1, r, zc, dz=-0.6))
    o, _ = chain(C, 0, 1, zc, r, 0.215, cont=arc_pts(0.31,(zc+zb)/2,(zc-zb)/2,math.pi/2,-math.pi/2,14) + [(0.25,zb),(-0.58,zb)],
                 radii=[r]*15 + [rb, rb], n=32); P.append(o)                                                  # wing joint -> boot U-bend -> bass joint: one tube
    P.append(sweep(C, 3, [(-0.58,zb),(-0.62,zb)], rb+0.008, y=0.215, ymax=0.06))                          # ivory bell ring
    P.append(sweep(C, 2, [(-0.618,zb),(-0.621,zb)], rb*0.8, y=0.215, ymax=0.045))
    for x in (-0.15, 0.10): P.append(sweep(C, 1, [(x-0.007,zb),(x+0.007,zb)], rb+0.004, y=0.215, ymax=0.06))
    P.append(C.prim('cube', 0, loc=(0.40,0.215,(zc+zb)/2), scale=(0.11,0.09,0.20), bevel=0.03))            # boot joint
    P.append(C.prim('cube', 2, loc=(0.46,0.215,(zc+zb)/2), scale=(0.012,0.095,0.205), bevel=0.004))         # black boot cap
    for z in (zc-0.02, zb+0.03): P.append(C.prim('cyl', 1, loc=(0.36,0.163,z), rot=(math.pi/2,0,0), scale=(0.016,0.016,0.006), verts=20))
    o, (mx, my) = chain(C, 0, -1, zc, r, 0.2); P.append(o)
    P.append(collar(C, 1, mx-0.004, zc, my, 0.024, w=0.018))                                                 # bocal receiver
    boc = [(mx,zc),(-0.34,zc),(-0.37,zc+0.02),(-0.38,zc+0.06),(-0.40,zc+0.09),(-0.44,zc+0.10),(-0.48,zc+0.11)]
    P.append(sweep(C, 1, boc, [0.01,0.0085,0.008,0.0075,0.007,0.0065,0.006], y=my, n=12))
    P += double_reed(C, 4, 5, 6, -0.48, zc+0.11, y=my, scale=1.3)
    return P
''',
  f"'keys': {metal('bn_keys', SILVER)}, 'dark': C.mat('bn_dark',(0.012,0.01,0.01),rough=0.4,coat=0.5), "
  f"'ivory': C.mat('bn_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.6), 'cork': C.mat('bn_cork',(0.55,0.38,0.22),rough=0.8), "
  f"'thread': C.mat('bn_thread',(0.75,0.08,0.06),rough=0.6), 'cane': C.mat('bn_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)",
  wood_body((0.17,0.045,0.012),(0.11,0.028,0.007),(0.26,0.075,0.02),scale=4.0))

# ------------------------------------------------------------------ 45 clarinet
asset('clarinet', 145, 45,
  'Jewelbox 45 Clarinet: jet-black grenadilla wood with bright silver rings, key cups and rods - the body is the striker; at the left the '
  'barrel and black beak mouthpiece with a silver ligature, at the right the flared black bell with a silver rim. Clearly not the straight SILVER soprano sax.',
  ['body','keys','dark','pad','mouth','reed'], [0.85,0.9,1.0], '''
def build(C, variant=None):
    r = 0.038; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.30, -0.05, 0.30): P.append(ferrule(C, 1, x, r, zc, w=0.016, extra=0.005))
    for x in (-0.22,-0.16,-0.10, 0.05,0.11,0.17): P.append(hole(C, 2, x, r, zc, 0.011))
    for x in (-0.22,-0.16,-0.10, 0.05,0.11,0.17): P.append(C.prim('torus', 1, loc=(x,-(r-0.002),zc), rot=(math.pi/2,0,0), scale=(0.015,0.0025), verts=24))  # ring keys
    for x in (-0.27, 0.23, 0.27): P += keycup(C, 1, x, r, zc, rc=0.016, pad=3)
    P.append(keyrod(C, 1, r, zc, dz=-0.6)); P.append(keyrod(C, 1, r, zc, -0.25, 0.25, dz=0.4, rr=0.003))
    o, (bx, by) = chain(C, 0, 1, zc, r, 0.215, cont=[(0.35,zc)]); P.append(o)                              # lower joint folds back to the bell
    P += bell(C, 0, 2, (0.35,zc), (1,0), 0.17, r, 0.085, y=by, ymax=0.058, power=2.2)
    P.append(collar(C, 1, 0.35, zc, by, r+0.005, w=0.014))
    P.append(sweep(C, 1, [(0.508,zc),(0.522,zc)], 0.089, y=by, ymax=0.058, smooth=1))                        # silver bell rim
    o, (mx, my) = chain(C, 0, -1, zc, r, 0.205, cont=[(-0.33,zc),(-0.40,zc),(-0.42,zc)], radii=[0.042,0.042,0.036]); P.append(o)   # upper joint -> barrel
    for x in (-0.332,-0.398): P.append(collar(C, 1, x, zc, my, 0.046, w=0.012, ymax=0.048))
    P.append(sweep(C, 4, [(-0.415,zc),(-0.47,zc),(-0.51,zc+0.006),(-0.54,zc+0.012)], [0.03,0.026,0.02,0.01], y=my))  # beak mouthpiece
    P.append(collar(C, 1, -0.4675, zc, my, 0.031, w=0.025, ymax=0.036))                                    # ligature
    P.append(sweep(C, 5, [(-0.43,zc-0.027),(-0.53,zc-0.016)], 0.004, y=my, ymax=0.018))                    # reed
    return P
''',
  f"'keys': {metal('cl_keys', (0.95,0.95,0.97), 0.08)}, 'dark': C.mat('cl_dark',(0.004,0.004,0.004),rough=0.6), "
  f"'pad': C.mat('cl_pad',(0.85,0.75,0.55),rough=0.6), 'mouth': C.mat('cl_mouth',(0.012,0.012,0.014),rough=0.15,coat=1.0), "
  f"'reed': C.mat('cl_reed',(0.82,0.66,0.35),rough=0.45)",
  wood_body((0.022,0.016,0.014),(0.012,0.009,0.008),(0.045,0.03,0.025),rough=0.2,coat=1.0,scale=5.0))

# ------------------------------------------------------------------ 46 piccolo (adapted from flute: slender, complete, in its case)
asset('piccolo', 146, 46,
  'Jewelbox 46 Piccolo: the flute\'s little sibling - a slender, COMPLETE silver piccolo (crown, lip plate, head joint, keyed body) fits within '
  'the paddle; behind it lies its small open black case with royal-blue velvet lining and the empty piccolo-shaped recess.',
  ['body','pad','rod','dark','case','velvet'], [0.85,0.9,1.0], '''
def build(C, variant=None):
    r = 0.024; zc = 0.045 - r
    P = [tube_x(C, 0, r, x0=-0.285, x1=0.30, zc=zc)]
    P.append(C.prim('cyl', 2, loc=(-0.295,0,zc), rot=(0,math.pi/2,0), scale=(r,r,0.02), bevel=0.004, verts=32))   # crown
    P.append(C.prim('sphere', 2, loc=(-0.302,0,zc), scale=(0.007,r*0.9,r*0.9), verts=20))
    P.append(ferrule(C, 2, -0.08, r, zc, w=0.02, extra=0.004)); P.append(ferrule(C, 2, 0.29, r, zc, w=0.02, extra=0.004))
    P.append(C.prim('sphere', 0, loc=(-0.19,-(r+0.002),zc), scale=(0.04,0.008,0.018), verts=32))           # lip plate
    P.append(C.prim('sphere', 3, loc=(-0.19,-(r+0.009),zc), scale=(0.014,0.003,0.007), verts=16))         # embouchure hole
    for x in (-0.03,0.03,0.09,0.15,0.21,0.26):
        P += keycup(C, 2, x, r, zc, rc=0.015, pad=1)
    P.append(keyrod(C, 2, r, zc, -0.04, 0.27, dz=-0.7, rr=0.003))
    # open case behind (backplate band)
    P.append(C.prim('cube', 4, loc=(0.0,0.265,-0.16), scale=(0.66,0.035,0.17), bevel=0.02))
    P.append(C.prim('cube', 5, loc=(0.0,0.245,-0.16), scale=(0.62,0.012,0.13), bevel=0.01))
    P.append(C.prim('cube', 3, loc=(0.0,0.238,-0.16), scale=(0.56,0.004,0.035), bevel=0.012))           # recess
    P.append(C.prim('cube', 3, loc=(0.18,0.238,-0.205), scale=(0.12,0.004,0.025), bevel=0.01))
    for x in (-0.25, 0.25): P.append(C.prim('cube', 2, loc=(x,0.245,-0.243), scale=(0.04,0.012,0.008)))  # latches
    return P
''',
  f"'pad': C.mat('pc_pad',(0.85,0.75,0.55),rough=0.6), 'rod': {metal('pc_rod', (0.95,0.94,0.92), 0.08)}, "
  f"'dark': C.mat('pc_dark',(0.01,0.01,0.02),rough=0.6), 'case': C.mat('pc_case',(0.02,0.02,0.022),rough=0.35,coat=0.6), "
  f"'velvet': C.mat('pc_velvet',(0.015,0.03,0.2),rough=0.95)",
  "C.mat(name,(0.97,0.96,0.94),rough=0.07,metal=1.0)")

# ------------------------------------------------------------------ 48 recorder
asset('recorder', 148, 48,
  'Jewelbox 48 Recorder: honey-coloured boxwood baroque recorder with chocolate-brown turned rings - the body is the striker; open finger holes '
  '(double holes at the bottom), no keys; the head with its square window and the curved beak mouthpiece at the left, the flared foot at the right.',
  ['body','ring','dark','edge'], [1.0,0.9,0.6], '''
def build(C, variant=None):
    r = 0.036; zc = 0.045 - r
    P = [tube_x(C, 0, r, x0=-0.24, x1=0.25, zc=zc)]
    P.append(tube_x(C, 0, r+0.006, x0=-0.31, x1=-0.24, zc=zc-0.006))                       # head (wider, top flush)
    P.append(tube_x(C, 0, r+0.004, x0=0.25, x1=0.31, zc=zc-0.004))                          # foot socket
    for x, w in ((-0.245,0.012),(-0.23,0.006),(0.0,0.012),(0.245,0.012),(0.296,0.01)): P.append(ferrule(C, 1, x, r+0.004, zc-0.004, w=w, extra=0.002))
    P.append(C.prim('cube', 2, loc=(-0.275,-(r+0.002),zc+0.004), scale=(0.022,0.01,0.018)))               # window
    P.append(C.prim('cube', 3, loc=(-0.262,-(r+0.004),zc+0.004), rot=(0,0,0), scale=(0.004,0.008,0.018)))  # labium edge
    for x in (-0.17,-0.12,-0.07,0.05,0.10,0.15): P.append(hole(C, 2, x, r, zc, 0.0085))
    for x in (0.20,): P += [hole(C, 2, x-0.008, r, zc, 0.006), hole(C, 2, x+0.008, r, zc, 0.006)]
    o, _ = chain(C, 0, -1, zc-0.006, r+0.006, 0.215, cont=[(-0.36,zc-0.002),(-0.40,zc+0.008),(-0.43,zc+0.016)], radii=[0.036,0.026,0.014], ymax=0.045); P.append(o)   # head -> beak
    o, (bx, by) = chain(C, 0, 1, zc-0.004, r+0.004, 0.215); P.append(o)
    P += bell(C, 0, 2, (bx,zc-0.004), (1,0), 0.07, r+0.004, 0.055, y=by, ymax=0.045, power=1.8)
    P.append(collar(C, 1, bx+0.066, zc-0.004, by, 0.058, w=0.01, ymax=0.047))
    return P
''',
  f"'ring': C.mat('rc_ring',(0.025,0.011,0.005),rough=0.25,coat=0.8), 'dark': C.mat('rc_dark',(0.01,0.006,0.003),rough=0.7), "
  f"'edge': C.mat('rc_edge',(0.9,0.85,0.7),rough=0.3)",
  wood_body((0.3,0.15,0.045),(0.22,0.1,0.028),(0.4,0.21,0.07),rough=0.3,coat=0.6,scale=7.0))

# ------------------------------------------------------------------ 49 pan flute
asset('pan_flute', 149, 49,
  'Jewelbox 49 Pan Flute: the bamboo crossbar wrapped in red cord is the striker; behind it a row of twelve bamboo pipes of graded length '
  '(long at the left, short at the right) with aligned open tops and a second corded binding band.',
  ['body','cord','pipe','dark','node'], [1.0,0.9,0.55], '''
def build(C, variant=None):
    r = 0.028; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.29,-0.27,0.27,0.29) + tuple(-0.25+0.0455*k for k in range(12)): P.append(ferrule(C, 1, x, r, zc, w=0.006, extra=0.002))
    top = 0.12
    for k in range(12):
        x = -0.25 + 0.0455*k; L = 0.50 - 0.03*k; rp = 0.021 - 0.0006*k
        P.append(C.prim('cyl', 2, loc=(x,0.215,top-L/2), scale=(rp,rp,L), verts=24))
        P.append(C.prim('cyl', 3, loc=(x,0.215,top-0.002), scale=(rp*0.7,rp*0.7,0.006), verts=20))       # open top
        P.append(C.prim('cyl', 4, loc=(x,0.215,top-L+0.01), scale=(rp*1.06,rp*1.06,0.012), verts=24))   # closed node end
    for k in range(12): P.append(yport(C, 1, -0.25+0.0455*k, zc, 0.005, 0.0, 0.215, verts=8))           # cord lashings: crossbar -> every pipe
    P.append(C.prim('cube', 1, loc=(0.0,0.19,-0.15), scale=(0.56,0.008,0.012)))                            # lower cord band
    P.append(C.prim('cube', 1, loc=(0.0,0.19,0.09), scale=(0.56,0.008,0.012)))
    for x in (-0.30, 0.30):                                                                                  # tassels
        P.append(sweep(C, 1, [(x,zc-0.02),(x+0.01,-0.10),(x+0.005,-0.16)], 0.004, y=0.19, n=8))
        P.append(sweep(C, 1, [(x+0.005,-0.16),(x+0.005,-0.235)], [0.005,0.018], y=0.19, ymax=0.018, n=16))
    return P
''',
  "'cord': C.mat('pf_cord',(0.75,0.06,0.04),rough=0.7), "
  "'pipe': C.add_wood(C.mat('pf_pipe',(0.72,0.55,0.26),rough=0.35,coat=0.5),(0.6,0.42,0.17),(0.82,0.66,0.34),scale=2.0), "
  "'dark': C.mat('pf_dark',(0.02,0.012,0.005),rough=0.7), 'node': C.mat('pf_node',(0.45,0.3,0.12),rough=0.4,coat=0.4)",
  wood_body((0.62,0.45,0.2),(0.5,0.34,0.13),(0.75,0.58,0.3),rough=0.35,coat=0.5,scale=2.0))

# ------------------------------------------------------------------ 50 shakuhachi
asset('shakuhachi', 150, 50,
  'Jewelbox 50 Shakuhachi: thick green-gold bamboo with raised nodes is the striker; the angled blowing edge with white horn inlay at the left, '
  'four big finger holes, the flared root end with root nubs at the right, and a purple silk cord with tassel.',
  ['body','node','dark','inlay','cord'], [0.9,1.0,0.6], '''
def build(C, variant=None):
    r = 0.042; zc = 0.045 - r
    P = [tube_x(C, 0, r, zc=zc)]
    for x in (-0.20,-0.04,0.12,0.27): P.append(ferrule(C, 1, x, r, zc, w=0.012, extra=0.0015))
    for x in (-0.12,-0.06,0.04,0.10): P.append(hole(C, 2, x, r, zc, 0.012))
    P.append(C.prim('cube', 3, loc=(-0.302,-0.02,zc+0.03), rot=(0,0,0), scale=(0.012,0.03,0.016), bevel=0.003))   # horn inlay
    P.append(C.prim('cyl', 2, loc=(-0.307,0,zc), rot=(0,math.pi/2,0), scale=(r*0.65,r*0.65,0.004), verts=24))
    o, (bx, by) = chain(C, 0, 1, zc, r, 0.215, cont=[(0.35,zc-0.004),(0.39,zc-0.012),(0.42,zc-0.02),(0.435,zc-0.024)], radii=[0.05,0.056,0.054,0.04]); P.append(o)   # root end, same culm
    for dx, dz in ((0.37,-0.05),(0.40,-0.055),(0.42,-0.045),(0.40,0.04),(0.37,0.045)):
        P.append(C.prim('sphere', 1, loc=(dx,0.168,zc-0.01+dz), scale=(0.008,0.008,0.008), verts=12))
    P.append(sweep(C, 4, [(-0.25,zc-0.04),(-0.26,-0.10),(-0.24,-0.16),(-0.26,-0.20)], 0.004, y=0.19, n=8))
    P.append(sweep(C, 4, [(-0.26,-0.20),(-0.26,-0.28)], [0.006,0.02], y=0.19, ymax=0.02, n=16))
    P.append(C.prim('sphere', 4, loc=(-0.26,0.19,-0.197), scale=(0.012,0.012,0.012), verts=16))
    return P
''',
  "'node': C.mat('sk_node',(0.08,0.055,0.015),rough=0.35,coat=0.6), 'dark': C.mat('sk_dark',(0.015,0.01,0.004),rough=0.7), "
  "'inlay': C.mat('sk_inlay',(0.93,0.9,0.82),rough=0.2,coat=0.8), 'cord': C.mat('sk_cord',(0.35,0.06,0.45),rough=0.6)",
  wood_body((0.17,0.15,0.035),(0.12,0.1,0.02),(0.24,0.21,0.06),rough=0.3,coat=0.7,scale=1.5))

# ------------------------------------------------------------------ 51 tin whistle
asset('tin_whistle', 151, 51,
  'Jewelbox 51 Tin Whistle: a thin bright nickel tube is the striker with six open finger holes; at the left the emerald-green plastic fipple head '
  'with its white window edge and mouthpiece, and a green shamrock lying behind it.',
  ['body','head','dark','edge','leaf'], [0.85,1.0,0.85], '''
def build(C, variant=None):
    r = 0.022; zc = 0.045 - r; rh = 0.028; zh = 0.045 - rh
    P = [tube_x(C, 0, r, x0=-0.17, x1=0.31, zc=zc)]
    P.append(tube_x(C, 1, rh, x0=-0.31, x1=-0.16, zc=zh))
    P.append(C.prim('cube', 2, loc=(-0.215,-(rh-0.001),zh+0.004), scale=(0.024,0.008,0.016)))
    P.append(C.prim('cube', 3, loc=(-0.2,-(rh+0.001),zh+0.004), scale=(0.004,0.006,0.016)))
    for x in (-0.07,-0.02,0.03,0.10,0.15,0.20): P.append(hole(C, 2, x, r, zc, 0.0075))
    o, _ = chain(C, 1, -1, zh, rh, 0.2, cont=[(-0.35,zh+0.004),(-0.38,zh+0.01)], radii=[0.02,0.012]); P.append(o)   # fipple head -> mouthpiece, one piece
    def leaf(cx, cz, a):
        o = []
        for s in (-0.45, 0.45):
            o.append(C.prim('sphere', 4, loc=(cx+0.045*math.cos(a+s), 0.24, cz+0.045*math.sin(a+s)), rot=(0,-(a+s),0), scale=(0.045,0.008,0.032), verts=24))
        return o
    cx, cz = 0.20, -0.17
    for a in (math.pi/2, math.pi/2+2.1, math.pi/2-2.1): P += leaf(cx, cz, a)
    P.append(sweep(C, 4, [(cx,cz),(cx+0.02,cz-0.06),(cx+0.05,cz-0.11)], 0.008, y=0.24, n=10))
    return P
''',
  "'head': C.mat('tw_head',(0.0,0.35,0.1),rough=0.25,coat=0.8), 'dark': C.mat('tw_dark',(0.01,0.01,0.01),rough=0.7), "
  "'edge': C.mat('tw_edge',(0.92,0.92,0.9),rough=0.3), 'leaf': C.mat('tw_leaf',(0.03,0.42,0.08),rough=0.45,coat=0.3)",
  "C.mat(name,(0.88,0.88,0.86),rough=0.1,metal=1.0)")
print('wrote jewelbox F5 assets')
