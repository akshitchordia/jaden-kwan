import sys, subprocess
from brolls import *
OUT='/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/out/broll/'
import os; os.makedirs(OUT,exist_ok=True)
for name in sys.argv[1].split(','):
    nm,t0,t1,fn=next(b for b in BEATS if b[0]==name)
    n0,n1=int(round(t0*FPS)),int(round(t1*FPS))
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24000/1001','-i','-','-c:v','libx264','-crf','10','-preset','medium','-pix_fmt','yuv420p',OUT+f'{name}_{n0}.mp4'],stdin=subprocess.PIPE)
    for n in range(n0,n1):
        img=render_frame(name,n,ss=2); enc.stdin.write((np.clip(img,0,1)*255+0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print('done',name,n0,n1,flush=True)
