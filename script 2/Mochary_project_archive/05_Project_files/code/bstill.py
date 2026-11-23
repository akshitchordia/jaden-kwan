import sys,time; sys.argv=[sys.argv[0]]+sys.argv[1:]
from brolls import *
names=sys.argv[1].split(','); fracs=[float(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
tiles=[]
for nm in names:
    b=next(b for b in BEATS if b[0]==nm); row=[]
    for f in fracs:
        T=b[1]+(b[2]-b[1])*f; n=int(round(T*FPS)); t=time.time()
        img=render_frame(nm,n,ss=1); print(nm,f,round(time.time()-t,2),flush=True)
        row.append(cv2.resize((img*255).astype(np.uint8),(270,480),interpolation=cv2.INTER_AREA))
    tiles.append(np.hstack(row))
cv2.imwrite(out,cv2.cvtColor(np.vstack(tiles),cv2.COLOR_RGB2BGR))
