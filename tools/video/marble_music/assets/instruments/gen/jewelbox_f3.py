"""Jewelbox Orchestra (珠匣乐团) - family 3 (25-32: solo strings, string ensemble, choir, voice, orchestra hit).
All folders new and registry-only (tracks_regex NEVER). Bowed contrast with F2: violin / viola show a bow behind the body
(pizzicato 23 has none); cello / contrabass / string ensemble use the BOW itself as the striker, the instrument standing
upright behind it (upright bass 21 is plucked and lies horizontally)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assetgen import write, HDR, NEVER
from snippets import H

KEYPINS = [{"x":-0.15,"z":-0.03,"y_start":0.2,"radius":0.022},{"x":0.15,"z":-0.03,"y_start":0.2,"radius":0.022}]
FIDPINS = [{"x":0.10,"z":-0.07,"y_start":0.24,"radius":0.022},{"x":-0.10,"z":-0.07,"y_start":0.24,"radius":0.022}]

FID = '''
def fiddle(C, L, y, mi, eb, dk, st, pale, cx=0.0, cz=0.0, rot=0.0, endpin=0.0, pin_mi=None, bstrings=True, chin=False, slope=False, name='fid'):
    """violin-family instrument (body length L) modelled horizontally - neck toward -x, body centred at x=0, front face at y -
    then rotated by rot about Y (rot = pi/2 stands it upright, neck up) and moved to (cx, cz).
    mi body, eb ebony (fingerboard/tailpiece/pegs), dk dark (f-holes, purfling), st strings, pale bridge."""
    import bpy
    ins = violin_inside(L, 0.0)
    if slope:                                                                           # double bass: sloping shoulders
        base = ins
        def ins(x, z, base=base):
            if x < -0.02*L and x > -0.47*L:
                lim = 0.12*L + (0.20*L)*(x+0.47*L)/(0.45*L)
                if abs(z) > lim and x < -0.25*L: return False
            return base(x, z)
    d = 0.03 + 0.03*L; P = [plate(C, name+'_b', ins, y, d, mi, n=180, bevel=0.01)]
    P.append(plate(C, name+'_e', ins, y+0.004, d*0.8, dk, n=180, bevel=0.0)); P[-1].scale = (1.02, 1.0, 1.03)
    for s in (-1, 1):
        P.append(bar(C, (0.03*L,s*0.09*L), (0.17*L,s*0.13*L), 0.016*L, 0.005, dk, y-0.004))
        for xx, zz in ((0.03*L,0.085*L), (0.18*L,0.135*L)): P.append(C.prim('cyl', dk, loc=(xx,y-0.004,s*zz), rot=(math.pi/2,0,0), scale=(0.018*L,0.018*L,0.005), verts=10))
    P.append(C.prim('cube', eb, loc=(-0.38*L,y-0.012,0.0), scale=(0.80*L,0.014,0.10*L), bevel=0.004))      # fingerboard
    P.append(C.prim('cube', mi, loc=(-0.88*L,y,0.0), scale=(0.16*L,0.03,0.09*L), bevel=0.006))             # pegbox
    P.append(C.prim('torus', mi, loc=(-0.98*L,y,0.0), rot=(math.pi/2,0,0), scale=(0.05*L,0.022*L), verts=24))  # scroll
    P.append(C.prim('sphere', mi, loc=(-0.98*L,y,0.0), scale=(0.035*L,0.012,0.035*L), verts=16))
    for xx in (-0.84*L, -0.92*L):
        for s in (-1, 1): P.append(C.prim('cyl', eb, loc=(xx,y,s*0.09*L), scale=(0.012*L+0.004,0.012*L+0.004,0.07*L), verts=10))
    P.append(C.shape_profile(name+'_tp', [(0.26*L,-0.05*L),(0.44*L,-0.03*L),(0.44*L,0.03*L),(0.26*L,0.05*L)], 0.012, y-0.016, eb, bevel=0.004))
    if bstrings:
        P.append(C.prim('cube', pale, loc=(0.10*L,y-0.016,0.0), scale=(0.02,0.012,0.14*L), bevel=0.003))     # bridge
        for z in (-0.045*L,-0.015*L,0.015*L,0.045*L):
            P.append(C.prim('cyl', st, loc=(-0.25*L,y-0.022,z), rot=(0,math.pi/2,0), scale=(0.0025+0.002*L,0.0025+0.002*L,1.08*L), verts=8))
    if chin: P.append(C.prim('sphere', eb, loc=(0.36*L,y-0.01,0.13*L), scale=(0.07*L,0.012,0.05*L), verts=16))
    if endpin > 0:
        P.append(C.prim('cyl', pin_mi if pin_mi is not None else st, loc=(0.47*L+endpin/2,y,0.0), rot=(0,math.pi/2,0), scale=(0.008,0.008,endpin), verts=10))
        P.append(C.prim('cyl', eb, loc=(0.47*L,y,0.0), rot=(0,math.pi/2,0), scale=(0.02,0.02,0.04), verts=12))
    o = C.join(P, name); o.rotation_euler = (0, rot, 0); o.location = (cx, 0, cz)
    C._activate(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
def bow(C, stick, hair, frog, tip, y=0.0, x0=-0.31, x1=0.31, top=0.045, depth=0.05, pearl=None):
    """bow as a striker (inside the contact rectangle): stick (top flush with the contact face), hair ribbon below, frog + tip"""
    r = 0.018; P = [C.prim('cyl', stick, loc=((x0+x1)/2,y,top-r), rot=(0,math.pi/2,0), scale=(r,r,x1-x0-0.02), verts=16)]
    P.append(C.prim('cube', hair, loc=((x0+x1)/2+0.02,y,top-0.068), scale=(x1-x0-0.10,depth,0.008)))
    P.append(C.prim('cube', frog, loc=(x0+0.05,y,top-0.05), scale=(0.08,depth+0.02,0.07), bevel=0.008))      # frog
    if pearl is not None: P.append(C.prim('cyl', pearl, loc=(x0+0.05,y-depth/2-0.011,top-0.05), rot=(math.pi/2,0,0), scale=(0.012,0.012,0.004), verts=12))
    P.append(C.shape_profile('bow_tip', [(x1-0.05,top-0.072),(x1,top-0.072),(x1,top-0.004),(x1-0.02,top)], depth+0.01, y-(depth+0.01)/2, tip, bevel=0.003))
    return P
def back_bow(C, a, b, y, stick, hair, frog):
    """bow drawn behind the marble plane from (x,z) a (frog) to b (tip)"""
    P = [rod(C, (a[0],a[1],y), b, 0.008, stick)]
    dx, dz = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dz); nx, nz = dz/L, -dx/L
    P.append(rod(C, (a[0]+0.03*nx+0.05*dx/L, a[1]+0.03*nz+0.05*dz/L, y+0.004), (b[0]+0.02*nx, b[1]+0.02*nz), 0.006, hair, verts=8))
    P.append(bar(C, (a[0], a[1]), (a[0]+0.06*dx/L, a[1]+0.06*dz/L), 0.04, 0.02, frog, y, bevel=0.004))
    return P
'''

def fid_mats(prefix, body_c, c1, c2):
    return f'''
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,{body_c},rough=0.25,coat=0.85),{c1},{c2},scale=6.0)
'''
SHARED_STR = '''
    'ebony': C.mat('{p}_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'dark': C.mat('{p}_dark',(0.03,0.012,0.005),rough=0.6),
    'steel': C.mat('{p}_steel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'pale': C.mat('{p}_pale',(0.85,0.74,0.55),rough=0.4),
    'stick': C.add_wood(C.mat('{p}_stick',(0.2,0.07,0.02),rough=0.3,coat=0.6),(0.12,0.04,0.01),(0.3,0.11,0.03),scale=12.0),
    'hair': C.mat('{p}_hair',(0.92,0.9,0.84),rough=0.6), 'pearl': C.mat('{p}_pearl',(0.85,0.88,0.9),rough=0.1,coat=1.0)'''
STR_SLOTS = ['body','ebony','dark','steel','pale','stick','hair','pearl','pin']   # indices 0..7

# ------------------------------------------------------------------ 25 violin / 26 viola (strings striker + bow behind)
for folder, sec, num, L, bc, c1, c2, bowpts, chin, txt in (
    ('violin', 125, 25, 0.52, (0.62,0.15,0.02), (0.45,0.08,0.01), (0.75,0.2,0.03), ((-0.52,0.30),(0.50,-0.22)), True,
     'bright orange-red varnished violin face-on (f-holes, ebony fingerboard and chinrest, scroll) with its bow laid diagonally across it'),
    ('viola', 126, 26, 0.64, (0.12,0.045,0.015), (0.07,0.025,0.008), (0.18,0.07,0.025), ((0.55,0.30),(-0.50,-0.26)), True,
     'LARGER dark chestnut-brown viola face-on (f-holes, ebony fingerboard, chinrest, scroll) with its bow crossing the other way')):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=FIDPINS,
      description=f'Jewelbox {num} {folder.title()}: four steel strings (the striker) over a {txt} - bowed, unlike pizzicato (23).',
      slots=STR_SLOTS, flash_slot='body', flash_slots=['body','steel'], flash_color=[1.0,0.75,0.4]),
f'''"""{folder} (jewelbox {num}): steel strings striker + {folder} face-on with a bow behind the marble plane."""
'''+HDR+H+FID+f'''
def build(C, variant=None):
    P = [fiddle(C, {L}, 0.20, 0, 1, 2, 3, 4, cx=0.02, bstrings=False, chin={chin})]
    P += back_bow(C, {bowpts[0]}, {bowpts[1]}, 0.172, 5, 6, 1)
    P.append(C.prim('cube', 4, loc=(0.12,0.04,0.015), scale=(0.025,0.30,0.035), bevel=0.004))      # bridge (in the contact rectangle)
    P.append(C.prim('cube', 1, loc=(-0.298,0.04,0.02), scale=(0.012,0.30,0.03)))                   # nut
    P += strings(C, (-0.075,-0.025,0.025,0.075), 3, 0.009, 0.0008)
    return P
''',
f'''"""{folder} materials"""
def shared(C):
    return {{{SHARED_STR.format(p=folder[:3])}}}
'''+fid_mats(folder, bc, c1, c2))

# ------------------------------------------------------------------ 27 cello / 28 contrabass (bow striker, instrument upright)
for folder, sec, num, L, cz, endpin, slope, bc, c1, c2, txt in (
    ('cello', 127, 27, 0.58, 0.04, 0.16, False, (0.28,0.05,0.015), (0.18,0.03,0.01), (0.36,0.07,0.02),
     'deep oxblood-red cello standing upright behind it (neck and scroll rising above, f-holes, bridge, strings, chrome end-pin to the floor)'),
    ('contrabass', 128, 28, 0.74, 0.06, 0.12, True, (0.03,0.013,0.006), (0.015,0.006,0.003), (0.06,0.025,0.01),
     'BIG near-black double bass with sloping shoulders standing upright behind it (tall neck and scroll, f-holes, bridge, strings, end-pin) - bowed, unlike the plucked, lying acoustic bass (21)')):
    write(folder, dict(name=folder, section=sec, tracks_regex=NEVER, pins=KEYPINS,
      description=f'Jewelbox {num} {folder.title()}: the BOW is the striker (pernambuco stick flush with the contact face, white hair, ebony frog with pearl eye, ivory tip), crossing the strings of a {txt}.',
      slots=STR_SLOTS, flash_slot='body', flash_slots=['body','hair'], flash_color=[1.0,0.7,0.4]),
f'''"""{folder} (jewelbox {num}): bow striker across an upright {folder}."""
'''+HDR+H+FID+f'''
def build(C, variant=None):
    L = {L}
    P = [fiddle(C, L, 0.22, 0, 1, 2, 3, 4, cx=0.0, cz=0.10*L - 0.07 + {cz}, rot=math.pi/2, endpin={endpin}, slope={slope})]
    P += bow(C, 5, 6, 1, 7, pearl=7)
    return P
''',
f'''"""{folder} materials (bow: stick / hair / frog = ebony / tip = pearl)"""
def shared(C):
    return {{{SHARED_STR.format(p=folder[:3])}}}
'''+fid_mats(folder, bc, c1, c2))

# ------------------------------------------------------------------ 29 string ensemble
write('string_ensemble', dict(name='string_ensemble', section=129, tracks_regex=NEVER, pins=KEYPINS,
  description='Jewelbox 29 String Ensemble: the BOW is the striker, in front of a whole section - an upright cello in the middle flanked by a '
              'violin (orange) and a viola (chestnut) angled outward on either side, a second bow fanned behind, all standing on a red velvet stage riser.',
  slots=['body','ebony','dark','steel','pale','stick','hair','pearl','v_orange','v_brown','velvet','gold','pin'], flash_slot='body', flash_slots=['body','hair'], flash_color=[1.0,0.75,0.45]),
'''"""string_ensemble (jewelbox 29): bow striker + cello, violin and viola together on a red riser."""
'''+HDR+H+FID+'''
def build(C, variant=None):
    P = [fiddle(C, 0.46, 0.235, 0, 1, 2, 3, 4, cx=0.0, cz=-0.06, rot=math.pi/2, endpin=0.10, name='se_c')]
    P.append(fiddle(C, 0.36, 0.20, 8, 1, 2, 3, 4, cx=-0.42, cz=-0.12, rot=math.pi/2+0.55, chin=True, name='se_v'))
    P.append(fiddle(C, 0.42, 0.205, 9, 1, 2, 3, 4, cx=0.44, cz=-0.14, rot=math.pi/2-0.55, chin=True, name='se_a'))
    P += back_bow(C, (-0.30,-0.40), (0.42,0.22), 0.172, 5, 6, 1)
    P.append(C.prim('cube', 10, loc=(0,0.24,-0.47), scale=(1.30,0.10,0.07), bevel=0.02))           # red velvet riser
    P.append(C.prim('cube', 11, loc=(0,0.188,-0.44), scale=(1.30,0.006,0.012)))
    P += bow(C, 5, 6, 1, 7, pearl=7)
    return P
''',
'''"""string_ensemble materials: body = cello; v_orange / v_brown = violin / viola"""
def shared(C):
    d = {'''+SHARED_STR.format(p='se')+'''}
    d['v_orange'] = C.add_wood(C.mat('se_vo',(0.62,0.15,0.02),rough=0.25,coat=0.85),(0.45,0.08,0.01),(0.75,0.2,0.03),scale=6.0)
    d['v_brown'] = C.add_wood(C.mat('se_vb',(0.12,0.045,0.015),rough=0.25,coat=0.85),(0.07,0.025,0.008),(0.18,0.07,0.025),scale=6.0)
    d['velvet'] = C.mat('se_velvet',(0.4,0.02,0.04),rough=0.95); d['gold'] = C.mat('se_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)
    return d
'''+fid_mats('string_ensemble', (0.28,0.05,0.015), (0.18,0.03,0.01), (0.36,0.07,0.02)))

# ------------------------------------------------------------------ 30 choir aahs
write('choir', dict(name='choir', section=130, tracks_regex=NEVER, pins=KEYPINS,
  description='Jewelbox 30 Choir Aahs: the striker is the front board of an oak choir riser with a gold trim strip; behind it stand two rows of '
              'robed singers (burgundy robes, white stoles, black folders, round heads with open "aah" mouths), a gap in the middle of the front '
              'row where the marble lands, back row raised on a second step.',
  slots=['body','robe','stole','skin','hair','folder','gold','pin'], flash_slot='body', flash_slots=['body','stole'], flash_color=[1.0,0.85,0.6]),
'''"""choir (jewelbox 30): oak riser striker + two rows of robed singers."""
'''+HDR+H+'''
def singer(C, cx, z0, y, h=0.26, s=1.0, hair_mi=4):
    w0, w1 = 0.065*s, 0.095*s; P = []
    P.append(C.shape_profile('robe', [(cx-w1,z0),(cx+w1,z0),(cx+w0,z0+h),(cx+w0*0.6,z0+h+0.02*s),(cx-w0*0.6,z0+h+0.02*s),(cx-w0,z0+h)], 0.05, y, 1, bevel=0.012))
    for sg in (-1, 1): P.append(bar(C, (cx+sg*0.045*s, z0+h+0.01), (cx+sg*0.012*s, z0+h*0.45), 0.022*s, 0.006, 2, y-0.004))
    P.append(C.prim('cube', 5, loc=(cx, y-0.012, z0+h*0.55), scale=(0.09*s,0.012,0.07*s), bevel=0.004))      # folder
    hz = z0+h+0.065*s
    P.append(C.prim('sphere', 3, loc=(cx,y+0.02,hz), scale=(0.048*s,0.03,0.052*s), verts=24))              # head
    P.append(C.prim('sphere', hair_mi, loc=(cx,y+0.03,hz+0.014*s), scale=(0.052*s,0.03,0.048*s), verts=24))  # hair (behind/above)
    P.append(C.prim('cyl', 4, loc=(cx,y-0.012,hz-0.018*s), rot=(math.pi/2,0,0), scale=(0.012*s,0.016*s,0.006), verts=12))   # open "aah" mouth
    for sg in (-1, 1): P.append(C.prim('sphere', 4, loc=(cx+sg*0.017*s,y-0.01,hz+0.008*s), scale=(0.006*s,0.004,0.006*s), verts=8))
    return P
def build(C, variant=None):
    P = [C.prim('cube', 0, scale=(0.62,0.30,0.09), bevel=0.012)]
    P.append(C.prim('cube', 0, loc=(0,0.23,-0.03), scale=(1.20,0.14,0.07), bevel=0.01))            # riser step behind (front row stands here)
    P.append(C.prim('cube', 0, loc=(0,0.27,0.04), scale=(1.10,0.06,0.09), bevel=0.01))             # second step (back row)
    P.append(C.prim('cube', 6, loc=(0,0.159,-0.055), scale=(1.20,0.008,0.014)))
    for cx in (-0.34, -0.12, 0.12, 0.34): P += singer(C, cx, 0.09, 0.262, s=0.92)
    for cx in (-0.50, -0.27, 0.27, 0.50): P += singer(C, cx, 0.0, 0.205)
    return P
''',
'''"""choir materials"""
def shared(C):
    return {'robe': C.mat('ch_robe',(0.32,0.02,0.05),rough=0.7,coat=0.1), 'stole': C.mat('ch_stole',(0.92,0.9,0.84),rough=0.5),
            'skin': C.mat('ch_skin',(0.8,0.55,0.4),rough=0.5), 'hair': C.mat('ch_hair',(0.05,0.03,0.02),rough=0.6),
            'folder': C.mat('ch_folder',(0.02,0.02,0.025),rough=0.4), 'gold': C.mat('ch_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.36,0.2,0.09),rough=0.35,coat=0.6),(0.24,0.12,0.05),(0.5,0.3,0.14),scale=6.0)
''')

# ------------------------------------------------------------------ 31 voice oohs
write('voice_oohs', dict(name='voice_oohs', section=131, tracks_regex=NEVER,
  pins=[{"x":-0.12,"z":0.0,"y_start":0.2,"radius":0.022},{"x":0.12,"z":0.0,"y_start":0.2,"radius":0.022}],
  description='Jewelbox 31 Voice Oohs: a vintage 1950s studio microphone - the chrome boom arm (with a counterweight ball) is the striker; the '
              'art-deco chrome capsule with horizontal grille slots sits on a gold yoke at its right end, the boom clamps onto a chrome stand with a '
              'black cast base and a coiled cable, and a red ON-AIR lamp glows above.',
  slots=['body','grille','gold','black','red','pin'], flash_slot='body', flash_slots=['body','grille'], flash_color=[1.0,0.9,0.7]),
'''"""voice_oohs (jewelbox 31): chrome boom striker + vintage art-deco microphone on a stand."""
'''+HDR+H+'''
def build(C, variant=None):
    P = [C.prim('cyl', 0, loc=(0.02,0.0,0.007), rot=(0,math.pi/2,0), scale=(0.038,0.038,0.56), verts=32)]   # boom arm (top z=0.045)
    P.append(C.prim('sphere', 0, loc=(-0.262,0.0,0.0), scale=(0.045,0.045,0.045), verts=24))         # counterweight
    P.append(C.prim('cube', 3, loc=(-0.08,0.0,0.0), scale=(0.07,0.10,0.07), bevel=0.01))           # boom clamp
    # microphone capsule on a yoke at the right end
    mx, mz = 0.47, 0.16
    P.append(bar(C, (0.30,0.007), (mx,mz-0.19), 0.03, 0.03, 0, 0.2, bevel=0.008))
    P.append(C.prim('torus', 2, loc=(mx,0.21,mz-0.02), rot=(math.pi/2,0,0), scale=(0.15,0.014), verts=40))
    P.append(C.prim('sphere', 0, loc=(mx,0.225,mz), scale=(0.13,0.055,0.19), verts=40))
    for k in range(-5, 6):
        dz = 0.028*k; w = 2*0.13*math.sqrt(max(0.0, 1-(dz/0.19)**2))*0.82
        if w > 0.03: P.append(C.prim('cube', 1, loc=(mx,0.168+0.04*(abs(dz)/0.19)**2,mz+dz), scale=(w,0.006,0.011), bevel=0.002))
    P.append(C.prim('cube', 2, loc=(mx,0.163,mz), scale=(0.02,0.008,0.37), bevel=0.004))          # gold spine
    # stand: chrome pole from the clamp down to a black cast base
    P.append(C.prim('cyl', 0, loc=(-0.08,0.21,-0.32), scale=(0.018,0.018,0.64), verts=16))
    P.append(C.prim('cyl', 3, loc=(-0.08,0.22,-0.64), scale=(0.18,0.055,0.04), verts=40))
    P.append(C.prim('cyl', 0, loc=(-0.08,0.21,-0.10), scale=(0.03,0.03,0.05), verts=16))
    for i in range(10): P.append(C.prim('torus', 3, loc=(0.0,0.19,-0.08-0.05*i), rot=(math.pi/2,0,0), scale=(0.014,0.005), verts=12))   # cable
    P.append(C.prim('cube', 3, loc=(-0.48,0.25,0.22), scale=(0.24,0.05,0.09), bevel=0.012))        # ON-AIR lamp
    P.append(C.prim('cube', 4, loc=(-0.48,0.222,0.22), scale=(0.20,0.006,0.06), bevel=0.006))
    return P
''',
'''"""voice_oohs materials (red = ON-AIR lamp, emissive)"""
def shared(C):
    r = C.mat('vo_red',(0.8,0.05,0.04),rough=0.3); b = r.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (1.0,0.12,0.06,1); b.inputs['Emission Strength'].default_value = 2.5
    return {'grille': C.mat('vo_grille',(0.03,0.03,0.035),rough=0.5,metal=0.5), 'gold': C.mat('vo_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'black': C.mat('vo_black',(0.02,0.02,0.022),rough=0.35,coat=0.5), 'red': r}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9,0.9,0.92),rough=0.07,metal=1.0)
''')

# ------------------------------------------------------------------ 32 orchestra hit
write('orchestra_hit', dict(name='orchestra_hit', section=132, tracks_regex=NEVER, pins=KEYPINS,
  description='Jewelbox 32 Orchestra Hit: a timpani whose calfskin head + chrome counter-hoop is the striker, polished copper kettle below with '
              'chrome tuning rods, base ring, legs and pedal; a gold crash cymbal on a stand beside it with a starburst of gold impact rays, '
              'and two felt-headed timpani mallets crossed on the other side.',
  slots=['body','chrome','copper','gold','black','felt','pin'], flash_slot='body', flash_slots=['body','gold'], flash_color=[1.0,0.85,0.5]),
'''"""orchestra_hit (jewelbox 32): timpani head striker + copper kettle + crash cymbal with impact rays."""
'''+HDR+H+'''
def build(C, variant=None):
    P = [C.prim('cube', 0, loc=(0,0,0.02), scale=(0.60,0.30,0.05), bevel=0.01)]                     # calfskin head (top z=0.045)
    P.append(C.prim('cube', 1, loc=(0,0,-0.02), scale=(0.62,0.30,0.05), bevel=0.008))               # chrome counter-hoop
    k = C.prim('sphere', 2, loc=(0,0.215,-0.07), scale=(0.31,0.05,0.30), verts=64)                  # copper kettle (lower half)
    C.cut(k, C.prim('cube', 2, loc=(0,0.215,0.2), scale=(0.8,0.3,0.5)))
    P.append(k)
    P.append(C.prim('cube', 1, loc=(0,0.215,-0.075), scale=(0.66,0.07,0.03), bevel=0.008))          # rim band
    for x in (-0.28,-0.18,-0.06,0.06,0.18,0.28):
        P.append(C.prim('cyl', 1, loc=(x,0.163,-0.17), scale=(0.005,0.005,0.18), verts=8))
        P.append(C.prim('cube', 1, loc=(x,0.165,-0.085), scale=(0.02,0.012,0.025), bevel=0.003))
    P.append(C.prim('torus', 1, loc=(0,0.22,-0.42), rot=(math.pi/2,0,0), scale=(0.22,0.012), verts=48))
    for x in (-0.20, 0.0, 0.20):
        P.append(rod(C, (x*0.6,-0.36,0.22), (x,-0.54), 0.012, 1))
        P.append(C.prim('sphere', 4, loc=(x,0.22,-0.555), scale=(0.022,0.022,0.022), verts=12))
    P.append(C.prim('cube', 4, loc=(0.08,0.19,-0.52), scale=(0.12,0.04,0.02), bevel=0.005))         # tuning pedal
    # crash cymbal on a stand (right) with impact rays
    cx, cz = 0.58, 0.10
    P.append(C.prim('cyl', 1, loc=(cx,0.26,(cz-0.56)/2), scale=(0.01,0.01,cz+0.56), verts=10))
    P.append(C.prim('cyl', 3, loc=(cx,0.22,cz), rot=(1.3,0,0.25), scale=(0.17,0.17,0.006), verts=48))
    P.append(C.prim('sphere', 3, loc=(cx,0.205,cz), scale=(0.04,0.015,0.035), verts=16))
    for i in range(9):
        a = i*2*math.pi/9 + 0.2; r0, r1 = 0.21, 0.27 + 0.03*(i % 2)
        P.append(bar(C, (cx+r0*math.cos(a), cz+r0*math.sin(a)), (cx+r1*math.cos(a), cz+r1*math.sin(a)), 0.012, 0.008, 3, 0.2))
    # crossed timpani mallets (left)
    for a_, b_ in (((-0.62,-0.40), (-0.38,0.02)), ((-0.38,-0.40), (-0.62,0.02))):
        P.append(rod(C, (a_[0],a_[1],0.19), b_, 0.007, 4, verts=8))
        P.append(C.prim('sphere', 5, loc=(b_[0],0.19,b_[1]), scale=(0.03,0.03,0.03), verts=16))
    return P
''',
'''"""orchestra_hit materials"""
def shared(C):
    return {'chrome': C.mat('oh_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0), 'copper': C.mat('oh_copper',(0.85,0.42,0.22),rough=0.18,metal=1.0),
            'gold': C.mat('oh_gold',(0.95,0.72,0.3),rough=0.18,metal=1.0), 'black': C.mat('oh_black',(0.02,0.02,0.02),rough=0.4),
            'felt': C.mat('oh_felt',(0.88,0.84,0.76),rough=0.95)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9,0.85,0.72),rough=0.55)
''')
print('wrote jewelbox F3 assets')
