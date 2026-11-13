"""Blender scene builder/renderer for marble music.
blender -b -P scene.py -- --plan plan.json --out frames/ [--start 0 --end 450 --samples 24 --res 1080x1920 --preview 0]"""
import bpy, json, sys, math, argparse
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ap=argparse.ArgumentParser(); ap.add_argument('--plan',default='plan.json'); ap.add_argument('--out',default='frames/')
ap.add_argument('--start',type=int,default=0); ap.add_argument('--end',type=int,default=-1); ap.add_argument('--samples',type=int,default=24)
ap.add_argument('--res',default='1080x1920'); ap.add_argument('--frames',default='',help='comma list of specific frames'); ap.add_argument('--save-blend',default=''); ap.add_argument('--device',default='AUTO',help='AUTO|CPU|METAL|CUDA|OPTIX')
a=ap.parse_args(argv)
P=json.load(open(a.plan)); fps=P['fps']; R=P['R']; KW,KD,KH=P['KW'],P['KD'],P['KH']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
W,Hh=map(int,a.res.split('x'))
sc.render.resolution_x=W; sc.render.resolution_y=Hh; sc.render.fps=fps
sc.frame_start=0; sc.frame_end=len(P['marble'])-1
sc.render.engine='CYCLES'; cy=sc.cycles; cy.device='CPU';
_dev=a.device.upper()
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
    except Exception as e: print('GPU setup failed, CPU fallback',e)
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
# instrument looks: (base material builder, flash colour)
def look_for(track,drum):
    t=track.lower()
    if 'castanet' in t or drum: kind='rosewood'
    elif 'piano' in t: kind='ivory'
    elif any(k in t for k in ['vibra','glock','tubular','steel']): kind='metal'
    elif any(k in t for k in ['marimba','xylo']): kind='wood'
    else: kind='ivory'
    return kind
FLASH={'rosewood':(1.0,0.55,0.25),'ivory':(1.0,0.85,0.55),'metal':(0.45,0.7,1.0),'wood':(1.0,0.6,0.3)}
def key_material(i,kind):
    if kind=='rosewood':
        m,b=mat(f'key{i}',(0.25,0.08,0.04),rough=0.35,coat=0.4); add_wood(m,b,(0.16,0.05,0.02),(0.42,0.16,0.07))
    elif kind=='wood':
        m,b=mat(f'key{i}',(0.5,0.25,0.1),rough=0.4,coat=0.3); add_wood(m,b,(0.35,0.15,0.06),(0.65,0.35,0.15))
    elif kind=='metal':
        m,b=mat(f'key{i}',(0.8,0.82,0.85),rough=0.22,metal=1.0)
    else:
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
for k in P['keys']:
    kind=look_for(k['track'],k['drum'])
    ZZ=('ang' in k)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(k['x'],0,k['z']),rotation=((0,k['ang'],0) if ZZ else (0,0,0)))
    o=bpy.context.object; o.name=f"key{k['i']}"; o.scale=(KW,KD,KH)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bv=o.modifiers.new('bev','BEVEL'); bv.width=0.018; bv.segments=3
    bpy.ops.object.shade_smooth()
    m,b=key_material(k['i'],kind); o.data.materials.append(m)
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
    for f,v in [(fh-0.5,0),(fh,6.0),(fh+4,1.5),(fh+12,0)]:
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
off=Vector((0.7,-7.2,1.4)) if P.get('layout')=='zigzag' else Vector((1.3,-6.6,1.9)); cam.location=off
cam.rotation_euler=(-off).to_track_quat('-Z','Y').to_euler()
cd.dof.focus_distance=off.length
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
# Blender 5.x (incl. macOS 5.3): Action.fcurves removed — slotted channelbags
import os as _os
_here=_os.path.dirname(_os.path.abspath(__file__))
if _here not in sys.path: sys.path.insert(0,_here)
from blender_compat import set_path_keyframe_interpolation
set_path_keyframe_interpolation()
if a.save_blend: bpy.ops.wm.save_as_mainfile(filepath=a.save_blend)
import time
frames=[int(x) for x in a.frames.split(',') if x.strip()] or list(range(a.start,(a.end if a.end>=0 else sc.frame_end)+1))
import os
for f in frames:
    if os.path.exists(f"{a.out}/{f:05d}.png") and os.path.getsize(f"{a.out}/{f:05d}.png")>1000: print(f"FRAME {f} skip",flush=True); continue
    t0=time.time(); sc.frame_set(f); sc.render.filepath=f"{a.out}/{f:05d}.png"; bpy.ops.render.render(write_still=True)
    print(f"FRAME {f} {time.time()-t0:.2f}s",flush=True)
