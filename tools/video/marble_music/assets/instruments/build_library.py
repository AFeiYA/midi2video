"""Build every instrument asset: model.blend + model.glb + probe_<variant>.npy (surface samples), and write measured
contact / keep-out data back into meta.json.   usage: blender -b -P assets/instruments/build_library.py"""
import bpy, sys, os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import _common as C
names = sorted(d for d in os.listdir(HERE) if os.path.isfile(os.path.join(HERE, d, 'meta.json')))
report = []
for n in names:
    d = os.path.join(HERE, n); meta, bmod, mmod = C.load_asset(d)
    meta['measured'] = {}
    for var in meta['variants']:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        o = C.make_asset(meta, bmod, var, f'{n}_{var}')
        sh = mmod.shared(C)
        for role in meta['slots']:
            if role == 'body': m = mmod.body(C, f'{n}_body_{var}', 0, 60, None if var == 'default' else var)
            elif role == 'pin': m = C.mat('pin', (0.7,0.7,0.72), rough=0.25, metal=1.0)
            else: m = sh[role]
            o.data.materials.append(m)
        P = C.surface_points(o); np.save(os.path.join(d, f'probe_{var}.npy'), P)
        slab = np.abs(P[:,1]) < C.R + 0.005
        centre = slab & (np.abs(P[:,0]) < 0.012) & (np.abs(P[:,1]) < 0.012)
        top = float(P[centre,2].max()) if centre.any() else None
        outside = slab & ((np.abs(P[:,0]) > C.PL/2 + 1e-4) | (np.abs(P[:,2]) > C.TOP + 1e-4))
        ko = [P[outside].min(0).round(4).tolist(), P[outside].max(0).round(4).tolist()] if outside.any() else None
        meta['measured'][var] = dict(contact_top_z_at_origin=round(top, 5) if top is not None else None, bbox=[P.min(0).round(4).tolist(), P.max(0).round(4).tolist()],
                                     keepout_aabb_in_marble_slab=ko, probe_points=int(len(P)), triangles=len(o.data.polygons))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(d, 'model.blend' if var == 'default' else f'model_{var}.blend'))
        try:
            bpy.ops.export_scene.gltf(filepath=os.path.join(d, 'model.glb' if var == 'default' else f'model_{var}.glb'), export_format='GLB', use_selection=False)
        except Exception as e: print('glb export failed', n, e)
        report.append((n, var, top, ko, len(P)))
    json.dump(meta, open(os.path.join(d, 'meta.json'), 'w'), indent=1)
print('\nLIBRARY REPORT')
for r in report: print('LIB', r[0], r[1], 'top@origin', r[2], 'keepout', r[3], 'pts', r[4])
