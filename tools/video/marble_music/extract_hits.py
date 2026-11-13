r"""Extract melody note-on hits from a MIDI file in a time window.
usage: python extract_hits.py song.mid --start 0 --end 15 [--track-regex '^(0[1-9]|1[0-2])\.'] -o hits.json"""
import mido, json, re, argparse, bisect
ap=argparse.ArgumentParser(); ap.add_argument('midi'); ap.add_argument('--start',type=float,default=0); ap.add_argument('--end',type=float,default=15)
ap.add_argument('--track-regex',default=r'^\s*(0?[1-9]|1[0-2])\.'); ap.add_argument('--tracks',default='',help='comma list of track indices (overrides regex)')
ap.add_argument('--merge-ms',type=float,default=60); ap.add_argument('-o',default='hits.json'); a=ap.parse_args()
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
names=[]; sel=[]
idx=[int(x) for x in a.tracks.split(',') if x.strip()]
for i,tr in enumerate(mid.tracks):
    nm=next((m.name for m in tr if m.type=='track_name'),f'track{i}'); names.append(nm)
    if (idx and i in idx) or (not idx and re.search(a.track_regex,nm)): sel.append(i)
notes=[]
for i in sel:
    t=0
    for m in mid.tracks[i]:
        t+=m.time
        if m.type=='note_on' and m.velocity>0:
            s=t2s(t)
            if a.start-1e-6<=s<a.end-1e-4: notes.append(dict(time=round(s-a.start,5),abs_time=round(s,5),note=m.note,vel=m.velocity,track=i,track_name=names[i],drum=(m.channel==9)))
notes.sort(key=lambda n:(n['time'],-n['note']))
hits=[]
for n in notes:  # merge chords / near-simultaneous notes -> one hit (highest note)
    if hits and n['time']-hits[-1]['time']<a.merge_ms/1000: continue
    hits.append(n)
json.dump(dict(midi=a.midi,start=a.start,end=a.end,tracks=[names[i] for i in sel],hits=hits),open(a.o,'w'),indent=1)
print('selected tracks:',[names[i] for i in sel]); print('hits:',len(hits))
for h in hits: print(f"{h['time']:7.3f}s  note {h['note']:3d}  {h['track_name']}")
