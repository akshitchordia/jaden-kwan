"""Device-side renderer for Fridge zoom v1. Usage: python3 render_dev.py START END
Renders frames [START, END) to /tmp/fr/v_START.mp4 (+ /tmp/fr/a_START.wav for talking-head chunks)."""
import sys, os, json, subprocess, numpy as np, cv2
cv2.setNumThreads(2)
W = os.path.expanduser('~/mnt/Video editor/14th nov')
MASTER = W + '/ScaleAI_Fridge_RoughCut_v1_master.mov'
FPS = 24000 / 1001
A, B = int(sys.argv[1]), int(sys.argv[2])
os.makedirs('/tmp/fr', exist_ok=True)
fr = json.load(open(W + '/_work/zoom_v1.json'))
ARCH = (289, 516)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920',
                        '-r', '24000/1001', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16',
                        '-pix_fmt', 'yuv420p', '-video_track_timescale', '24000', f'/tmp/fr/v_{A:04d}.mp4'],
                       stdin=subprocess.PIPE)
if A >= ARCH[0] and B <= ARCH[1] + 1:
    cap = cv2.VideoCapture(W + '/_work/arch_v1.mp4')
    for i in range(A, B):
        ok, f = cap.read()
        enc.stdin.write(f.tobytes())
else:
    n = B - A
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(A - 0.5) / FPS:.6f}', '-i', MASTER,
                            '-map', '0:v:0', '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'bgr24', 'pipe:1',
                            '-map', '0:a:0', '-t', f'{n / FPS:.6f}', '-c:a', 'pcm_s24le', '-y', f'/tmp/fr/a_{A:04d}.wav'],
                           stdout=subprocess.PIPE)
    sz = 1728 * 3072 * 3
    for i in range(A, B):
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            raise SystemExit(f'short read at frame {i}')
        img = np.frombuffer(buf, np.uint8).reshape(3072, 1728, 3)
        smp = fr[i]
        if len(smp) == 1:
            s, tx, ty = smp[0]
            sig = 0.45 * np.sqrt(max(0.0, 1 / s ** 2 - 1))
            src = cv2.GaussianBlur(img, (0, 0), sig) if sig > 0.15 else img
            out = cv2.warpAffine(src, np.float32([[s, 0, tx], [0, s, ty]]), (1080, 1920),
                                 flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        else:
            step = max(1, len(smp) // 12)
            smp = smp[::step]
            acc = np.zeros((1920, 1080, 3), np.float32)
            for s, tx, ty in smp:
                acc += cv2.warpAffine(img, np.float32([[s, 0, tx], [0, s, ty]]), (1080, 1920),
                                      flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            out = (acc / len(smp) + 0.5).astype(np.uint8)
        enc.stdin.write(out.tobytes())
    dec.stdout.close(); dec.wait()
enc.stdin.close(); enc.wait()
print('done', A, B)
