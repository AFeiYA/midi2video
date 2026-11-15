"""Shared writer for procedural asset generators (gen/*.py write asset folders: build.py / material.py / meta.json).
Run a generator with plain python (no bpy):  python gen/jewelbox_f1.py   then build the cache with
  blender -b -P assets/instruments/build_library.py -- --only grand_piano,rhodes,...
Existing 'measured' data in meta.json is preserved until build_library.py rewrites it."""
import json, os, textwrap
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINS = [{"x": -0.3, "z": 0.02, "y_start": 0.05, "radius": 0.022}, {"x": 0.3, "z": 0.02, "y_start": 0.05, "radius": 0.022}]
CONTACT = {"length": 0.62, "thickness": 0.09, "point": [0, 0, 0.045], "normal": [0, 0, 1], "tangent": [1, 0, 0], "note": "marble centre at hit = point + normal*R"}
NEVER = '(?!)'   # tracks_regex that never matches: the asset is reachable only through registry.py (--instrument-set / plan['instrument_set'])
HDR = '''import math
# local frame: +Z = paddle normal, contact top face z=+0.045 over x in [-0.31,0.31]; Y = into wall (wall y=0.30).
# |y|<0.15 is the marble slab (keep-out checked); y in [0.155,0.285] is 'backplate' space the marble can never touch.
'''
def write(folder, meta, build, material, lib=LIB):
    d = os.path.join(lib, folder); os.makedirs(d, exist_ok=True)
    old = {}
    if os.path.isfile(os.path.join(d, 'meta.json')): old = json.load(open(os.path.join(d, 'meta.json'))).get('measured', {})
    meta = dict(meta); meta.setdefault('variants', ['default']); meta.setdefault('variant_rule', 'single'); meta.setdefault('contact', CONTACT)
    meta.setdefault('pins', PINS); meta.setdefault('scale', 1.0); meta['license'] = 'CC0-1.0 (original procedural geometry, written for this project)'
    meta['author'] = 'procedural (marble pipeline)'; meta['source_url'] = None; meta.setdefault('look', 'v5')
    if old: meta['measured'] = old
    open(os.path.join(d, 'meta.json'), 'w').write(json.dumps(meta, indent=1, ensure_ascii=False))
    open(os.path.join(d, 'build.py'), 'w').write(textwrap.dedent(build).lstrip())
    open(os.path.join(d, 'material.py'), 'w').write(textwrap.dedent(material).lstrip())
    return d
