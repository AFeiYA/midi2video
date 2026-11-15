"""bpy-free instrument registry for programmatic use (the 64-instrument GM set + finale + combo assets).
Data lives in registry.json (hand-editable).  The style series has a working name (series.id = 'jewelbox',
'Jewelbox Orchestra / 珠匣乐团'); rename it in registry.json only -- code refers to SERIES['id'].

    from registry import get_instrument, resolve_track, instrument_set, striker
    get_instrument('gm:0')            -> entry for Acoustic Grand Piano
    get_instrument('num:12') / get_instrument('12') / get_instrument('id:dulcimer')
    get_instrument('Vibraphone') / get_instrument('颤音琴') / get_instrument('08. Vibraphone (颤音琴)')
    resolve_track(track_name, program=None)   -> entry or None (marker/track text first, GM program second)
    instrument_set('jewelbox')  -> all 65 entries in order;  'jewelbox:F1' -> family 1;  'hook50' / 'jingle12' -> named sets
    striker(entry, look='v5')   -> asset dir, contact point/normal, keep-out bbox, pins, hanging tubes, flash colour, variants

Entry keys: num, id, gm, family, en, zh, aliases, asset (folder under assets/instruments), status
(reuse | adapt | new, relative to the pre-existing library), title {icon: titles.py NAMES id or None, accent rgb}, track.
"""
import os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
_DB = None
def db():
    global _DB
    if _DB is None: _DB = json.load(open(os.path.join(HERE, 'registry.json'), encoding='utf-8'))
    return _DB
def entries(): return db()['instruments']

def series(): return db()['series']

def _norm(s): return re.sub(r'[\s_\-/&().,·]+', ' ', s.lower()).strip()
_NUM = re.compile(r'^\s*(\d{1,2})(?:/\d+)?\s*[.:)\-]\s*')
def get_instrument(key):
    """'gm:N' | 'num:N' | 'id:slug' | 'NN' | free text (EN/中文 name, alias, or a 'NN. Name (中文)' marker/track string)."""
    E = entries(); k = str(key).strip()
    if k.startswith('gm:'): g = int(k[3:]); return next((e for e in E if e['gm'] == g), None)
    if k.startswith('num:') or k.isdigit(): n = int(k.split(':')[-1]); return next((e for e in E if e['num'] == n), None)
    if k.startswith('id:'): return next((e for e in E if e['id'] == k[3:]), None)
    hit = next((e for e in E if e['id'] == k or e['asset'] == k), None)
    if hit: return hit
    m = _NUM.match(k)
    if m and next((e for e in E if e['num'] == int(m.group(1))), None):
        e = next(e for e in E if e['num'] == int(m.group(1)))
        rest = _norm(k[m.end():])
        if not rest or _norm(e['en']) in rest or e['zh'] in k or any(_norm(a) in rest for a in e['aliases']): return e
    t = _norm(k)
    for e in E:                                   # exact name / alias
        if t in (_norm(e['en']), _norm(e['zh'])) or t in (_norm(a) for a in e['aliases']): return e
    best = None                                   # longest contained name / alias (zh or en)
    for e in E:
        for c in [e['en'], e['zh']] + e['aliases']:
            c2 = _norm(c)
            if len(c2) >= 3 and (c2 in t or (re.fullmatch(r'[\w ]*', c2) is None and c in k)):
                if best is None or len(c2) > best[0]: best = (len(c2), e)
    return best[1] if best else None
def resolve_track(name, program=None):
    e = get_instrument(name) if name else None
    if e is None and program is not None: e = get_instrument(f'gm:{int(program)}')
    return e
def instrument_set(name):
    """'jewelbox' (series id) -> the 64 + finale; '<series>:F1'..':F6' -> one family; other names -> registry.json sets."""
    D = db(); sid = D['series']['id']; base, _, fam = name.partition(':')
    if base in (sid, 'inst64', 'jewelbox'):
        out = [e for e in entries() if e['num'] is not None]
        return [e for e in out if e['family'] == fam] if fam else out
    if base in D['sets']: return [get_instrument('id:' + i) for i in D['sets'][base]]
    raise KeyError(f'unknown instrument set {name!r}; known: {sid}, {sid}:F1..F6, ' + ', '.join(D['sets']))
def set_assets(name):
    """{instrument id -> asset folder} for a set"""
    return {e['id']: e['asset'] for e in instrument_set(name)}

def asset_dir(entry, look='v5'):
    import library
    m = library.metas(look).get(entry['asset']); return m['_dir'] if m else None
def striker(entry, look='v5'):
    """programmatic striker geometry from the asset's meta.json (measured fields are written by build_library.py)."""
    import library
    m = library.metas(look).get(entry['asset'])
    if m is None: return dict(asset=entry['asset'], built=False)
    c = m.get('contact', {}); meas = m.get('measured', {})
    return dict(asset=entry['asset'], built=True, dir=m['_dir'], contact_point=c.get('point'), contact_normal=c.get('normal', [0, 0, 1]),
                contact_length=c.get('length'), contact_thickness=c.get('thickness'),
                bbox={v: d.get('bbox') for v, d in meas.items()}, keepout={v: d.get('keepout_aabb_in_marble_slab') for v, d in meas.items()},
                pins=m.get('pins'), hanging=m.get('hanging', []), flash_color=m.get('flash_color'), variants=m.get('variants'),
                variant_rule=m.get('variant_rule'))

if __name__ == '__main__':
    import sys
    for q in sys.argv[1:] or ['gm:0', '颤音琴', '08. Vibraphone (颤音琴)', 'Woodblock & Castanets', 'jewelbox:F1']:
        if ':F' in q or q in db()['sets']: print(q, [e['id'] for e in instrument_set(q)]); continue
        e = get_instrument(q); print(q, '->', e and (e['num'], e['id'], e['gm'], e['asset'], e['status']))
