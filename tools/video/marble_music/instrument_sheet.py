"""instrument_sheet.py plan_zz.json stills_dir out.png [--frames f1,f2,...] -- one labelled tile per instrument section (mid-section hit frame)."""
import json,sys,os
from PIL import Image,ImageDraw,ImageFont

_FR=None
if '--frames' in sys.argv:
    _i=sys.argv.index('--frames'); _FR=set(int(x) for x in sys.argv[_i+1].split(',')); del sys.argv[_i:_i+2]
def pick_key(ks, fps):
    """key used for a section's still: the one whose hit frame is in --frames (if given), else the mid-section hit."""
    if _FR:
        for k in ks:
            if round(k['t']*fps) in _FR: return k
    return ks[len(ks)//2]

P=json.load(open(sys.argv[1])); fd=sys.argv[2]; out=sys.argv[3]; fps=P['fps']
secs={}; [secs.setdefault(k['track'],[]).append(k) for k in P['keys']]
NAMES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
tw,th,hd=360,640,56; cols=6; rows=(len(secs)+cols-1)//cols
sheet=Image.new('RGB',(cols*tw,rows*(th+hd)),(18,18,18)); d=ImageDraw.Draw(sheet)

def _font(size, bold=False):
    from PIL import ImageFont
    names = []
    if bold:
        names += ['DejaVuSans-Bold.ttf','Arial Bold.ttf','Arial Unicode.ttf','LiberationSans-Bold.ttf','Helvetica.ttc']
    else:
        names += ['DejaVuSans.ttf','Arial.ttf','Arial Unicode.ttf','LiberationSans-Regular.ttf','Helvetica.ttc']
    roots = [
        '/usr/share/fonts/truetype/dejavu',
        '/usr/share/fonts/truetype/liberation',
        '/usr/share/fonts/truetype/freefont',
        '/System/Library/Fonts/Supplemental',
        '/System/Library/Fonts',
        '/Library/Fonts',
    ]
    for root in roots:
        for name in names:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                try: return ImageFont.truetype(path, size)
                except Exception: continue
    return ImageFont.load_default()

F=lambda s,b=False: _font(s,b)
for idx,(tr,ks) in enumerate(secs.items()):
    k=pick_key(ks,fps); f=round(k['t']*fps); p=f"{fd}/{f:05d}.png"; x=(idx%cols)*tw; y=(idx//cols)*(th+hd)
    if os.path.exists(p): sheet.paste(Image.open(p).convert('RGB').resize((tw,th)),(x,y+hd))
    d.text((x+8,y+5),tr.split('(')[0].strip(),fill=(255,255,255),font=F(20,True))
    d.text((x+8,y+31),f"frame {f}  {k['t']:.2f}s  {NAMES[k['note']%12]}{k['note']//12-1}",fill=(190,190,190),font=F(15))
sheet.save(out); print('saved',out)
