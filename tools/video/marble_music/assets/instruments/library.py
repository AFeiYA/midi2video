"""bpy-free helpers: map plan keys -> (asset name, variant, index within section). Used by scene.py (v3+) and check_keepout.py.
Look overrides: an instrument folder may contain a sub-folder named after a look (e.g. guitar/v4/) with its own
build.py / material.py / meta.json / probe_*.npy; it replaces the base asset for that look only (base = v3, untouched)."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
LOOK_ORDER = ['v3', 'v4', 'v5', 'v6', 'v7']
def look_num(look):
    '''Numeric look index so v6 (and later) inherit the newest override <= the requested look.'''
    try:
        return int(str(look).lstrip('vV'))
    except ValueError:
        return 0
def metas(look='v3'):
    out = {}
    want = look_num(look)
    for d in sorted(os.listdir(HERE)):
        base = os.path.join(HERE, d)
        if not os.path.isfile(os.path.join(base, 'meta.json')): continue
        use = base
        # newest override whose version is not newer than the requested look
        for lk in LOOK_ORDER[1:]:
            if look_num(lk) <= want and os.path.isfile(os.path.join(base, lk, 'meta.json')): use = os.path.join(base, lk)
        m = json.load(open(os.path.join(use, 'meta.json'))); m['_dir'] = use; out[d] = m
    return out
def asset_dirs():
    """every buildable asset folder (base + look overrides)"""
    out = []
    for d in sorted(os.listdir(HERE)):
        base = os.path.join(HERE, d)
        if not os.path.isfile(os.path.join(base, 'meta.json')): continue
        out.append(base)
        for lk in LOOK_ORDER[1:]:
            if os.path.isfile(os.path.join(base, lk, 'meta.json')): out.append(os.path.join(base, lk))
    return out
def hanging_world(k, h):
    """world-space top point of a hanging (world-vertical) part attached at local point h['attach'] of key k"""
    x, y, z = h['attach']; nx, nz = k['nx'], k['nz']
    return (k['x'] + x*nz + z*nx, y, k['z'] - x*nx + z*nz)
def assign(keys, M=None):
    """returns list of (asset, variant, j) per key; j = index of the key within its section."""
    M = M or metas(); out = []; count = {}
    order = sorted(M.values(), key=lambda m: m['section'])
    for k in keys:
        t = k['track'].lower()
        m = next((m for m in order if re.search(m['tracks_regex'], t)), None) or (M['castanets'] if k.get('drum') else M['piano'])
        j = count.get(k['track'], 0); count[k['track']] = j + 1
        if m['variant_rule'] == 'alternate': v = m['variants'][j % len(m['variants'])]
        elif m['variant_rule'] == 'pitch': v = 'black' if int(k['note']) % 12 in (1, 3, 6, 8, 10) else 'white'   # v5 piano: shape follows the note
        else: v = m['variants'][0]
        out.append((m['name'], v, j))
    return out

CAM_OFF = (0.5, -5.3, 1.0)   # v2+ camera offset from the rig (scene.py); rig = (camera_x, 0, camera_z) of the plan at that frame
def aligned_local(k, cam_xz, part, cam_off=CAM_OFF):
    """v5 'aligned' part (meta.aligned): a piece placed BEHIND the marble plane (local y = part['y']) on the camera ray through the
    striker's local axis segment a->b, so in the image it continues that axis exactly (no tilt-dependent parallax step) and keeps
    the same apparent thickness. Returns (loc, rot_y, scale) in the key's LOCAL frame (the part is parented to the key).
    The part mesh is modelled along -X from the origin, length |b-a|, at local y=0."""
    import math
    cx, cz = cam_xz; Cx, Cy, Cz = cx + cam_off[0], cam_off[1], cz + cam_off[2]
    nx, nz = k['nx'], k['nz']; dx, dz = Cx - k['x'], Cz - k['z']
    cl = (dx*nz - dz*nx, Cy, dx*nx + dz*nz)                     # camera in key-local coords (x = tangent, z = normal)
    y = part['y']; s = (y - cl[1]) / (0.0 - cl[1])             # depth ratio of the plane y vs the axis plane y=0
    def proj(p): return tuple(cl[i] + (p[i] - cl[i]) * s for i in range(3))
    A = proj(part['a']); B = proj(part['b'])
    ddx, ddz = B[0] - A[0], B[2] - A[2]; L = math.hypot(ddx, ddz); L0 = math.hypot(part['b'][0] - part['a'][0], part['b'][2] - part['a'][2])
    phi = math.atan2(ddz / L, -ddx / L)                         # rotation about local Y that maps mesh -X onto A->B
    return (A[0], y, A[2]), phi, (L / L0, s, s)
