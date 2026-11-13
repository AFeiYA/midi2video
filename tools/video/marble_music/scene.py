"""Blender scene builder/renderer for marble music.
blender -b -P scene.py -- --plan plan.json --out frames/ [--start 0 --end 450 --samples 24 --res 1080x1920 --look v3 --device AUTO]
Looks: v1 = approved 15s sample, v2 = studio reflectors + edge flash, v3 = v2 + instrument asset library, v4 = v3 + readability pass, v5 = v4 + recognisable silhouettes (default), v6 = v5 + section backdrop colour, bloom, snow, hit sparks.
Device: --device AUTO|CPU|GPU|METAL|CUDA|OPTIX|HIP, or env MARBLE_DEVICE (GPU/AUTO tries Metal, then OptiX/CUDA/HIP, then CPU).
"""
import bpy, json, sys, math, argparse, os
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ap=argparse.ArgumentParser(); ap.add_argument('--plan',default='plan.json'); ap.add_argument('--out',default='frames/')
ap.add_argument('--start',type=int,default=0); ap.add_argument('--end',type=int,default=-1); ap.add_argument('--samples',type=int,default=24)
ap.add_argument('--res',default='1080x1920'); ap.add_argument('--frames',default='',help='comma list of specific frames'); ap.add_argument('--save-blend',default='')
ap.add_argument('--look',default='v5',help='v1 = approved 15s sample look, v2 = studio reflectors + edge flash + piano black/ivory + closer camera, v3 = v2 + instrument asset library strikers, v4 = v3 + readability pass (asset overrides in <instrument>/v4/, world-vertical resonators, string flash), v5 = v4 + recognisable instrument silhouettes (<instrument>/v5/; pair with titles.py overlays; default), v6 = v5 + per-section backdrop colour, bloom, background snow, hit sparks')
ap.add_argument('--device',default=os.environ.get('MARBLE_DEVICE','AUTO'),help='AUTO|CPU|GPU|METAL|CUDA|OPTIX|HIP (GPU is an alias for AUTO)')
a=ap.parse_args(argv)
P=json.load(open(a.plan)); fps=P['fps']; R=P['R']; KW,KD,KH=P['KW'],P['KD'],P['KH']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
W,Hh=map(int,a.res.split('x'))
sc.render.resolution_x=W; sc.render.resolution_y=Hh; sc.render.fps=fps
sc.frame_start=0; sc.frame_end=len(P['marble'])-1
sc.render.engine='CYCLES'; cy=sc.cycles; cy.device='CPU'
_dev=a.device.upper()
if _dev=='GPU': _dev='AUTO'
if _dev!='CPU':
    try:
        pr=bpy.context.preferences.addons['cycles'].preferences
        for t in ([_dev] if _dev!='AUTO' else ['METAL','OPTIX','CUDA','HIP']):
            try: pr.compute_device_type=t
            except Exception: continue
            pr.get_devices(); devs=[d for d in pr.devices if d.type==t]
            if devs:
                for d in pr.devices: d.use=(d.type==t)
                cy.device='GPU'; print('Cycles device',t); break
        else:
            print('GPU setup: no matching device, CPU fallback')
    except Exception as e:
        print('GPU setup failed, CPU fallback',e)
