"""Jewelbox Orchestra (珠匣乐团) - family 6 (53-64: world strings & winds, percussion, synths). Reuses koto, kalimba (v5), bagpipe,
steel_drums (v5), pixel8bit; 65 Finale reuses finale. New folders are registry-only (tracks_regex NEVER).
F6 rule (after the F4/F5 tube feedback): every instrument is ONE rigid object on ONE depth plane - the whole instrument sits in the
marble slab, pushed forward so its struck part is the striker (top face z=0.045 over x in [-0.31,0.31]); the rest of its real shape hangs
below the striker or continues past its ends low down. No parts in the backplate band, no elbows, nothing floating: every piece touches
the piece it belongs to (strings end on bridges, castanets hang on cords, the crystal ball hangs in its cradle from the bar).
Keep-out is checked against the real marble paths (check_keepout), as for the approved finale / koto / kalimba."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER
from snippets import H, BRASS, WOOD

PINS = [{"x":-0.15,"z":0.0,"y_start":0.05,"radius":0.02},{"x":0.15,"z":0.0,"y_start":0.05,"radius":0.02}]
SRC = HDR + H + BRASS + WOOD
def metal(name, rgb, rough=0.12): return f"C.mat('{name}',{rgb},rough={rough},metal=1.0)"
def wood(name, base, c1, c2, rough=0.3, coat=0.7, scale=6.0): return f"C.add_wood(C.mat('{name}',{base},rough={rough},coat={coat}),{c1},{c2},scale={scale})"
def glow(name, rgb, strength=4.0, base=None):
    b = base or rgb
    return (f"(lambda m: (m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].__setattr__('default_value', ({rgb[0]},{rgb[1]},{rgb[2]},1)), "
            f"m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].__setattr__('default_value', {strength}), m)[-1])(C.mat('{name}',{b},rough=0.3))")

def asset(folder, sec, num, desc, slots, flash, build, shared, body, pins=PINS):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=pins, description=desc, slots=slots+['pin'],
                       flash_slot='body', flash_color=flash),
          f'"""{folder} (jewelbox {num})."""\n' + SRC + build,
          f'"""{folder} materials"""\ndef shared(C):\n    return {{{shared}}}\ndef body(C, name, j, note, variant):\n    return {body}\n')

# ------------------------------------------------------------------ 53 sitar
asset('sitar', 153, 53,
  'Jewelbox 53 Sitar: a compact whole sitar lying along the paddle - the dark teak neck with ivory edge inlay, arched brass frets and steel '
  'strings is the striker and runs straight into the lacquered pumpkin gourd (tumba) with ivory rosette and bridge at the right; the small upper gourd hangs under the neck, tuning pegs below the left end.',
  ['body','gourd','ivory','brass','steel'], [1.0,0.8,0.5], """
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(-0.10,0,0.005), scale=(0.42,0.11,0.08), bevel=0.008)]                  # teak neck (struck)
    for z in (0.037,-0.027): P.append(C.prim('cube', 2, loc=(-0.10,-0.0555,z), scale=(0.40,0.002,0.006)))
    for k in range(13):
        x = -0.27 + 0.33*(1-(1-k/12)**1.5)
        P.append(C.prim('cyl', 3, loc=(x,-0.06,0.005), scale=(0.004,0.004,0.074), verts=8))              # brass frets
    gx, gz, ax, ay, az = 0.19, -0.115, 0.13, 0.09, 0.155
    P.append(C.prim('sphere', 1, loc=(gx,0.0,gz), scale=(ax,ay,az), verts=48))                         # tumba gourd
    P.append(C.prim('cyl', 2, loc=(gx,-ay+0.002,gz-0.02), rot=(math.pi/2,0,0), scale=(0.035,0.035,0.006), verts=40))   # ivory rosette
    for k in range(12):
        a = 2*math.pi*k/12; dx, dz = 0.065*math.cos(a), 0.065*math.sin(a) - 0.02
        sq = 1 - (dx/ax)**2 - (dz/az)**2
        P.append(C.prim('sphere', 2, loc=(gx+dx,-ay*math.sqrt(max(sq,0.0))-0.002,gz+dz), scale=(0.007,0.004,0.007), verts=12))
    P.append(C.prim('cube', 3, loc=(0.10,0.0,-0.005), scale=(0.014,0.112,0.074), bevel=0.003))        # brass collar neck/gourd
    P.append(C.prim('sphere', 1, loc=(-0.20,0.0,-0.10), scale=(0.07,0.065,0.07), verts=32))            # upper gourd
    P.append(C.prim('cube', 2, loc=(0.21,-0.06,0.007), scale=(0.012,0.022,0.055)))                     # bridge on the gourd
    for z in (0.028,0.014,0.0,-0.014):
        P.append(C.prim('cyl', 4, loc=((-0.30+0.21)/2,-0.071,z), rot=(0,math.pi/2,0), scale=(0.0016,0.0016,0.51), verts=6))
    for x in (-0.29,-0.25):                                                                                # main pegs
        P.append(C.prim('cyl', 0, loc=(x,0.0,-0.07), scale=(0.008,0.008,0.075), verts=12))
        P.append(C.prim('sphere', 2, loc=(x,0.0,-0.11), scale=(0.016,0.016,0.024), verts=16))
    for x in (-0.10,-0.05,0.0,0.05):                                                                       # sympathetic-string side pegs
        P.append(C.prim('cyl', 0, loc=(x,-0.035,-0.05), scale=(0.004,0.004,0.035), verts=8))
        P.append(C.prim('sphere', 2, loc=(x,-0.035,-0.07), scale=(0.008,0.008,0.01), verts=12))
    P.append(C.prim('sphere', 0, loc=(-0.303,0.0,0.0), scale=(0.007,0.05,0.04), verts=20))             # carved finial
    P.append(C.prim('sphere', 2, loc=(0.302,0.0,gz), scale=(0.006,0.018,0.018), verts=12))             # tail knob
    return P
