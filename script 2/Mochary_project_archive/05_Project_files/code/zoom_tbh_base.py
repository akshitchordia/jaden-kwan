import sys, math, subprocess, numpy as np, cv2
TH="/mnt/user-data/uploads/tbh_gimmick_cut_eyecontact_v1.mp4"
FPS=24000/1001; SW,SH=1728,3072; W,H=1080,1920; DUR=55.0967; N=int(math.ceil(DUR*FPS))
FACE=(864.0,1448.0)          # face centre in source pixels
def eio(x): x=min(1,max(0,x)); return 0.5-0.5*math.cos(math.pi*x)
def eic(x): x=min(1,max(0,x)); return 4*x**3 if x<0.5 else 1-(-2*x+2)**3/2
def eoc(x): x=min(1,max(0,x)); return 1-(1-x)**3
# ZOOM SCRIPT: list of shots (cut_time, start_zoom, [ (t, kind, args) ... ])
#   push: slow eased push from current zoom to target by time t_end
#   snap: eased zoom starting at t, duration d, to target (fast)
SHOTS=[
 (0.00, 1.00, [("push",2.10,1.03), ("ease",2.10,0.40,1.12), ("push",5.62,1.14)]),
 (5.62, 1.00, [("push",7.86,1.04)]),
 (7.86, 1.15, [("push",9.50,1.18), ("ease",9.50,0.38,1.32), ("push",10.62,1.33)]),
 (10.62,1.33, [("ease",10.62,0.70,1.00), ("push",16.16,1.06)]),
 (16.16,1.16, [("push",20.16,1.22), ("snap",20.16,0.25,1.38), ("push",21.28,1.39)]),
 (21.28,1.12, [("push",22.44,1.14), ("ease",22.44,0.55,1.00), ("push",23.60,1.01)]),
 (23.60,1.14, [("push",25.45,1.17)]),
 (25.45,1.26, [("push",26.48,1.28)]),
 (26.48,1.08, [("push",28.40,1.12)]),
 (28.40,1.00, [("push",30.56,1.04)]),
 (30.56,1.04, [("ease",30.56,2.30,1.16), ("push",32.94,1.16)]),
 (32.94,1.16, [("snap",32.94,0.22,1.36), ("push",34.06,1.37)]),
 (34.06,1.00, [("push",39.42,1.08)]),
 (39.42,1.15, [("push",40.78,1.17)]),
 (40.78,1.05, [("push",42.86,1.08)]),
 (42.86,1.20, [("push",44.70,1.24)]),
 (44.70,1.24, [("ease",44.70,0.60,1.00), ("push",47.10,1.06), ("ease",47.10,0.40,1.18), ("push",48.54,1.19)]),
 (48.54,1.00, [("push",50.14,1.05), ("snap",50.14,0.30,1.22), ("push",52.22,1.23)]),
 (52.22,1.10, [("push",54.40,1.20), ("ease",54.40,0.50,1.38), ("push",55.10,1.39)]),
]
def zoom_at(t):
    t=max(0.0,t); i=max(k for k,s in enumerate(SHOTS) if s[0]<=t); t0,z,evs=SHOTS[i]
    cur_t=t0
    for kind,a,b,*c in [(e[0],)+tuple(e[1:]) for e in evs]:
        if kind=="push":
            tend,zt=a,b
            if t<tend: return z+(zt-z)*eio((t-cur_t)/max(1e-6,tend-cur_t))
            z,cur_t=zt,tend
        else:
            ts,d,zt=a,b,c[0]
            if t<ts: return z
            if t<ts+d: return z+(zt-z)*(eoc if kind=="snap" else eic)((t-ts)/d)
            z,cur_t=zt,ts+d
    return z
def render(src,z):
    s=z*(2*W/SW)   # render at 2x then downsample (clean, no aliasing)
    M=np.float32([[s,0,W - s*FACE[0]],[0,s,2*H*0.4714 - s*FACE[1]]])   # keep face at the same screen spot
    big=cv2.warpAffine(src,M,(2*W,2*H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA)
dec=subprocess.Popen(["ffmpeg","-v","error","-i",TH,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24000/1001","-i","-","-i",TH,"-map","0:v","-map","1:a","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",sys.argv[1]],stdin=subprocess.PIPE)
log=open(sys.argv[2],"w")
for n in range(N):
    raw=dec.stdout.read(SW*SH*3)
    if len(raw)<SW*SH*3: break
    src=np.frombuffer(raw,np.uint8).reshape(SH,SW,3); t=n/FPS
    z0=zoom_at(t-0.5/FPS*0.5); z1=zoom_at(t+0.5/FPS*0.5); z=zoom_at(t)
    cut=any(abs(t-s[0])<0.6/FPS for s in SHOTS)
    if abs(z1-z0)>0.003 and not cut:   # motion blur on fast zooms (180-degree shutter)
        fr=np.mean([render(src,z0+(z1-z0)*k/5).astype(np.float32) for k in range(6)],axis=0).astype(np.uint8)
    else: fr=render(src,z)
    log.write(f"{t:.3f} {z:.4f}\n")
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("done",n+1)