cy.samples=a.samples; cy.use_adaptive_sampling=True; cy.adaptive_threshold=0.03
cy.use_denoising=True; cy.denoiser='OPENIMAGEDENOISE'; cy.max_bounces=8; cy.diffuse_bounces=2; cy.glossy_bounces=3; cy.transmission_bounces=8; cy.caustics_reflective=False; cy.caustics_refractive=False
cy.blur_glossy=1.0
sc.render.use_motion_blur=True; sc.render.motion_blur_shutter=0.4
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_depth='8'
sc.render.threads_mode='AUTO'
# ---------- world
wd=bpy.data.worlds.new('W'); sc.world=wd; wd.use_nodes=True
bg=wd.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.55,0.56,0.58,1); bg.inputs[1].default_value=0.08
def mat(name,base,rough=0.5,metal=0.0,trans=0.0,ior=1.45,coat=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*base,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    b.inputs['Transmission Weight'].default_value=trans; b.inputs['IOR'].default_value=ior; b.inputs['Coat Weight'].default_value=coat
    return m,b
def add_wood(m,b,c1,c2,scale=6.0):
    nt=m.node_tree; tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1,scale*0.15,scale)
    wv=nt.nodes.new('ShaderNodeTexWave'); wv.wave_type='RINGS'; wv.inputs['Scale'].default_value=2.5; wv.inputs['Distortion'].default_value=6; wv.inputs['Detail'].default_value=3
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=40
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*c1,1); ramp.color_ramp.elements[1].color=(*c2,1)
    mix=nt.nodes.new('ShaderNodeMath'); mix.operation='ADD'
    nt.links.new(tc.outputs['Object'],mp.inputs[0]); nt.links.new(mp.outputs[0],wv.inputs[0]); nt.links.new(mp.outputs[0],nz.inputs[0])
    nt.links.new(wv.outputs['Fac'],mix.inputs[0]); nt.links.new(nz.outputs['Fac'],mix.inputs[1])
    mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=0.6
    nt.links.new(mix.outputs[0],mul.inputs[0]); nt.links.new(mul.outputs[0],ramp.inputs[0]); nt.links.new(ramp.outputs[0],b.inputs['Base Color'])
# instrument looks: one material family per melody section (castanets + piano identical to the approved 15s sample)
def look_for(track,drum):
    t=track.lower()
    for key,kind in [('castanet','rosewood'),('piano','ivory'),('vibra','alu'),('tubular','brass'),('marimba','marimba'),
                     ('kalimba','kalimba'),('flute','silver'),('xylo','rainbow'),('ocarina','ceramic'),('glock','steel'),
                     ('steel drum','chrome'),('guitar','spruce')]:
        if key in t: return kind
    return 'rosewood' if drum else 'ivory'
FLASH={'rosewood':(1.0,0.55,0.25),'ivory':(1.0,0.85,0.55),'alu':(0.45,0.7,1.0),'brass':(1.0,0.75,0.35),'marimba':(1.0,0.6,0.3),
       'kalimba':(0.75,0.9,1.0),'silver':(0.85,0.9,1.0),'rainbow':(1.0,0.95,0.85),'ceramic':(1.0,0.65,0.4),'steel':(0.55,0.8,1.0),
       'chrome':(1.0,0.85,0.4),'spruce':(1.0,0.78,0.45),'metal':(0.45,0.7,1.0),'wood':(1.0,0.6,0.3)}
import colorsys
LOOKN=int(a.look.lstrip('v'))
V2=(LOOKN>=2)
V3=(LOOKN>=3)
V4=(LOOKN>=4)   # v4 behaviour (kept material slots, override assets, hanging parts) also applies to v5+
V6=(LOOKN>=6)   # Phase 3 effects; v5 geometry/assets unchanged
PIANO_IDX={}
for _k in P['keys']:
    if 'piano' in _k['track'].lower(): PIANO_IDX[_k['i']]=len(PIANO_IDX)
