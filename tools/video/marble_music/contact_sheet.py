"""contact_sheet.py plan.json frames_dir out.png [n] -- frames nearest to note hits, labelled with time/note."""
import json,sys,os
from PIL import Image,ImageDraw,ImageFont
p=json.load(open(sys.argv[1])); fd=sys.argv[2]; out=sys.argv[3]; n=int(sys.argv[4]) if len(sys.argv)>4 else 12
fps=p['fps']; keys=p['keys']; step=max(1,len(keys)//n); sel=keys[::step][:n]
NAMES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
tw,th=270,480; cols=6; rows=(len(sel)+cols-1)//cols
sheet=Image.new('RGB',(cols*tw,rows*(th+34)),(20,20,20)); d=ImageDraw.Draw(sheet)

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

font=_font(18)
for idx,k in enumerate(sel):
    f=int(round(k['t']*fps)); path=f"{fd}/{f:05d}.png"
    if not os.path.exists(path): continue
    im=Image.open(path).convert('RGB').resize((tw,th)); x=(idx%cols)*tw; y=(idx//cols)*(th+34)
    sheet.paste(im,(x,y+34))
    nm='perc' if k['drum'] else NAMES[k['note']%12]+str(k['note']//12-1)
    d.text((x+6,y+6),f"f{f} {k['t']:.2f}s {nm} {k['track'][:10]}",fill=(255,255,255),font=font)
sheet.save(out); print('saved',out,len(sel),'tiles')