""",
  f"'gourd': C.mat('si_gourd',(0.28,0.09,0.02),rough=0.2,coat=1.0), 'ivory': C.mat('si_ivory',(0.9,0.86,0.75),rough=0.3,coat=0.5), "
  f"'brass': {metal('si_brass',(0.92,0.66,0.3))}, 'steel': {metal('si_steel',(0.9,0.9,0.9),0.2)}",
  "C.add_wood(C.mat(name,(0.06,0.028,0.012),rough=0.3,coat=0.8),(0.035,0.016,0.007),(0.09,0.045,0.02),scale=6.0)")

# ------------------------------------------------------------------ 54 banjo (hangs upright from a wall-hanger rail)
asset('banjo', 154, 54,
  'Jewelbox 54 Banjo: a walnut wall-hanger rail with a brass yoke is the striker; the whole banjo hangs upright from it by the headstock - '
  'pearl-button tuners, maple neck with ebony fingerboard, chrome frets and pearl dots, 5th-string peg, and the round pot at the bottom with white head, chrome hoop and brackets, bridge, tailpiece and five strings.',
  ['body','maple','board','head','chrome','rim','pearl','steel','bridge','brass'], [1.0,0.85,0.6], """
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.005), scale=(0.62,0.1,0.08), bevel=0.012)]                       # walnut hanger rail (struck)
    for x in (-0.06, 0.06): P.append(C.prim('cyl', 9, loc=(x,0.03,-0.1), scale=(0.007,0.007,0.13), verts=12))   # brass yoke arms
    P.append(tube3(C, 9, [(-0.06,0.03,-0.165)] + [(0.06*math.cos(math.pi+math.pi*k/12),0.03,-0.165+0.035*math.sin(math.pi+math.pi*k/12)) for k in range(13)] + [(0.06,0.03,-0.165)], 0.007, n=12, smooth=1))
    hs = [(-0.042,-0.045),(0.042,-0.045),(0.05,-0.085),(0.032,-0.165),(-0.032,-0.165),(-0.05,-0.085)]
    P.append(C.shape_profile('bj_head', hs, 0.03, -0.015, 1, bevel=0.006))                            # headstock (sits in the yoke)
    P.append(C.shape_profile('bj_veneer', [(x*0.88,z) for x,z in hs], 0.006, -0.019, 2, bevel=0.002))
    P.append(C.prim('sphere', 6, loc=(0,-0.02,-0.09), scale=(0.016,0.003,0.022), verts=16))            # pearl inlay
    for z in (-0.07, -0.125):
        for sx in (-1, 1):
            P.append(C.prim('cyl', 4, loc=(sx*0.058,0.0,z), rot=(0,math.pi/2,0), scale=(0.004,0.004,0.025), verts=8))
            P.append(C.prim('sphere', 6, loc=(sx*0.074,0.0,z), scale=(0.008,0.007,0.011), verts=12))
    P.append(C.prim('cube', 1, loc=(0,0,-0.335), scale=(0.055,0.04,0.34), bevel=0.006))               # maple neck
    P.append(C.prim('cube', 2, loc=(0,-0.022,-0.335), scale=(0.05,0.006,0.33)))                        # ebony fingerboard
    for k in range(16):
        z = -0.175 - 0.31*(1-(1-k/15)**1.5)
        P.append(C.prim('cube', 4, loc=(0,-0.0255,z), scale=(0.05,0.004,0.003)))
    for z in (-0.27,-0.31,-0.37,-0.41): P.append(C.prim('sphere', 6, loc=(0,-0.0255,z), scale=(0.006,0.002,0.006), verts=12))
    P.append(C.prim('cyl', 4, loc=(0.036,0.0,-0.30), rot=(0,math.pi/2,0), scale=(0.004,0.004,0.02), verts=8))   # 5th-string peg
    P.append(C.prim('sphere', 6, loc=(0.05,0.0,-0.30), scale=(0.008,0.007,0.011), verts=12))
    cz, R = -0.615, 0.13
    P.append(C.prim('cyl', 5, loc=(0,0.02,cz), rot=(math.pi/2,0,0), scale=(R+0.012,R+0.012,0.07), verts=64))   # resonator
    P.append(C.prim('cyl', 3, loc=(0,-0.022,cz), rot=(math.pi/2,0,0), scale=(R-0.004,R-0.004,0.012), verts=64)) # drum head
    P.append(C.prim('torus', 4, loc=(0,-0.028,cz), rot=(math.pi/2,0,0), scale=(R,0.009), verts=64))           # tension hoop
    for k in range(16):
        a = 2*math.pi*k/16 + 0.2
        P.append(C.prim('cube', 4, loc=((R+0.014)*math.cos(a),-0.01,cz+(R+0.014)*math.sin(a)), rot=(0,-a,0), scale=(0.015,0.028,0.009), bevel=0.002))
    P.append(C.prim('cube', 8, loc=(0,-0.04,cz-0.05), scale=(0.05,0.01,0.009)))                         # bridge
    P.append(C.prim('cube', 4, loc=(0,-0.035,cz-0.10), scale=(0.032,0.008,0.06), bevel=0.003))         # tailpiece
    for x in (-0.012,-0.004,0.004,0.012):
        P.append(C.prim('cyl', 7, loc=(x,-0.046,(-0.165+cz-0.075)/2), scale=(0.0013,0.0013,cz-0.075+0.165), verts=6))
    P.append(C.prim('cyl', 7, loc=(0.02,-0.046,(-0.30+cz-0.075)/2), scale=(0.0013,0.0013,cz-0.075+0.30), verts=6))
    return P