def key_material(i,kind,note=60):
    if kind=='rosewood':   # castanets: dark lacquered rosewood
        m,b=mat(f'key{i}',(0.25,0.08,0.04),rough=0.35,coat=0.4); add_wood(m,b,(0.16,0.05,0.02),(0.42,0.16,0.07))
    elif kind=='marimba':  # marimba: warm honduras-rosewood bars, satin finish
        m,b=mat(f'key{i}',(0.45,0.16,0.07),rough=0.4,coat=0.3); add_wood(m,b,(0.30,0.09,0.04),(0.62,0.26,0.11))
    elif kind=='spruce':   # guitar: lacquered spruce top
        m,b=mat(f'key{i}',(0.8,0.6,0.35),rough=0.3,coat=0.8); add_wood(m,b,(0.62,0.42,0.20),(0.88,0.70,0.44),scale=9.0)
    elif kind=='alu':      # vibraphone: brushed aluminium
        m,b=mat(f'key{i}',(0.88,0.89,0.91),rough=0.32,metal=1.0); b.inputs['Anisotropic'].default_value=0.7
    elif kind=='brass':    # tubular bells: polished brass
        m,b=mat(f'key{i}',(0.88,0.58,0.18),rough=0.18,metal=1.0)
    elif kind=='kalimba':  # kalimba: spring-steel tines, slightly blued
        m,b=mat(f'key{i}',(0.70,0.73,0.78),rough=0.14,metal=1.0)
    elif kind=='silver':   # flute: bright sterling silver
        m,b=mat(f'key{i}',(0.97,0.96,0.94),rough=0.07,metal=1.0)
    elif kind=='steel':    # glockenspiel: polished steel
        m,b=mat(f'key{i}',(0.82,0.84,0.87),rough=0.05,metal=1.0)
    elif kind=='chrome':   # steel drums: mirror chrome
        m,b=mat(f'key{i}',(0.96,0.96,0.97),rough=0.02,metal=1.0)
    elif kind=='ceramic':  # ocarina: glazed terracotta ceramic
        m,b=mat(f'key{i}',(0.60,0.27,0.15),rough=0.55,coat=1.0); b.inputs['Coat Roughness'].default_value=0.04
    elif kind=='rainbow':  # xylophone: painted gloss bars, 7-colour rainbow
        h=(i%7)/7.0; rgb=colorsys.hsv_to_rgb(h,0.72,0.85)   # rainbow cycling bar to bar
        m,b=mat(f'key{i}',rgb,rough=0.3,coat=0.6)
    elif kind=='wood':
        m,b=mat(f'key{i}',(0.5,0.25,0.1),rough=0.4,coat=0.3); add_wood(m,b,(0.35,0.15,0.06),(0.65,0.35,0.15))
    elif kind=='metal':
        m,b=mat(f'key{i}',(0.8,0.82,0.85),rough=0.22,metal=1.0)
    elif kind=='ivory' and V2 and PIANO_IDX.get(i,0)%2==1:   # piano v2: alternate glossy ebony keys
        m,b=mat(f'key{i}',(0.015,0.015,0.017),rough=0.12,coat=1.0); b.inputs['Coat Roughness'].default_value=0.03
    else:                  # piano: glossy ivory (as in approved sample)
        m,b=mat(f'key{i}',(0.92,0.88,0.78),rough=0.18,coat=0.6)
    b.inputs['Emission Color'].default_value=(*FLASH[kind],1); b.inputs['Emission Strength'].default_value=0.0
    return m,b
