"""Coaching footage B-rolls: vertical crops of the interview recordings, same treatment as client file v4."""
import sys, math, subprocess, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/moch')
from kit import W, H, FPS, cl, eio
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
CLIPS = {
 'C1_stage':  dict(src=S + 'cf3/n1.mkv', ss=9.00, rect=(144, 66, 961), fx=770, t0=19.23, t1=21.30, sat=0.55),
 'C2_webcam': dict(src=S + 'cf3/n2.mkv', ss=3.60, rect=(144, 66, 961), fx=830, t0=21.30, t1=24.25, sat=0.8),
 'C3_client': dict(src=S + 'cf3/n3.mkv', ss=5.10, rect=(144, 70, 940), fx=410, t0=36.20, t1=38.55, sat=0.75),
}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - 0.28 * (((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2) * 2.2, 0, 1)[..., None]
rng = np.random.default_rng(9); GR = [rng.normal(0, 0.02, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]

def render_clip(name, out):
    c = CLIPS[name]; VX, VY, VH = c['rect']; CW = VH * 9 / 16
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(c['ss']), '-t', str(c['t1'] - c['t0'] + 0.2), '-i', c['src'], '-vf', 'fps=30', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    frs = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8).reshape(-1, 1080, 1920, 3)
    n0, n1 = int(round(c['t0'] * FPS)), int(round(c['t1'] * FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    dur = c['t1'] - c['t0']
    for n in range(n0, n1):
        t = n / FPS; lt = t - c['t0']
        fr = frs[min(len(frs) - 1, max(0, int(round(lt * 30))))]
        z = 1.0 + 0.07 * eio(lt / dur)
        w, h = CW / z, VH / z; x0 = VX + c['fx'] - w / 2; y0 = VY + (VH - h) * 0.3
        M = np.float32([[W / w, 0, -x0 * W / w], [0, H / h, -y0 * H / h]])
        img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LANCZOS4).astype(np.float32) / 255
        bl = cv2.GaussianBlur(img, (0, 0), 1.6); img = np.clip(img + (img - bl) * 0.6, 0, 1)
        l = img @ np.array([0.299, 0.587, 0.114], np.float32)
        img = l[..., None] + (img - l[..., None]) * c['sat']
        img = np.clip((img * np.array([1.03, 1.0, 0.95], np.float32) - 0.025) / 0.95, 0, 1) * VIG
        img = img * (1 + 0.55 * math.exp(-lt / 0.045))
        g = cv2.resize(GR[(n // 2) % 6], (W, H)); img = np.clip(img + g[..., None] * (0.5 + 0.5 * img), 0, 1)
        enc.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print(name, n0, n1, flush=True)
    return n0

if __name__ == '__main__':
    for name in sys.argv[1].split(','):
        c = CLIPS[name]; n0 = int(round(c['t0'] * FPS)); s, f = n0 // 24, n0 % 24
        render_clip(name, S + f'out/Mochary_{name}_in-0m{s:02d}s{f:02d}f.mp4')