""",
  f"'maple': {wood('bj_maple',(0.5,0.3,0.12),(0.38,0.21,0.08),(0.62,0.4,0.18),scale=8.0)}, 'board': C.mat('bj_board',(0.015,0.01,0.008),rough=0.35,coat=0.5), "
  f"'head': C.mat('bj_head',(0.92,0.9,0.85),rough=0.65), 'chrome': {metal('bj_chrome',(0.92,0.92,0.94),0.08)}, "
  f"'rim': {wood('bj_rim',(0.14,0.05,0.015),(0.09,0.03,0.01),(0.2,0.08,0.03))}, 'pearl': C.mat('bj_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), "
  f"'steel': {metal('bj_steel',(0.9,0.9,0.9),0.2)}, 'bridge': C.mat('bj_bridge',(0.55,0.36,0.17),rough=0.4), 'brass': {metal('bj_brass',(0.92,0.66,0.3))}",
  "C.add_wood(C.mat(name,(0.07,0.035,0.015),rough=0.3,coat=0.8),(0.04,0.02,0.008),(0.11,0.055,0.025),scale=5.0)")

# ------------------------------------------------------------------ 55 shamisen (hangs from a lacquer rail on a red cord)
asset('shamisen', 155, 55,
  'Jewelbox 55 Shamisen: a black-lacquer rail with gold end caps is the striker; the whole shamisen hangs upright from it on a red silk cord '
  'tied round the head - three ivory itomaki pegs, the slim dark-red shitan neck, the square drum body with bulging sides, white skin, red cloth, ivory bridge, three silk strings and the big ivory bachi resting on the skin.',
  ['body','neck','frame','skin','ivory','silk','red','patch','gold'], [1.0,0.85,0.7], """
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.005), scale=(0.62,0.1,0.08), bevel=0.012)]                       # black lacquer rail (struck)
    for x in (-0.29, 0.29): P.append(C.prim('cube', 8, loc=(x,0,0.005), scale=(0.04,0.104,0.08), bevel=0.008))
    for sx in (-1, 1): P.append(rod(C, (sx*0.035,-0.035,0.0), (sx*0.01,-0.095), 0.004, 6, 8))          # red silk cord
    P.append(tube3(C, 6, [(0.0,0.0,-0.095),(0.025,-0.0,-0.13),(0.03,0.0,-0.17),(0.03,0.0,-0.2)], [0.004,0.004,0.012,0.016], n=16, smooth=2))   # tassel
    P.append(C.prim('cube', 1, loc=(0,0,-0.135), scale=(0.05,0.045,0.08), bevel=0.01))                # head (tenjin)
    for i, z in enumerate((-0.11,-0.135,-0.16)):                                                        # itomaki pegs through the head
        sx = -1 if i % 2 == 0 else 1
        P.append(C.prim('cyl', 3, loc=(sx*0.04,0.0,z), rot=(0,math.pi/2,0), scale=(0.0065,0.0065,0.07), verts=8))
        P.append(C.prim('cyl', 3, loc=(sx*0.082,0.0,z), rot=(0,math.pi/2,0), scale=(0.013,0.013,0.026), verts=8))
    P.append(C.prim('cube', 1, loc=(0,0,-0.39), scale=(0.03,0.03,0.45), bevel=0.005))                 # shitan neck
    cx, cz, hx, hz = 0.0, -0.71, 0.10, 0.11
    def sq(s=1.0, n=64):
        out = []
        for i in range(n):
            a = 2*math.pi*i/n; c, d = math.cos(a), math.sin(a)
            out.append((cx + s*hx*math.copysign(abs(c)**0.35, c), cz + s*hz*math.copysign(abs(d)**0.35, d)))
        return out
    P.append(C.shape_profile('sh_frame', sq(), 0.07, -0.035, 2, bevel=0.008))                          # drum body
    P.append(C.shape_profile('sh_skin', sq(0.93), 0.006, -0.041, 3, bevel=0.002))                      # skin
    P.append(C.prim('cube', 7, loc=(0.035,-0.0425,cz+0.02), scale=(0.06,0.002,0.05)))                  # bachi-kawa patch
    P.append(C.prim('cube', 6, loc=(cx+hx+0.002,0.0,cz), scale=(0.014,0.074,0.18), bevel=0.004))      # red cloth on the side
    P.append(C.prim('cube', 1, loc=(0,0,cz-hz-0.012), scale=(0.03,0.04,0.024), bevel=0.004))          # neck tail
    P.append(C.prim('cube', 4, loc=(0,-0.046,cz-0.05), scale=(0.036,0.007,0.008)))                     # koma bridge
    for x in (-0.009,0.0,0.009):
        P.append(C.prim('cyl', 5, loc=(x,-0.047,(-0.17+cz-hz-0.02)/2), scale=(0.0015,0.0015,cz-hz-0.02+0.17), verts=6))
    P.append(C.shape_profile('sh_bachi', [(-0.09,cz-0.03),(-0.02,cz-0.075),(-0.035,cz-0.04),(-0.11,cz+0.05),(-0.125,cz+0.04),(-0.05,cz-0.045)], 0.006, -0.05, 4, bevel=0.002))
    return P