# ---------- wall
zs=[k['z'] for k in P['keys']]; zmin=min(zs)-12; zmax=max(zs)+8
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,KD/2+0.12,(zmin+zmax)/2),rotation=(math.pi/2,0,0))
wall=bpy.context.object; wall.scale=(14,(zmax-zmin),1)
wm,wb=mat('wall',(0.36,0.36,0.37),rough=0.8)
nt=wm.node_tree; nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=60; bm=nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value=0.05
tc=nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'],nz.inputs[0]); nt.links.new(nz.outputs['Fac'],bm.inputs['Height']); nt.links.new(bm.outputs['Normal'],wb.inputs['Normal'])
wall.data.materials.append(wm)
# ---------- keys + pins
pinm,_=mat('pin',(0.7,0.7,0.72),rough=0.25,metal=1.0)
def frame_of(t): return t*fps
if V3:
    import os as _os
    sys.path.insert(0,_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'assets','instruments'))
    import _common as AC, library as ALIB
    _AM=ALIB.metas(a.look if V3 else 'v3'); _ASG=ALIB.assign(P['keys'],_AM); _MODS={}; _MESH={}; _SH={}; _HANG={}; _ALN={}
    for (an,av,_j) in sorted(set(_ASG)):
        if an not in _MODS:
            _MODS[an]=AC.load_asset(_AM[an]['_dir']); _SH[an]=_MODS[an][2].shared(AC)
            for hi,h in enumerate(_AM[an].get('hanging',[])):   # world-vertical parts (e.g. resonator tubes): top at origin, hanging along -Z
                tb=AC.prim('cyl',0,loc=(0,0,-h['length']/2),scale=(h['radius'],h['radius'],h['length']),verts=40)
                AC.cut(tb,AC.prim('cyl',1,loc=(0,0,0),scale=(h['inner'],h['inner'],0.12),verts=40))
                hm=[_SH[an][h['role']],_SH[an].get('dark',pinm)]
                if h.get('cap_role'):                              # v5: crown cap at the top of a chime tube
                    cap=AC.prim('cyl',2,loc=(0,0,-0.018),scale=(h['radius']*1.3,h['radius']*1.3,0.036),verts=40)
                    tb=AC.join([tb,cap],f'hang_{an}_{hi}'); hm.append(_SH[an][h['cap_role']])
                AC.set_slots(tb.data,hm)
                while len(tb.data.materials)>len(hm): tb.data.materials.pop(index=len(tb.data.materials)-1)
                _HANG[(an,hi)]=tb.data; bpy.data.objects.remove(tb,do_unlink=True)
        meta,bmod,mmod=_MODS[an]; t=AC.make_asset(meta,bmod,av,f'tmpl_{an}_{av}',keep_slots=V4); me=t.data   # v3 kept the join-collapsed slots
        AC.set_slots(me,[pinm if role=='pin' else (mmod.body(AC,f'{an}_{av}_placeholder',0,60,None) if role=='body' else _SH[an][role]) for role in meta['slots']])
        bpy.data.objects.remove(t,do_unlink=True); _MESH[(an,av)]=me
        for ap_ in meta.get('aligned',[]):                    # v5: camera-aligned behind-plane parts (e.g. flute head joint), one mesh per asset
            if (an,ap_['name']) in _ALN: continue
            ta=AC.join(bmod.build_aligned(AC,ap_['name']),f"aln_{an}_{ap_['name']}"); n_=len(meta['slots'])
            for p_ in ta.data.polygons: p_.material_index=min(p_.material_index,n_-1)
            while len(ta.data.materials)>n_: ta.data.materials.pop(index=len(ta.data.materials)-1)
            AC.set_slots(ta.data,[pinm if role=='pin' else (mmod.body(AC,f'{an}_aln_placeholder',0,60,None) if role=='body' else _SH[an][role]) for role in meta['slots']])
            _ALN[(an,ap_['name'])]=ta.data; bpy.data.objects.remove(ta,do_unlink=True)
