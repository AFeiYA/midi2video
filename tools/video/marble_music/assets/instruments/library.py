"""bpy-free helpers: map plan keys -> (asset name, variant, index within section). Used by scene.py (v3+) and check_keepout.py.
Look overrides: an instrument folder may contain a sub-folder named after a look (e.g. guitar/v4/) with its own
build.py / material.py / meta.json / probe_*.npy; it replaces the base asset for that look only (base = v3, untouched)."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
LOOK_ORDER = ['v3', 'v4']
def metas(look='v3'):
    out = {}
    for d in sorted(os.listdir(HERE)):
        base = os.path.join(HERE, d)
        if not os.path.isfile(os.path.join(base, 'meta.json')): continue
        use = base
        # newest override not newer than the requested look
        for lk in LOOK_ORDER[1:LOOK_ORDER.index(look)+1] if look in LOOK_ORDER else []:
            if os.path.isfile(os.path.join(base, lk, 'meta.json')): use = os.path.join(base, lk)
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
        v = m['variants'][j % len(m['variants'])] if m['variant_rule'] == 'alternate' else m['variants'][0]
        out.append((m['name'], v, j))
    return out
