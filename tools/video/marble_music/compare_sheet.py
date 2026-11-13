"""compare_sheet.py plan.json old_dir new_dir out.png -- per instrument: old (left) vs new (right)."""
import json,sys,os
from PIL import Image,ImageDraw,ImageFont
P=json.load(open(sys.argv[1])); od,nd,out=sys.argv[2:5]; fps=P['fps']
LAB=(sys.argv[5],sys.argv[6]) if len(sys.argv)>6 else ('v1 (old)','v2 (new)')
secs={}; [secs.setdefault(k['track'],[]).append(k) for k in P['keys']]

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
tw,th,hd,gap=270,480,48,14; cols=4; pw=2*tw+gap; rows=(len(secs)+cols-1)//cols
sh=Image.new('RGB',(cols*pw,rows*(th+hd)),(18,18,18)); d=ImageDraw.Draw(sh)
for i,(tr,ks) in enumerate(secs.items()):
    f=round(ks[len(ks)//2]['t']*fps); x=(i%cols)*pw; y=(i//cols)*(th+hd)
    for j,dd in enumerate((od,nd)):
        p=f"{dd}/{f:05d}.png"
        if os.path.exists(p): sh.paste(Image.open(p).convert('RGB').resize((tw,th)),(x+j*tw,y+hd))
        d.text((x+j*tw+6,y+28),LAB[j],fill=(180,180,180),font=F(14))
    d.text((x+6,y+4),f"{tr.split('(')[0].strip()}   frame {f}",fill=(255,255,255),font=F(17,True))
sh.save(out); print('saved',out)