for _ki,k in enumerate(P['keys']):
    if V3:
        an,av,j=_ASG[_ki]; meta,bmod,mmod=_MODS[an]
        o=bpy.data.objects.new(f"key{k['i']}",_MESH[(an,av)]); sc.collection.objects.link(o)
        o.location=(k['x'],0,k['z']); o.rotation_euler=(0,k['ang'],0)
        bi=meta['slots'].index('body'); m=mmod.body(AC,f"key{k['i']}",j,k['note'],None if av=='default' else av)
        o.material_slots[bi].link='OBJECT'; o.material_slots[bi].material=m
        flashes=[AC.add_flash(m,tuple(meta['flash_color']))]
        for role in meta.get('flash_slots',['body']):           # v4: extra per-key flashing slots (e.g. guitar strings)
            if role=='body': continue
            si=meta['slots'].index(role); m2=_SH[an][role].copy(); m2.name=f"key{k['i']}_{role}"
            o.material_slots[si].link='OBJECT'; o.material_slots[si].material=m2; flashes.append(AC.add_flash(m2,tuple(meta['flash_color'])))
        fh=frame_of(k['t']); x0,z0,nx,nz=k['x'],k['z'],k['nx'],k['nz']
        for f,dd in [(fh-1,0),(fh,0),(fh+1.0,-0.05),(fh+3,-0.012),(fh+7,0)]:
            o.location.x=x0+nx*dd; o.location.z=z0+nz*dd; o.keyframe_insert('location',index=0,frame=f); o.keyframe_insert('location',index=2,frame=f)
        for fi,(rim,em) in enumerate(flashes):
            pk=(2.5 if fi==0 else 6.0)                       # strings: thin, so a stronger edge flash to read
            for f,v in [(fh-0.5,0),(fh,pk),(fh+4,pk*0.32),(fh+12,0)]:      # v3: weaker edge flash (less pale wash on impact)
                rim.default_value=v; rim.keyframe_insert('default_value',frame=f)
            for f,v in [(fh-0.5,0),(fh,0.1 if fi==0 else 1.5),(fh+4,0.03 if fi==0 else 0.4),(fh+10,0)]:
                em.default_value=v; em.keyframe_insert('default_value',frame=f)
        for hi,h in enumerate(meta.get('hanging',[])):
            ho=bpy.data.objects.new(f"key{k['i']}_hang{hi}",_HANG[(an,hi)]); sc.collection.objects.link(ho)
            ho.location=ALIB.hanging_world(k,h)                 # stays world-vertical regardless of the bar tilt
        for ap_ in meta.get('aligned',[]):                    # v5: re-aim the part along the camera ray every 2 frames while the key can be on screen
            ao=bpy.data.objects.new(f"key{k['i']}_{ap_['name']}",_ALN[(an,ap_['name'])]); sc.collection.objects.link(ao); ao.parent=o
            ao.material_slots[bi].link='OBJECT'; ao.material_slots[bi].material=m
            fh_=int(round(fh)); fr_=[f for f in range(max(0,fh_-150),min(len(P['camera'])-1,fh_+150)+1,2) if abs(P['camera'][f][1]-k['z'])<4.0] or [fh_]
            prev=None
            for f in fr_:
                lc,ph,scl=ALIB.aligned_local(k,P['camera'][f],ap_)
                if prev is not None: ph=prev+((ph-prev+math.pi)%(2*math.pi)-math.pi)   # unwrap: atan2 jumps +-pi -> a full spin + huge motion blur
                prev=ph
                ao.location=lc; ao.rotation_euler=(0,ph,0); ao.scale=scl
                ao.keyframe_insert('location',frame=f); ao.keyframe_insert('rotation_euler',index=1,frame=f); ao.keyframe_insert('scale',frame=f)
        continue
    kind=look_for(k['track'],k['drum'])
    ZZ=('ang' in k)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(k['x'],0,k['z']),rotation=((0,k['ang'],0) if ZZ else (0,0,0)))
    o=bpy.context.object; o.name=f"key{k['i']}"; o.scale=(KW,KD,KH)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bv=o.modifiers.new('bev','BEVEL'); bv.width=0.018; bv.segments=3
    bpy.ops.object.shade_smooth()
    m,b=key_material(k['i'],kind,k['note']); o.data.materials.append(m)
    if kind=='ivory':  # thin dark accent strip like a piano key edge
        pass
    # pins (two), parented to key so they dip with it
    for dx in (-KW*0.3,KW*0.3):
        if ZZ: px,pz=k['x']+dx*k['nz'],k['z']-dx*k['nx']
        else: px,pz=k['x']+dx,k['z']
        bpy.ops.mesh.primitive_cylinder_add(radius=0.022,depth=0.16,location=(px,KD/2+0.06,pz),rotation=(math.pi/2,0,0))
        p=bpy.context.object; p.data.materials.append(pinm); p.parent=o; p.matrix_parent_inverse=o.matrix_world.inverted()
    # hit animation: dip + emission flash
    fh=frame_of(k['t']); z0=k['z']
    x0=k['x']; nx,nz=(k['nx'],k['nz']) if ZZ else (0.0,1.0)
    for f,dd in [(fh-1,0),(fh,0),(fh+1.0,-0.05),(fh+3,-0.012),(fh+7,0)]:
        o.location.x=x0+nx*dd; o.location.z=z0+nz*dd; o.keyframe_insert('location',index=0,frame=f); o.keyframe_insert('location',index=2,frame=f)
    em=b.inputs['Emission Strength']
    if not V2:
        for f,v in [(fh-0.5,0),(fh,6.0),(fh+4,1.5),(fh+12,0)]:
            em.default_value=v; em.keyframe_insert('default_value',frame=f)
    else:
        nt=m.node_tree; out=nt.nodes['Material Output']
        lw=nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.35
        pw=nt.nodes.new('ShaderNodeMath'); pw.operation='POWER'; pw.inputs[1].default_value=2.0
        es=nt.nodes.new('ShaderNodeEmission'); es.inputs['Color'].default_value=(*FLASH[kind],1)
        ml=nt.nodes.new('ShaderNodeMath'); ml.operation='MULTIPLY'
        ad=nt.nodes.new('ShaderNodeAddShader')
        nt.links.new(lw.outputs['Facing'],pw.inputs[0]); nt.links.new(pw.outputs[0],ml.inputs[0]); nt.links.new(ml.outputs[0],es.inputs['Strength'])
        nt.links.new(b.outputs[0],ad.inputs[0]); nt.links.new(es.outputs[0],ad.inputs[1]); nt.links.new(ad.outputs[0],out.inputs['Surface'])
        rim=ml.inputs[1]
        for f,v in [(fh-0.5,0),(fh,4.0),(fh+4,1.2),(fh+12,0)]:
            rim.default_value=v; rim.keyframe_insert('default_value',frame=f)
        for f,v in [(fh-0.5,0),(fh,0.25),(fh+4,0.06),(fh+10,0)]:   # faint body glow
            em.default_value=v; em.keyframe_insert('default_value',frame=f)
