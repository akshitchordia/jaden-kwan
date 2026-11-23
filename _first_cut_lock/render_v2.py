"""Device renderer for Fridge v2. Usage: python3 render_v2.py TL_START TL_END -> /tmp/fr2/v_XXXX.mp4"""
import sys, os, json, subprocess, numpy as np, cv2
cv2.setNumThreads(2)
W = os.path.expanduser('~/mnt/Video editor/14th nov')
MASTER = W + '/ScaleAI_Fridge_RoughCut_v1_master.mov'
FPS = 24000 / 1001
A, B = int(sys.argv[1]), int(sys.argv[2])
os.makedirs('/tmp/fr2', exist_ok=True)
tl = json.load(open('/tmp/fr2/tl_v2.json'))
AR0 = next(i for i, x in enumerate(tl) if x['k'] == 'ar')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920',
                        '-r', '24000/1001', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16',
                        '-pix_fmt', 'yuv420p', '-video_track_timescale', '24000', f'/tmp/fr2/v_{A:04d}.mp4'],
                       stdin=subprocess.PIPE)
frames = tl[A:B]
rc = [x['src'] for x in frames if x['k'] == 'rc']
dec = None; cur = None
if rc:
    lo, hi = min(rc), max(rc)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(lo - 0.5) / FPS:.6f}', '-i', MASTER, '-map', '0:v:0',
                            '-frames:v', str(hi - lo + 1), '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:1'],
                           stdout=subprocess.PIPE, bufsize=0)
    cur = lo - 1
arc = None
if any(x['k'] == 'ar' for x in frames):
    arc = cv2.VideoCapture('/tmp/fr2/arch_v2.mp4')
    first_ar = A + next(i for i, x in enumerate(frames) if x['k'] == 'ar')
    for _ in range(first_ar - AR0):
        arc.read()
sz = 1728 * 3072 * 3
buf = bytearray(sz); mv = memoryview(buf)
def read_frame():
    got = 0
    while got < sz:
        k = dec.stdout.readinto(mv[got:])
        if not k: raise SystemExit('short read')
        got += k
for x in frames:
    if x['k'] == 'ar':
        ok, out = arc.read()
        enc.stdin.write(out.tobytes()); continue
    while cur < x['src']:
        read_frame(); cur += 1
    img = np.frombuffer(buf, np.uint8).reshape(3072, 1728, 3)
    T = x['T']
    if len(T) == 1:
        s, tx, ty = T[0]
        sig = 0.45 * np.sqrt(max(0.0, 1 / s ** 2 - 1))
        src = cv2.GaussianBlur(img, (0, 0), sig) if sig > 0.15 else img
        out = cv2.warpAffine(src, np.float32([[s, 0, tx], [0, s, ty]]), (1080, 1920),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    else:
        T = T[::max(1, len(T) // 12)]
        acc = np.zeros((1920, 1080, 3), np.float32)
        for s, tx, ty in T:
            acc += cv2.warpAffine(img, np.float32([[s, 0, tx], [0, s, ty]]), (1080, 1920),
                                  flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = (acc / len(T) + 0.5).astype(np.uint8)
    enc.stdin.write(out.tobytes())
if dec:
    dec.stdout.close(); dec.kill()
enc.stdin.close(); enc.wait()
print('done', A, B)
