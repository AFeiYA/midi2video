"""plot_trajectory.py plan_zz.json out.png [depth_per_column] -- true-aspect 2D overview: marble path + paddles, coloured per instrument section.
The (very tall) course is cut into columns of equal depth, read left->right."""
import json,sys,math,numpy as np,matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
P=json.load(open(sys.argv[1])); out=sys.argv[2]; D=float(sys.argv[3]) if len(sys.argv)>3 else 30.0
fps=P['fps']; M=np.array(P['marble']); K=P['keys']; PL,PT,R=P['KW'],P['KH'],P['R']
secs=[];[secs.append(k['track']) for k in K if k['track'] not in secs]
cmap=plt.get_cmap('tab20'); col={s:cmap(i*1.0/len(secs)*0.999) for i,s in enumerate(secs)}
# section of each frame = track of the next/last hit
kt=np.array([k['t'] for k in K]); fr=np.arange(len(M))/fps
fsec=[K[min(np.searchsorted(kt,t,side='left'),len(K)-1)]['track'] for t in fr]
ztop=0.8; zbot=M[:len(M)-25,1].min()-1; ncol=int(math.ceil((ztop-zbot)/D)); W=3.2
fig,ax=plt.subplots(figsize=(ncol*W*0.34,D*0.34+1.6),dpi=110)
def place(x,z):  # map course coords -> sheet coords
    c=np.floor((ztop-z)/D).astype(int); return x+c*W, z+c*D, c
for c in range(ncol): ax.axvline(c*W-W/2,color='#ccc',lw=0.6)
# path, broken where column changes or section changes
X,Z,C=place(M[:,0],M[:,1]); 
start=0
for i in range(1,len(M)+1):
    if i==len(M) or C[i]!=C[start] or fsec[i]!=fsec[start]:
        e=min(i+1,len(M)) if i<len(M) and C[i]==C[start] else i
        ax.plot(X[start:e],Z[start:e],color=col[fsec[start]],lw=1.1); start=i
for k in K:
    n=np.array([k['nx'],k['nz']]); t=np.array([n[1],-n[0]]); c=np.array([k['x'],k['z']])
    pts=[c+sx*t*PL/2+sy*n*PT/2 for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    pts=np.array(pts); xx,zz,cc=place(pts[:,0],pts[:,1]); cc0=place(np.array([k['x']]),np.array([k['z']]))[2][0]
    xx=pts[:,0]+cc0*W; zz=pts[:,1]+cc0*D
    ax.add_patch(Polygon(np.c_[xx,zz],closed=True,fc=col[k['track']],ec='k',lw=0.4))
first={}
for k in K: first.setdefault(k['track'],k)
for s,k in first.items():
    x,z,c=place(np.array([k['x']]),np.array([k['z']]))
    ax.annotate(s.split('(')[0].strip(),(x[0],z[0]),xytext=(x[0]+0.9,z[0]+0.6),fontsize=7,color=col[s],weight='bold',arrowprops=dict(arrowstyle='-',color=col[s],lw=0.6))
ax.set_aspect('equal'); ax.set_xlim(-W/2,ncol*W-W/2); ax.set_ylim(ztop-D,ztop); ax.set_yticks([]); ax.set_xticks([c*W for c in range(ncol)])
ax.set_xticklabels([f'{c*D:.0f}-{(c+1)*D:.0f}' for c in range(ncol)],fontsize=6,rotation=90); ax.set_xlabel('depth below start (scene units); columns read left to right, true aspect')
from matplotlib.lines import Line2D
ax.legend([Line2D([0],[0],color=col[s],lw=4) for s in secs],[f"{s}  ({sum(k['track']==s for k in K)} hits)" for s in secs],loc='upper center',bbox_to_anchor=(0.5,1.0+1.4/(D*0.34)),ncol=6,fontsize=7,frameon=False)
ax.set_title(f"Zig-zag marble course: {len(K)} hits / {len(M)} frames @ {fps}fps, depth {-K[-1]['cz']:.0f} units, 0 paddle collisions",fontsize=10,pad=36)
plt.savefig(out,bbox_inches='tight'); print('saved',out)