# ---------- marble
bpy.ops.mesh.primitive_uv_sphere_add(radius=R,segments=64,ring_count=32); mb=bpy.context.object; mb.name='marble'; bpy.ops.object.shade_smooth()
mm,mbsdf=mat('marble',(0.05,0.75,0.35),rough=0.02,trans=1.0,ior=1.52)
mbsdf.inputs['Subsurface Weight'].default_value=0.0
# inner cat's-eye swirl via volume absorption for colour depth
nt=mm.node_tree; vol=nt.nodes.new('ShaderNodeVolumeAbsorption'); vol.inputs['Color'].default_value=(0.1,0.8,0.35,1); vol.inputs['Density'].default_value=6.0
nt.links.new(vol.outputs[0],nt.nodes['Material Output'].inputs['Volume'])
mb.data.materials.append(mm)
prev=None; ang=0.0
for f,(x,z) in enumerate(P['marble']):
    if prev is not None: ang+= -(x-prev)/R
    mb.location=(x,0,z); mb.rotation_euler=(0.3,ang,0)
    mb.keyframe_insert('location',frame=f); mb.keyframe_insert('rotation_euler',frame=f); prev=x
# ---------- camera + lights rig
rig=bpy.data.objects.new('rig',None); sc.collection.objects.link(rig)
cd=bpy.data.cameras.new('cam'); cd.lens=40; cd.sensor_fit='VERTICAL'; cd.sensor_height=36
cd.dof.use_dof=True; cd.dof.aperture_fstop=5.6
cam=bpy.data.objects.new('cam',cd); sc.collection.objects.link(cam); sc.camera=cam; cam.parent=rig
off=Vector((0.7,-7.2,1.4)) if P.get('layout')=='zigzag' else Vector((1.3,-6.6,1.9))
aim=Vector((0,0,0))
if V2: off=Vector((0.5,-5.3,1.0)); aim=Vector((0,0,-0.9))
cam.location=off
cam.rotation_euler=(aim-off).to_track_quat('-Z','Y').to_euler()
cd.dof.focus_distance=(aim-off).length
for f,(cx,cz) in enumerate(P['camera']):
    rig.location=(cx,0,cz); rig.keyframe_insert('location',frame=f)
