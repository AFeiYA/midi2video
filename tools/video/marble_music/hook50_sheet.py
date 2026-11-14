"""hook50 labelled stills sheet: 3x3 grid, one mid-section hit frame per section."""
import json,sys,os
from PIL import Image,ImageDraw,ImageFont
plan,fd,out=sys.argv[1:4]
P=json.load(open(plan)); fps=P['fps']; secs={}
[secs.setdefault(k['track'],[]).append(k) for k in P['keys']]
ZH={'01':'管钟+响板','02':'八音盒','03':'马林巴','04':'钢鼓','05':'卡林巴','06':'古筝','07':'8-bit 方波','08':'风笛','09':'齐奏终章'}
FB=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',26,index=2); FR=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18,index=2)
tw,th,hd,cols=400,711,70,3; rows=(len(secs)+cols-1)//cols
sh=Image.new('RGB',(cols*tw,rows*(th+hd)),(18,18,18)); d=ImageDraw.Draw(sh)
for i,(tr,ks) in enumerate(secs.items()):
    k=ks[len(ks)//2]; f=round(k['t']*fps); p=f"{fd}/{f:05d}.png"; x=(i%cols)*tw; y=(i//cols)*(th+hd)
    if os.path.exists(p): sh.paste(Image.open(p).convert('RGB').resize((tw,th)),(x,y+hd))
    num=tr.split('/')[0].strip(); en=tr.split('.',1)[1].strip()
    try: d.text((x+10,y+6),f"{num} {ZH.get(num,'')}",fill=(255,255,255),font=FB)
    except Exception: d.text((x+10,y+6),f"{num}",fill=(255,255,255),font=FB)
    d.text((x+10,y+42),f"{en}   frame {f}  {k['t']:.2f}s",fill=(185,185,185),font=FR)
sh.save(out); print('saved',out)
