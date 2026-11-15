r"""Extract melody note-on hits from a MIDI file in a time window.
usage: python extract_hits.py song.mid --start 0 --end 15 [--track-regex '^(0[1-9]|1[0-2])\.'] -o hits.json"""
import mido, json, re, argparse, bisect
ap=argparse.ArgumentParser(); ap.add_argument('midi'); ap.add_argument('--start',type=float,default=0); ap.add_argument('--end',type=float,default=15)
ap.add_argument('--track-regex',default=r'^\s*(0?[1-9]|1[0-2])(/\d+)?\.'); ap.add_argument('--tracks',default='',help='comma list of track indices (overrides regex)')
ap.add_argument('--merge-ms',type=float,default=60)
ap.add_argument('--tutti-min',type=int,default=0,help='if >0: a merged group of near-simultaneous notes from >= this many distinct tracks becomes ONE hit labelled --tutti-name (single-marble tutti)')
ap.add_argument('--tutti-name',default='09/09. Grand Tutti Finale'); ap.add_argument('-o',default='hits.json')
ap.add_argument('--markers',action='store_true',help='label each note with the active marker text (e.g. "08. Vibraphone (颤音琴)") instead of its track name; '
                'use with relay MIDIs where one track walks through many instruments (inst64). Also records the GM program per note.')
ap.add_argument('--instrument-set',default='',help='registry set written into hits.json -> plan (e.g. jewelbox, jewelbox:F1); library.assign then maps by registry')
a=ap.parse_args()
mid=mido.MidiFile(a.midi)
# tempo map
tmp=[]
for tr in mid.tracks:
    t=0
    for m in tr:
        t+=m.time
        if m.type=='set_tempo': tmp.append((t,m.tempo))
tmp.sort(); 
if not tmp or tmp[0][0]>0: tmp.insert(0,(0,500000))
segs=[]; sec=0.0
for i,(tk,tp) in enumerate(tmp):
    if i: sec+=(tk-tmp[i-1][0])*tmp[i-1][1]/1e6/mid.ticks_per_beat
    segs.append((tk,sec,tp))
ticks=[s[0] for s in segs]
def t2s(tk):
    i=bisect.bisect_right(ticks,tk)-1; s=segs[i]; return s[1]+(tk-s[0])*s[2]/1e6/mid.ticks_per_beat
def _txt(x):
    try: return x.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError): return x
MARK=[]   # (tick, text) of every marker in the file
for tr in mid.tracks:
    t=0
    for m in tr:
        t+=m.time
        if m.type=='marker': MARK.append((t,_txt(m.text)))
MARK.sort(); MT=[x[0] for x in MARK]
def marker_at(tk):
    i=bisect.bisect_right(MT,tk)-1; return MARK[i][1] if i>=0 else None
names=[]; sel=[]
idx=[int(x) for x in a.tracks.split(',') if x.strip()]
for i,tr in enumerate(mid.tracks):
    nm=_txt(next((m.name for m in tr if m.type=='track_name'),f'track{i}')); names.append(nm)
    if (idx and i in idx) or (not idx and re.search(a.track_regex,nm)): sel.append(i)
notes=[]
for i in sel:
    t=0; prog={}
    for m in mid.tracks[i]:
        t+=m.time
        if m.type=='program_change': prog[m.channel]=m.program
        if m.type=='note_on' and m.velocity>0:
            s=t2s(t); tn=(marker_at(t) or names[i]) if a.markers else names[i]
            if a.start-1e-6<=s<a.end-1e-4: notes.append(dict(time=round(s-a.start,5),abs_time=round(s,5),note=m.note,vel=m.velocity,track=i,track_name=tn,drum=(m.channel==9),program=prog.get(m.channel)))
notes.sort(key=lambda n:(n['time'],-n['note']))
hits=[]; grp=[]
def _close():
    if a.tutti_min>0 and grp and len({g['track'] for g in grp})>=a.tutti_min:
        hits[-1]=dict(hits[-1],track=-1,track_name=a.tutti_name,tutti_tracks=sorted({g['track_name'] for g in grp}))
for n in notes:  # merge chords / near-simultaneous notes -> one hit (highest note); identical tutti onsets -> one hit
    if hits and n['time']-hits[-1]['time']<a.merge_ms/1000: grp.append(n); continue
    _close(); hits.append(n); grp=[n]
_close()
out=dict(midi=a.midi,start=a.start,end=a.end,tracks=[names[i] for i in sel],hits=hits)
if a.instrument_set: out['instrument_set']=a.instrument_set
json.dump(out,open(a.o,'w'),indent=1,ensure_ascii=False)
print('selected tracks:',[names[i] for i in sel]); print('hits:',len(hits))
for h in hits: print(f"{h['time']:7.3f}s  note {h['note']:3d}  {h['track_name']}")
