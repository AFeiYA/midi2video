"""bpy-free helpers: map plan keys -> (asset name, variant, index within section). Used by scene.py (v3) and check_keepout.py."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
def metas():
    return {d: json.load(open(os.path.join(HERE, d, 'meta.json'))) for d in sorted(os.listdir(HERE)) if os.path.isfile(os.path.join(HERE, d, 'meta.json'))}
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
