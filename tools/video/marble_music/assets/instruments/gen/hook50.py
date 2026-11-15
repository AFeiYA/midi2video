"""hook50 asset folders (bells_castanets, music_box, koto, pixel8bit, bagpipe, finale): build.py / material.py / meta.json.
Moved into the repo from the hook50 work dir; regenerate with  python gen/hook50.py  (no bpy needed)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, PINS, CONTACT

# ------------------------------------------------------------------ 01 tubular bells + castanets
write('bells_castanets', dict(name='bells_castanets', section=13, priority=5, tracks_regex='tubular.*castanet',
  description='hook50 section 01: polished brass chime rail (struck) with six graded brass tubes (crown caps, world-vertical, meta.hanging) and a red-corded castanet pair hanging off the right end of the rail, behind the marble plane.',
  slots=['body','tube','dark','cap','shell','cord','pin'], flash_slot='body', flash_color=[1.0,0.78,0.38],
  hanging=[{"attach":[x,0.222,0.0],"radius":0.03,"inner":0.022,"length":L,"role":"tube","cap_role":"cap"} for x,L in
           zip((-0.25,-0.15,-0.05,0.05,0.15,0.25),(0.56,0.51,0.46,0.41,0.36,0.31))]),
'''"""bells_castanets (hook50 01): brass chime rail with black end knobs; castanet pair (front + back shell, red cord) hangs off the right end, behind the marble plane."""
'''+HDR+'''
def build(C, variant=None):
    rail = C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.12,0.09), bevel=0.014)
    ends = [C.prim('sphere', 2, loc=(x,0.0,0.0), scale=(0.03,0.06,0.044), verts=24) for x in (-0.29,0.29)]
    beam = C.prim('cube', 2, loc=(0,0.215,0.0), scale=(0.66,0.05,0.035), bevel=0.008)      # dark hanger beam behind the rail
    hooks = [C.prim('cyl', 3, loc=(x,0.215,0.0), scale=(0.012,0.012,0.05), verts=12) for x in (-0.25,-0.15,-0.05,0.05,0.15,0.25)]
    # castanet pair hanging off the right end of the beam
    cx, cz = 0.47, -0.21
    cord = C.prim('cyl', 5, loc=(0.40,0.2,-0.06), rot=(0,-0.5,0), scale=(0.009,0.009,0.15), verts=10)
    shA = C.prim('sphere', 4, loc=(cx,0.195,cz), scale=(0.13,0.032,0.14), verts=48)
    rimA = C.prim('torus', 2, loc=(cx,0.168,cz), rot=(math.pi/2,0,0), scale=(0.125,0.008), verts=56)
    shB = C.prim('sphere', 4, loc=(cx+0.08,0.25,cz-0.04), scale=(0.13,0.03,0.14), verts=48)
    knot = C.prim('sphere', 5, loc=(cx-0.04,0.17,cz+0.13), scale=(0.03,0.02,0.03), verts=16)
    return [rail, beam, cord, shA, rimA, shB, knot] + ends + hooks
''',
'''"""bells_castanets materials"""
def shared(C):
    return {'tube': C.mat('bc_tube',(0.95,0.68,0.26),rough=0.12,metal=1.0), 'cap': C.mat('bc_cap',(0.80,0.48,0.14),rough=0.08,metal=1.0),
            'dark': C.mat('bc_dark',(0.03,0.025,0.02),rough=0.35,coat=0.6),
            'shell': C.add_wood(C.mat('bc_shell',(0.32,0.09,0.04),rough=0.3,coat=0.7),(0.20,0.05,0.02),(0.50,0.18,0.07)),
            'cord': C.mat('bc_cord',(0.75,0.03,0.03),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.93,0.66,0.27),rough=0.12,metal=1.0)
''')

# ------------------------------------------------------------------ 02 music box
write('music_box', dict(name='music_box', section=14, tracks_regex='music box',
  description='hook50 section 02: brass music-box comb (struck: solid top strip + row of graded tines) above a pinned brass cylinder, all on a walnut box with an open red-velvet lid, gold keyhole and a winding key, behind the marble plane.',
  slots=['body','wood','velvet','brass','dark','pin'], flash_slot='body', flash_color=[1.0,0.85,0.5]),
'''"""music_box (hook50 02): brass comb (struck) + pinned cylinder + walnut box with open red-velvet lid and winding key."""
'''+HDR+'''
def build(C, variant=None):
    P = []
    P.append(C.prim('cube', 0, loc=(0,0,0.0275), scale=(0.62,0.20,0.035), bevel=0.006))         # comb base strip (contact top z=0.045)
    n = 17
    for i in range(n):                                                                            # tines, graded (long bass -> short treble)
        x = -0.28 + 0.56*i/(n-1); L = 0.06 - 0.025*i/(n-1)
        P.append(C.prim('cube', 0, loc=(x,0.0,0.01-L/2), scale=(0.022,0.16,L), bevel=0.003))
    # behind the marble plane: pinned cylinder
    cyl = C.prim('cyl', 3, loc=(0,0.2,-0.115), rot=(0,math.pi/2,0), scale=(0.055,0.055,0.52), verts=40); P.append(cyl)
    for i in range(26):
        x = -0.24 + 0.48*((i*7)%26)/25; a = (i*2.39)%(math.pi)-math.pi/2
        P.append(C.prim('sphere', 3, loc=(x,0.2-0.055*math.cos(a)*0.9,-0.115+0.055*math.sin(a)), scale=(0.008,0.008,0.008), verts=8, smooth=False))
    for x in (-0.275,0.275): P.append(C.prim('cyl', 4, loc=(x,0.2,-0.115), rot=(0,math.pi/2,0), scale=(0.07,0.07,0.02), verts=32))
    # walnut box (front face toward the camera)
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.29), scale=(0.70,0.12,0.24), bevel=0.02))
    P.append(C.prim('cube', 3, loc=(0,0.153,-0.29), scale=(0.62,0.004,0.17), bevel=0.003))       # brass inlay frame
    P.append(C.prim('cube', 1, loc=(0,0.150,-0.29), scale=(0.58,0.004,0.14), bevel=0.003))       # inner panel
    P.append(C.prim('cyl', 4, loc=(0,0.146,-0.27), rot=(math.pi/2,0,0), scale=(0.018,0.018,0.006), verts=20))   # keyhole
    P.append(C.prim('cube', 4, loc=(0,0.146,-0.295), scale=(0.012,0.006,0.03)))
    # open lid behind: red velvet inside face toward camera, walnut rim
    P.append(C.shape_profile('mb_lid', [(-0.35,-0.16),(0.35,-0.16),(0.35,0.20),(-0.35,0.20)], 0.02, 0.265, 1, bevel=0.01))
    P.append(C.shape_profile('mb_velvet', [(-0.32,-0.14),(0.32,-0.14),(0.32,0.17),(-0.32,0.17)], 0.004, 0.261, 2))
    # winding key on the right side
    P.append(C.prim('cyl', 3, loc=(0.385,0.215,-0.27), rot=(0,math.pi/2,0), scale=(0.012,0.012,0.07), verts=12))
    P.append(C.prim('torus', 3, loc=(0.45,0.215,-0.24), rot=(math.pi/2,0,0), scale=(0.04,0.01), verts=24))
    P.append(C.prim('torus', 3, loc=(0.45,0.215,-0.30), rot=(math.pi/2,0,0), scale=(0.04,0.01), verts=24))
    return P
''',
'''"""music_box materials"""
def shared(C):
    return {'wood': C.add_wood(C.mat('mb_wood',(0.25,0.12,0.06),rough=0.3,coat=0.8),(0.12,0.05,0.02),(0.38,0.19,0.08),scale=8.0),
            'velvet': C.mat('mb_velvet',(0.45,0.02,0.04),rough=0.95), 'brass': C.mat('mb_brass',(0.9,0.66,0.3),rough=0.18,metal=1.0),
            'dark': C.mat('mb_dark',(0.03,0.02,0.015),rough=0.4,metal=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.95,0.75,0.38),rough=0.1,metal=1.0)
''')

# ------------------------------------------------------------------ 06 koto
write('koto', dict(name='koto', section=15, tracks_regex='koto',
  description='hook50 section 06: rosewood koto edge (struck) above a face-on paulownia koto board with silk strings (7 drawn so they read at video scale), a diagonal row of ivory bridges (ji) and dark rosewood end caps with gold trim, behind the marble plane.',
  slots=['body','board','string','bridge','trim','pin'], flash_slot='body', flash_color=[1.0,0.8,0.5], flash_slots=['body','string']),
'''"""koto (hook50 06): rosewood edge rail (struck) + face-on paulownia board, 13 strings, diagonal ivory bridges, rosewood end caps."""
'''+HDR+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.16,0.09), bevel=0.012)]
    for x in (-0.2,0.0,0.2): P.append(C.prim('cube', 4, loc=(x,-0.0805,0.0), scale=(0.006,0.002,0.07)))   # gold inlay ticks on the front face
    # board (slightly bowed top edge), behind the marble plane
    pts = [(-0.46,-0.30)]
    for i in range(13): x = -0.46 + 0.92*i/12; pts.append((x, -0.035 + 0.02*(1-(x/0.46)**2)))
    pts.append((0.46,-0.30))
    P.append(C.shape_profile('koto_board', pts, 0.07, 0.19, 1, bevel=0.015))
    for x in (-0.47,0.47): P.append(C.prim('cube', 0, loc=(x,0.215,-0.165), scale=(0.07,0.07,0.29), bevel=0.012))  # rosewood end caps
    for x in (-0.43,0.43): P.append(C.prim('cube', 4, loc=(x,0.178,-0.165), scale=(0.008,0.004,0.27)))            # gold trim
    for i in range(13):
        z = -0.06 - 0.017*i
        if i % 2 == 0: P.append(C.prim('cyl', 2, loc=(0,0.183,z), rot=(0,math.pi/2,0), scale=(0.0012,0.0012,0.84), verts=6))
        bx = 0.25 - 0.4*i/12
        P.append(C.shape_profile(f'ji{i}', [(bx-0.02,z-0.007),(bx+0.02,z-0.007),(bx+0.005,z+0.007),(bx-0.005,z+0.007)], 0.016, 0.168, 3))
    return P
''',
'''"""koto materials"""
def shared(C):
    return {'board': C.add_wood(C.mat('ko_board',(0.05,0.02,0.007),rough=0.5,coat=0.0),(0.03,0.011,0.004),(0.11,0.045,0.014),scale=3.0,rings=1.2),
            'string': C.mat('ko_string',(0.4,0.32,0.15),rough=0.5), 'bridge': C.mat('ko_bridge',(0.98,0.96,0.9),rough=0.2,coat=0.5),
            'trim': C.mat('ko_trim',(0.92,0.7,0.3),rough=0.15,metal=1.0)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.08,0.025,0.015),rough=0.3,coat=0.8); return C.add_wood(m,(0.04,0.012,0.008),(0.16,0.05,0.025))
''')

# ------------------------------------------------------------------ 07 8-bit square lead
BITMAP = ["....XXXX..","....X..XX.","....X...X.","....X.....","....X.....","..XXX.....",".XXXX.....",".XXXX.....","..XX......"]
write('pixel8bit', dict(name='pixel8bit', section=16, tracks_regex='8-bit|square lead|chiptune',
  description='hook50 section 07: a row of seven glossy pixel blocks (struck; colour cycles key to key) above a glowing voxel 8-bit eighth-note on a dark console plate with a d-pad and two buttons, behind the marble plane.',
  slots=['body','plate','glow','accent','pin'], flash_slot='body', flash_color=[0.6,1.0,1.0]),
'''"""pixel8bit (hook50 07): seven pixel blocks (struck) + glowing voxel eighth-note on a dark console plate with d-pad and A/B buttons."""
'''+HDR+'''BITMAP = %r
def build(C, variant=None):
    P = []
    w = 0.62/7
    for i in range(7):
        x = -0.31 + w*(i+0.5)
        P.append(C.prim('cube', 0, loc=(x,0,0.0), scale=(w-0.006,0.20,0.09), bevel=0.008, smooth=False))
        P.append(C.prim('cube', 3, loc=(x,-0.1,0.0), scale=(w*0.42,0.004,0.036), smooth=False))          # lit pixel inset on the front face
    P.append(C.prim('cube', 1, loc=(0,0.24,-0.27), scale=(0.70,0.06,0.48), bevel=0.03))                 # console plate
    s = 0.046
    for r, row in enumerate(BITMAP):
        for c, ch in enumerate(row):
            if ch == 'X': P.append(C.prim('cube', 2, loc=(-0.31 + c*s, 0.195, -0.08 - r*s), scale=(s*0.92,0.04,s*0.92), smooth=False))
    # d-pad + buttons on the right of the plate
    P.append(C.prim('cube', 3, loc=(0.23,0.205,-0.36), scale=(0.09,0.03,0.03), smooth=False))
    P.append(C.prim('cube', 3, loc=(0.23,0.205,-0.36), scale=(0.03,0.03,0.09), smooth=False))
    for x, z in ((0.17,-0.46),(0.27,-0.46)): P.append(C.prim('cyl', 2, loc=(x,0.205,z), rot=(math.pi/2,0,0), scale=(0.028,0.028,0.03), verts=20))
    return P
''' % BITMAP,
'''"""pixel8bit materials: glossy candy-coloured blocks, emissive pixels."""
import colorsys
PAL = [0.0, 0.08, 0.15, 0.33, 0.5, 0.62, 0.8]
def shared(C):
    g = C.mat('px_glow',(0.2,0.95,1.0),rough=0.3); b = g.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (0.25,0.95,1.0,1); b.inputs['Emission Strength'].default_value = 6.0
    return {'plate': C.mat('px_plate',(0.03,0.03,0.045),rough=0.35,coat=0.5), 'glow': g, 'accent': C.mat('px_accent',(0.9,0.9,0.9),rough=0.25,coat=0.6)}
def body(C, name, j, note, variant):
    r, g, b = colorsys.hsv_to_rgb(PAL[j %% len(PAL)], 1.0, 0.45)
    return C.mat(name,(r,g,b),rough=0.2,coat=0.8)
'''.replace('%%','%'))

# ------------------------------------------------------------------ 08 bagpipe
write('bagpipe', dict(name='bagpipe', section=17, tracks_regex='bagpipe',
  description='hook50 section 08: black drone pipe with ivory ferrules (struck) on top of a red tartan bag, with two more drones rising up-left, a chanter hanging down and red tassel cords, behind the marble plane.',
  slots=['body','tartan','ivory','pipe','cord','pin'], flash_slot='body', flash_color=[1.0,0.7,0.4]),
'''"""bagpipe (hook50 08): blackwood drone (struck) on a tartan bag with two tall drones, chanter and cords."""
'''+HDR+'''
def pipe(C, a, b, r, mi):
    ax, az = a; bx, bz = b; L = math.hypot(bx-ax, bz-az); ang = math.atan2(bx-ax, bz-az)
    return C.prim('cyl', mi, loc=((ax+bx)/2, 0.24, (az+bz)/2), rot=(0, ang, 0), scale=(r, r, L), verts=20)
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0,0,0.0), rot=(0,math.pi/2,0), scale=(0.045,0.045,0.62), verts=40)]
    for x in (-0.27,-0.09,0.09,0.27): P.append(C.prim('cyl', 2, loc=(x,0,0.0), rot=(0,math.pi/2,0), scale=(0.0452,0.0452,0.03), verts=40))
    P.append(C.prim('sphere', 1, loc=(0.02,0.215,-0.21), scale=(0.29,0.06,0.19), verts=48))          # tartan bag
    # two tall drones rising up-left behind, ivory tops
    for (a, b, r) in (((-0.12,-0.06),(-0.42,0.36),0.03), ((-0.02,-0.05),(-0.26,0.44),0.028)):
        P.append(pipe(C, a, b, r, 3))
        P.append(C.prim('cyl', 2, loc=(b[0],0.24,b[1]), rot=(0, math.atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(r*1.5, r*1.5, 0.05), verts=20))
    P.append(pipe(C, (0.2,-0.33), (0.3,-0.62), 0.024, 3))                                             # chanter
    P.append(C.prim('cyl', 2, loc=(0.3,0.24,-0.63), scale=(0.035,0.035,0.04), verts=20))
    P.append(pipe(C, (0.26,-0.1), (0.44,0.06), 0.016, 3))                                             # blowpipe
    for (a, b) in (((-0.3,0.2),(-0.12,-0.08)), ((-0.2,0.26),(-0.04,-0.06))):                          # red cords
        P.append(C.prim('cyl', 4, loc=((a[0]+b[0])/2, 0.17, (a[1]+b[1])/2), rot=(0, math.atan2(b[0]-a[0], b[1]-a[1]), 0), scale=(0.007,0.007,math.hypot(b[0]-a[0], b[1]-a[1])), verts=8))
    P.append(C.prim('sphere', 4, loc=(-0.14,0.16,-0.1), scale=(0.022,0.015,0.035), verts=12))
    return P
''',
'''"""bagpipe materials: Royal-Stewart-ish procedural tartan."""
def tartan(C):
    m = C.mat('bp_tartan',(0.6,0.03,0.03),rough=0.85); nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Object'], sp.inputs[0])
    def band(sock, freq, width):
        mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = freq; L(sock, mu.inputs[0])
        fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; L(mu.outputs[0], fr.inputs[0])
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = width; L(fr.outputs[0], lt.inputs[0]); return lt.outputs[0]
    def mx(fac, c1sock, c2):
        n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; L(fac, n.inputs['Factor'])
        if isinstance(c1sock, tuple): n.inputs[6].default_value = (*c1sock, 1)
        else: L(c1sock, n.inputs[6])
        n.inputs[7].default_value = (*c2, 1); return n.outputs[2]
    bx = band(sp.outputs['X'], 7.0, 0.32); bz = band(sp.outputs['Z'], 7.0, 0.32)
    both = nt.nodes.new('ShaderNodeMath'); both.operation = 'MULTIPLY'; L(bx, both.inputs[0]); L(bz, both.inputs[1])
    any_ = nt.nodes.new('ShaderNodeMath'); any_.operation = 'MAXIMUM'; L(bx, any_.inputs[0]); L(bz, any_.inputs[1])
    c = mx(any_.outputs[0], (0.62,0.03,0.03), (0.05,0.16,0.07))       # red ground, green bands
    c = mx(both.outputs[0], c, (0.01,0.03,0.08))                      # navy where bands cross
    yx = band(sp.outputs['X'], 7.0, 0.04); yz = band(sp.outputs['Z'], 7.0, 0.04)
    y = nt.nodes.new('ShaderNodeMath'); y.operation = 'MAXIMUM'; L(yx, y.inputs[0]); L(yz, y.inputs[1])
    c = mx(y.outputs[0], c, (0.85,0.7,0.1))                           # thin yellow over-check
    L(c, b.inputs['Base Color']); return m
def shared(C):
    return {'tartan': tartan(C), 'ivory': C.mat('bp_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.5),
            'pipe': C.mat('bp_pipe',(0.025,0.02,0.018),rough=0.25,coat=0.8), 'cord': C.mat('bp_cord',(0.7,0.04,0.04),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.03,0.025,0.022),rough=0.2,coat=0.9)
''')

# ------------------------------------------------------------------ 09 finale
write('finale', dict(name='finale', section=18, priority=5, tracks_regex='tutti|finale',
  description='hook50 section 09 (single-marble tutti finale): polished gold bar (struck) with a gold Christmas star behind it, a red ribbon bow and two gold jingle bells on red cords, behind the marble plane.',
  slots=['body','star','ribbon','bell','dark','pin'], flash_slot='body', flash_color=[1.0,0.85,0.45]),
'''"""finale (hook50 09): gold bar (struck) + gold star + red bow + two jingle bells."""
'''+HDR+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.0), scale=(0.62,0.16,0.09), bevel=0.02)]
    pts = []
    for i in range(10):
        r = 0.27 if i % 2 == 0 else 0.11; a = math.pi/2 + i*math.pi/5
        pts.append((r*math.cos(a), -0.27 + r*math.sin(a)))
    P.append(C.shape_profile('fin_star', pts, 0.05, 0.2, 1, bevel=0.012))
    # red bow just below the bar
    for s in (-1, 1):
        P.append(C.prim('sphere', 2, loc=(s*0.07,0.17,-0.06), rot=(0, s*0.5, 0), scale=(0.07,0.02,0.04), verts=24))
        P.append(C.prim('cube', 2, loc=(s*0.05,0.172,-0.12), rot=(0, s*0.35, 0), scale=(0.03,0.01,0.11)))
    P.append(C.prim('sphere', 2, loc=(0,0.165,-0.06), scale=(0.028,0.02,0.028), verts=16))
    # jingle bells on cords at both sides
    for s in (-1, 1):
        bx = s*0.36
        P.append(C.prim('cyl', 2, loc=(s*0.33,0.19,-0.07), rot=(0, -s*0.4, 0), scale=(0.006,0.006,0.15), verts=8))
        P.append(C.prim('sphere', 3, loc=(bx,0.2,-0.18), scale=(0.06,0.06,0.06), verts=32))
        P.append(C.prim('cube', 4, loc=(bx,0.14,-0.19), scale=(0.07,0.01,0.008)))
        P.append(C.prim('sphere', 4, loc=(bx,0.143,-0.21), scale=(0.012,0.006,0.012), verts=12))
    return P
''',
'''"""finale materials"""
def shared(C):
    st = C.mat('fin_star',(1.0,0.72,0.25),rough=0.15,metal=1.0); b = st.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (1.0,0.7,0.3,1); b.inputs['Emission Strength'].default_value = 0.6
    return {'star': st, 'ribbon': C.mat('fin_ribbon',(0.7,0.02,0.04),rough=0.35,coat=0.6),
            'bell': C.mat('fin_bell',(0.95,0.7,0.3),rough=0.1,metal=1.0), 'dark': C.mat('fin_dark',(0.02,0.015,0.01),rough=0.5)}
def body(C, name, j, note, variant):
    return C.mat(name,(1.0,0.76,0.32),rough=0.08,metal=1.0)
''')

# ------------------------------------------------------------------ 03 marimba v5
write('marimba/v5', dict(name='marimba', section=5, tracks_regex='marimba',
  description='v5 / hook50 03: arched honduras-rosewood bar (struck) above a face-on mini marimba keyboard: seven graded rosewood bars (long bass left, short treble right) on two cords between dark frame rails with brass nodes, behind the marble plane. No hanging tubes (they read as tubular bells).',
  slots=['body','cord','dark','bars','brass','pin'], flash_slot='body', flash_color=[1.0,0.6,0.3]),
'''"""marimba v5: arched rosewood bar (struck) + face-on keyboard of seven graded rosewood bars on cords + dark frame rails."""
'''+HDR+'''
def build(C, variant=None):
    pts = [(-0.31,0.045),(0.31,0.045),(0.31,-0.045)]
    n = 14
    for i in range(n+1):
        x = 0.22 - 0.44*i/n; pts.append((x, -0.045 + 0.038*(1-(x/0.22)**2)))
    pts.append((-0.31,-0.045))
    P = [C.shape_profile('marimba_bar', pts, 0.30, -0.15, 0, bevel=0.012)]
    P += [C.prim('cyl', 1, loc=(x,0.06,-0.015), rot=(math.pi/2,0,0), scale=(0.011,0.011,0.42), verts=12) for x in (-0.14,0.14)]
    nb = 7; w = 0.084; top = -0.06
    for i in range(nb):
        x = -0.30 + w/2 + i*(w+0.0093); L = 0.34 - 0.025*i
        P.append(C.prim('cube', 3, loc=(x,0.19,top-L/2), scale=(w,0.035,L), bevel=0.012))
        for zz in (top-0.22*L, top-0.78*L): P.append(C.prim('sphere', 4, loc=(x,0.17,zz), scale=(0.008,0.006,0.008), verts=10))
    for zf in (0.22, 0.78):   # cords through the bar nodes (follow the graded lengths)
        a = (-0.30+w/2, top-zf*0.34); b = (-0.30+w/2+6*(w+0.0093), top-zf*(0.34-0.15))
        L_ = math.hypot(b[0]-a[0], b[1]-a[1]); ang = math.atan2(b[0]-a[0], b[1]-a[1])
        P.append(C.prim('cyl', 1, loc=((a[0]+b[0])/2,0.168,(a[1]+b[1])/2), rot=(0,ang,0), scale=(0.004,0.004,L_+0.1), verts=8))
    P.append(C.prim('cube', 2, loc=(-0.335,0.22,-0.22), scale=(0.03,0.05,0.36), bevel=0.008))
    P.append(C.prim('cube', 2, loc=(0.335,0.22,-0.17), scale=(0.03,0.05,0.26), bevel=0.008))
    return P
''',
'''"""marimba v5 materials: deep rosewood bars, dark frame, brass nodes."""
def shared(C):
    return {'cord': C.mat('mar5_cord',(0.6,0.03,0.03),rough=0.7), 'dark': C.mat('mar5_dark',(0.02,0.018,0.015),rough=0.35,coat=0.5),
            'bars': C.add_wood(C.mat('mar5_bars',(0.2,0.05,0.02),rough=0.35,coat=0.5),(0.09,0.02,0.008),(0.30,0.09,0.035)),
            'brass': C.mat('mar5_brass',(0.9,0.65,0.3),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.2,0.05,0.02),rough=0.35,coat=0.5); return C.add_wood(m,(0.10,0.022,0.008),(0.30,0.09,0.035))
''')
print('ok')