""",
  f"'neck': C.add_wood(C.mat('sh_neck',(0.08,0.015,0.01),rough=0.25,coat=0.9),(0.05,0.008,0.005),(0.12,0.03,0.015),scale=6.0), "
  f"'frame': {wood('sh_frame',(0.09,0.03,0.012),(0.06,0.02,0.008),(0.13,0.05,0.02))}, 'skin': C.mat('sh_skin',(0.93,0.91,0.86),rough=0.6), "
  f"'ivory': C.mat('sh_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.6), 'silk': C.mat('sh_silk',(0.95,0.9,0.7),rough=0.5), "
  f"'red': C.mat('sh_red',(0.6,0.02,0.03),rough=0.7), 'patch': C.mat('sh_patch',(0.75,0.68,0.55),rough=0.6), 'gold': {metal('sh_gold',(1.0,0.75,0.35))}",
  "C.mat(name,(0.012,0.01,0.01),rough=0.12,coat=1.0)")

# ------------------------------------------------------------------ 59 shanai (shehnai)
asset('shanai', 159, 59,
  'Jewelbox 59 Shehnai: the conical dark-wood pipe (top line flush with the paddle) with brass bands and seven finger holes is the striker; '
  'a flared brass bell at the right; the brass staple with red thread and the double reed at the left, and spare reeds with an ivory pin and tassel hanging on a cord.',
  ['body','brass','dark','reed','thread','ivory'], [1.0,0.85,0.55], '''
def build(C, variant=None):
    rr = lambda x: 0.03 + (x+0.27)*0.045; zz = lambda x: 0.045 - rr(x)
    xs = [-0.27 + 0.43*k/20 for k in range(21)]
    P = [tube3(C, 0, [(x,0.0,zz(x)) for x in xs], [rr(x) for x in xs], n=32, smooth=1)]               # conical body, top line flush
    for x in (-0.255,-0.15,0.06,0.15): P.append(ferrule(C, 1, x, rr(x), zz(x), w=0.014, extra=0.003))
    for x in (-0.11,-0.075,-0.04,-0.005,0.03,0.09,0.12): P.append(hole(C, 2, x, rr(x), zz(x), 0.009))
    bx = [0.155 + 0.15*k/16 for k in range(17)]
    br = [rr(0.155) + (0.1-rr(0.155))*(k/16)**2.2 for k in range(17)]
    P.append(tube3(C, 1, [(x,0.0,zz(x)) for x in bx], br, n=40, cap0=False, cap1=False, smooth=1))   # brass bell (same straight axis)
    e = bx[-2]; P.append(C.prim('cyl', 2, loc=(e,0.0,zz(e)), rot=(0,math.pi/2,0), scale=(br[-2]*0.95,br[-2]*0.95,0.004), verts=40))
    z0 = zz(-0.27)
    P.append(tube3(C, 1, [(-0.272,0.0,z0),(-0.292,0.0,z0)], [0.013,0.008], n=16, smooth=1))           # staple
    P.append(tube3(C, 4, [(-0.276,0.0,z0),(-0.288,0.0,z0)], [0.0125,0.0095], n=16, smooth=1))         # red thread
    P.append(C.prim('sphere', 3, loc=(-0.299,0.0,z0), scale=(0.01,0.004,0.011), verts=20))           # double reed (broad face to camera)
    P.append(C.prim('cyl', 4, loc=(-0.20,0.0,-0.055), scale=(0.002,0.002,0.13), verts=6))             # cord for spare reeds
    P.append(C.prim('cyl', 5, loc=(-0.20,0.0,-0.12), rot=(0,math.pi/2,0), scale=(0.003,0.003,0.07), verts=8))   # ivory pin
    for dx in (-0.02, 0.02): P.append(C.prim('sphere', 3, loc=(-0.20+dx,0.0,-0.135), scale=(0.008,0.003,0.014), verts=12))
    P.append(tube3(C, 4, [(-0.20,0.0,-0.122),(-0.20,0.0,-0.17),(-0.20,0.0,-0.2)], [0.005,0.016,0.022], n=16, smooth=1))   # tassel
    return P
''',
  f"'brass': {metal('sn_brass',(0.92,0.66,0.3))}, 'dark': C.mat('sn_dark',(0.01,0.006,0.003),rough=0.7), "
  f"'reed': C.mat('sn_reed',(0.8,0.65,0.35),rough=0.5), 'thread': C.mat('sn_thread',(0.7,0.04,0.04),rough=0.6), "
  f"'ivory': C.mat('sn_ivory',(0.92,0.88,0.78),rough=0.3)",
  "C.add_wood(C.mat(name,(0.07,0.03,0.012),rough=0.25,coat=0.9),(0.04,0.017,0.007),(0.11,0.05,0.02),scale=6.0)")

# ------------------------------------------------------------------ 61 woodblock & castanets
asset('woodblock_castanets', 161, 61,
  'Jewelbox 61 Woodblock & Castanets: a glossy rosewood slotted woodblock is the striker (two dark resonance slits along its face); '
  'two pairs of ebony-brown flamenco castanets hang under it on red cords, each pair slightly open like a clam.',
  ['body','dark','shell','cord'], [1.0,0.8,0.55], '''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,-0.03), scale=(0.62,0.12,0.15), bevel=0.016)]                     # woodblock (struck)
    for z in (0.013,-0.073): P.append(C.prim('cube', 1, loc=(0.02,-0.057,z), scale=(0.52,0.01,0.012), bevel=0.004))
    for x in (-0.17, 0.17):
        P.append(C.prim('cyl', 3, loc=(x,0.0,-0.125), scale=(0.004,0.004,0.045), verts=8))            # cord
        P.append(C.prim('torus', 3, loc=(x,0.0,-0.152), rot=(math.pi/2,0,0), scale=(0.022,0.004), verts=24))
        P.append(C.prim('cube', 2, loc=(x,0.0,-0.168), scale=(0.05,0.05,0.024), bevel=0.008))         # ears
        P.append(C.prim('sphere', 2, loc=(x+0.006,0.016,-0.245), scale=(0.075,0.022,0.082), verts=32))   # back shell
        P.append(C.prim('sphere', 2, loc=(x-0.008,-0.018,-0.25), rot=(0,0.14,0), scale=(0.075,0.022,0.082), verts=32))  # front shell
        P.append(C.prim('torus', 1, loc=(x-0.008,-0.03,-0.25), rot=(math.pi/2,0,0), scale=(0.045,0.003), verts=32))   # carved ring
    return P
''',
  f"'dark': C.mat('wc_dark',(0.01,0.004,0.002),rough=0.7), "
  f"'shell': {wood('wc_shell',(0.035,0.016,0.008),(0.02,0.009,0.004),(0.07,0.035,0.015),rough=0.2,coat=1.0,scale=5.0)}, "
  f"'cord': C.mat('wc_cord',(0.7,0.03,0.03),rough=0.6)",
  "C.add_wood(C.mat(name,(0.16,0.04,0.015),rough=0.2,coat=1.0),(0.1,0.025,0.01),(0.24,0.07,0.03),scale=5.0)")

# ------------------------------------------------------------------ 63 saw lead
asset('saw_lead', 163, 63,
  'Jewelbox 63 Synth Lead Sawtooth: a vintage analog monosynth - brushed-aluminium top rail is the striker; black front panel with a row of '
  'knobs, a glowing cyan screen showing a pink sawtooth wave, walnut end cheeks and a mini keyboard; a pink neon SAWTOOTH sign on an acrylic plate hangs below on two chains.',
  ['body','cheek','panel','knob','cap','keyw','keyb','screen','neon','acryl'], [0.6,0.9,1.0], '''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.03), scale=(0.58,0.14,0.03), bevel=0.006)]                       # aluminium top rail (struck)
    P.append(C.prim('cube', 2, loc=(0,0,-0.07), scale=(0.58,0.14,0.17), bevel=0.01))                  # black case
    for x in (-0.29, 0.29): P.append(C.prim('cube', 1, loc=(x,0,-0.06), scale=(0.035,0.15,0.21), bevel=0.01))   # walnut cheeks
    for i, x in enumerate((-0.03,0.03,0.09,0.15,0.21,-0.25)):
        P.append(C.prim('cyl', 3, loc=(x,-0.074,-0.005), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.012), verts=24))
        P.append(C.prim('cyl', 4, loc=(x,-0.081,-0.005), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.004), verts=20))
    P.append(C.prim('cube', 7, loc=(-0.14,-0.072,-0.03), scale=(0.15,0.004,0.06), bevel=0.003))       # screen
    for k in range(3):                                                                                  # sawtooth trace on the screen
        x0 = -0.2 + 0.04*k
        P.append(bar(C, (x0,-0.05), (x0+0.04,-0.01), 0.004, 0.003, 8, -0.075))
        P.append(bar(C, (x0+0.04,-0.01), (x0+0.0401,-0.05), 0.004, 0.003, 8, -0.075))
    for k in range(17):                                                                                 # mini keyboard
        x = -0.24 + 0.03*k
        P.append(C.prim('cube', 5, loc=(x,-0.072,-0.12), scale=(0.027,0.012,0.06), bevel=0.002))
        if k % 7 not in (2, 6) and k < 16: P.append(C.prim('cube', 6, loc=(x+0.015,-0.08,-0.105), scale=(0.016,0.01,0.034), bevel=0.002))
    for x in (-0.2, 0.2): P.append(C.prim('cyl', 3, loc=(x,0.0,-0.19), scale=(0.003,0.003,0.07), verts=6))    # chains
    P.append(C.prim('cube', 9, loc=(0,0.0,-0.29), scale=(0.6,0.012,0.14), bevel=0.01))               # acrylic plate
    pts = [(-0.26,-0.34),(-0.1,-0.24),(-0.1,-0.34),(0.06,-0.24),(0.06,-0.34),(0.22,-0.24),(0.22,-0.34)]
    for a, b in zip(pts[:-1], pts[1:]): P.append(rod(C, (a[0],a[1],-0.014), b, 0.009, 8))           # neon tube segments
    for x, z in pts: P.append(C.prim('sphere', 8, loc=(x,-0.014,z), scale=(0.009,0.009,0.009), verts=12))   # rounded corners
    return P
''',
  f"'cheek': {wood('sl_cheek',(0.1,0.04,0.015),(0.06,0.024,0.009),(0.15,0.07,0.03))}, 'panel': C.mat('sl_panel',(0.012,0.012,0.014),rough=0.35,coat=0.4), "
  f"'knob': C.mat('sl_knob',(0.02,0.02,0.02),rough=0.3), 'cap': C.mat('sl_cap',(0.9,0.35,0.05),rough=0.3,coat=0.5), "
  f"'keyw': C.mat('sl_keyw',(0.9,0.89,0.85),rough=0.2,coat=0.6), 'keyb': C.mat('sl_keyb',(0.015,0.015,0.017),rough=0.15,coat=1.0), "
  f"'screen': {glow('sl_screen',(0.05,0.6,0.9),3.0,(0.02,0.1,0.15))}, 'neon': {glow('sl_neon',(1.0,0.05,0.45),6.0,(0.6,0.02,0.25))}, "
  f"'acryl': C.mat('sl_acryl',(0.008,0.008,0.02),rough=0.15,coat=1.0)",
  "C.mat(name,(0.8,0.8,0.82),rough=0.25,metal=1.0)")

# ------------------------------------------------------------------ 64 new age pad
asset('new_age_pad', 164, 64,
  'Jewelbox 64 Synth Pad New Age (Fantasia): a lilac opal crystal bar with gold end caps is the striker; a glowing crystal ball (violet nebula '
  'core in clear glass) hangs beneath it on three gold chains, held in a gold claw cradle with a tassel; little glowing stars hang from the bar on threads.',
  ['body','gold','glass','core','star','tassel'], [0.8,0.7,1.0], '''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.02), scale=(0.56,0.1,0.05), bevel=0.02)]                        # opal crystal bar (struck)
    for x in (-0.295, 0.295): P.append(C.prim('cube', 1, loc=(x,0,0.02), scale=(0.03,0.11,0.05), bevel=0.008))
    P.append(C.prim('cube', 1, loc=(0,-0.051,-0.0), scale=(0.54,0.003,0.004)))
    cz, R = -0.235, 0.15
    for x in (-0.12, 0.0, 0.12): P.append(rod(C, (x,-0.005,0.0), (0.0,-0.075), 0.0025, 1, 8))         # chains
    P.append(C.prim('sphere', 1, loc=(0,0,-0.08), scale=(0.045,0.045,0.028), verts=32))               # cap
    P.append(C.prim('sphere', 2, loc=(0,0,cz), scale=(R,R,R), verts=64))                               # glass ball
    P.append(C.prim('sphere', 3, loc=(0,0,cz), scale=(0.085,0.085,0.085), verts=48))                   # glowing nebula core
    for dx, dz in ((-0.05,0.05),(0.06,-0.03),(0.02,0.07)): P.append(C.prim('sphere', 4, loc=(dx,-0.02,cz+dz), scale=(0.012,0.012,0.012), verts=12))
    for ph in (0.0, 2.1, 4.2):                                                                          # gold claw cradle
        pts = [((R+0.008)*math.cos(t)*math.cos(ph), (R+0.008)*math.cos(t)*math.sin(ph), cz+(R+0.008)*math.sin(t)) for t in [-math.pi/2 + (math.pi/2-0.35)*k/12 for k in range(13)]]
        P.append(tube3(C, 1, pts, 0.007, n=12, smooth=1))
    P.append(C.prim('sphere', 1, loc=(0,0,cz-R-0.012), scale=(0.025,0.025,0.02), verts=24))
    P.append(tube3(C, 5, [(0,0,cz-R-0.03),(0,0,cz-R-0.08),(0,0,cz-R-0.11)], [0.006,0.02,0.026], n=20, smooth=1))   # tassel
    for x, z in ((-0.24,-0.15),(0.24,-0.12),(-0.17,-0.25),(0.19,-0.27)):                               # hanging stars
        P.append(C.prim('cyl', 1, loc=(x,0.0,(-0.005+z)/2), scale=(0.0015,0.0015,abs(z+0.005)), verts=6))
        star = [(x + (0.03 if k % 2 == 0 else 0.013)*math.sin(math.pi*k/5), z - 0.03 + (0.03 if k % 2 == 0 else 0.013)*math.cos(math.pi*k/5)) for k in range(10)]
        P.append(C.shape_profile(f'na_star{x}', star, 0.01, -0.005, 4, bevel=0.002))
    return P
''',
  f"'gold': {metal('na_gold',(1.0,0.75,0.35),0.12)}, 'glass': C.mat('na_glass',(0.8,0.85,1.0),rough=0.0,trans=1.0,ior=1.3), "
  f"'core': {glow('na_core',(0.45,0.15,1.0),3.5,(0.2,0.05,0.5))}, 'star': {glow('na_star',(1.0,0.75,0.3),4.0)}, "
  f"'tassel': C.mat('na_tassel',(0.45,0.15,0.6),rough=0.6)",
  "C.mat(name,(0.8,0.7,0.95),rough=0.15,coat=1.0)")
print('wrote jewelbox F6 assets')