def light(name,typ,loc,energy,size,color=(1,1,1)):
    ld=bpy.data.lights.new(name,typ); ld.energy=energy; ld.color=color
    if typ=='AREA': ld.size=size
    o=bpy.data.objects.new(name,ld); sc.collection.objects.link(o); o.parent=rig; o.location=loc
    o.rotation_euler=(Vector((0,0,0))-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
kl=light('key','AREA',(-3.0,-4.0,4.0),380,3.0,(1.0,0.95,0.88)); kl.data.spread=math.radians(70)
light('fill','AREA',(4.0,-5.0,0.0),70,5.0,(0.85,0.9,1.0))
light('rim','AREA',(0.5,-0.8,5.0),90,2.0)
if V2:
    def reflector(name,loc,energy,sx,sy,color=(1,1,1)):
        o=light(name,'AREA',loc,energy,sx,color); o.data.shape='RECTANGLE'; o.data.size=sx; o.data.size_y=sy
        o.visible_diffuse=False; o.visible_transmission=False; o.visible_volume_scatter=False; return o
    reflector('soft_top',(0.0,-3.5,6.0),900,9.0,2.5)          # long softbox overhead-front: streak on top faces
    reflector('soft_front',(-3.2,-8.0,3.0),220,1.0,6.0,(1.0,0.97,0.92))  # narrow off-axis strip: edge streaks
    reflector('soft_side',(5.5,-4.0,0.5),350,2.0,8.0,(0.9,0.95,1.0))   # cool side strip: bevel edge highlights
    # world: bright studio gradient seen only by glossy rays, original grey for everything else
    wn=wd.node_tree.nodes; wl=wd.node_tree.links
    lp=wn.new('ShaderNodeLightPath'); tcw=wn.new('ShaderNodeTexCoord'); sep=wn.new('ShaderNodeSeparateXYZ')
    rmp=wn.new('ShaderNodeValToRGB'); rmp.color_ramp.elements[0].position=0.5; rmp.color_ramp.elements[0].color=(0.05,0.05,0.055,1)
    rmp.color_ramp.elements[1].position=0.9; rmp.color_ramp.elements[1].color=(1.0,1.0,1.0,1)
    mp2=wn.new('ShaderNodeMapRange'); mp2.inputs[1].default_value=-1; mp2.inputs[2].default_value=1
    bg2=wn.new('ShaderNodeBackground'); bg2.inputs[1].default_value=1.2
    mx=wn.new('ShaderNodeMixShader')
    wl.new(tcw.outputs['Generated'],sep.inputs[0]); wl.new(sep.outputs['Z'],mp2.inputs[0]); wl.new(mp2.outputs[0],rmp.inputs[0]); wl.new(rmp.outputs[0],bg2.inputs[0])
    wl.new(lp.outputs['Is Glossy Ray'],mx.inputs[0]); wl.new(bg.outputs[0],mx.inputs[1]); wl.new(bg2.outputs[0],mx.inputs[2])
    wl.new(mx.outputs[0],wn['World Output'].inputs[0])
# Blender 5.x (incl. macOS 5.3): Action.fcurves removed — slotted channelbags
_here=os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path: sys.path.insert(0,_here)
from blender_compat import set_path_keyframe_interpolation
set_path_keyframe_interpolation()
if V6:
    from effects_v6 import apply_v6
    apply_v6(sc, P, fps, R, wd, bg, wall, wb, mb, mm, mbsdf, rig, cam, look_for, FLASH)
if a.save_blend: bpy.ops.wm.save_as_mainfile(filepath=a.save_blend)
import time
frames=[int(x) for x in a.frames.split(',') if x.strip()] or list(range(a.start,(a.end if a.end>=0 else sc.frame_end)+1))
os.makedirs(a.out, exist_ok=True)
for f in frames:
    if os.path.exists(f"{a.out}/{f:05d}.png") and os.path.getsize(f"{a.out}/{f:05d}.png")>1000: print(f"FRAME {f} skip",flush=True); continue
    t0=time.time(); sc.frame_set(f); sc.render.filepath=f"{a.out}/{f:05d}.png"; bpy.ops.render.render(write_still=True)
    print(f"FRAME {f} {time.time()-t0:.2f}s",flush=True)
