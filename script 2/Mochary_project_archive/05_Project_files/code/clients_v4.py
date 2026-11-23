"""Client file v4: full-frame vertical crops of the real footage, quick cuts, flash-bloom name glow."""
import sys, math, subprocess, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/moch')
from kit import W, H, FPS, SERIF, text, glow_of, cl, eio, eoq, INK
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
N0, N1 = 189, 262
VX, VY, VH = 144, 66, 961; CW = VH * 9 / 16
INTER = S + 'fd/inter-600.ttf'
P = [dict(src=S + 'cf3/alt.mkv', ss=6.00, fx=880, t_in=7.88, t_name=8.19, name='Sam Altman', role='CEO, OPENAI', sat=0.6),
     dict(src=S + 'cf3/arm.mkv', ss=3.80, fx=845, t_in=8.84, t_name=8.86, name='Brian Armstrong', role='CEO, COINBASE', sat=0.75),
     dict(src=S + 'cf3/ten.mkv', ss=5.30, fx=880, t_in=9.80, t_name=9.82, name='Vlad Tenev', role='CEO, ROBINHOOD', sat=0.45)]
for i, p in enumerate(P): p['t_out'] = P[i + 1]['t_in'] if i + 1 < len(P) else N1 / FPS + 0.1
def load(p):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(p['ss']), '-t', str(p['t_out'] - p['t_in'] + 0.2), '-i', p['src'], '-vf', 'fps=30', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.uint8).reshape(-1, 1080, 1920, 3)
for p in P: p['fr'] = load(p)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - 0.28 * (((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2) * 2.2, 0, 1)[..., None]
SHADE = (np.clip((yy - H * 0.58) / (H * 0.42), 0, 1) ** 1.3 * 0.72)[..., None]
rng = np.random.default_rng(9); GR = [rng.normal(0, 0.02, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
GCOL = np.array([1.0, 0.98, 0.95], np.float32)

def shot(p, t):
    k = min(len(p['fr']) - 1, max(0, int(round((t - p['t_in']) * 30))))
    fr = p['fr'][k]
    z = 1.0 + 0.06 * eio((t - p['t_in']) / 1.2)                      # slow push-in
    w, h = CW / z, VH / z; x0 = VX + p['fx'] - w / 2; y0 = VY + (VH - h) * 0.35
    M = np.float32([[W / w, 0, -x0 * W / w], [0, H / h, -y0 * H / h]])
    img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    bl = cv2.GaussianBlur(img, (0, 0), 1.6); img = np.clip(img + (img - bl) * 0.6, 0, 1)   # recover detail after the 2x crop
    l = img @ np.array([0.299, 0.587, 0.114], np.float32)
    img = l[..., None] + (img - l[..., None]) * p['sat']
    img = np.clip((img * np.array([1.03, 1.0, 0.95], np.float32) - 0.025) / 0.95, 0, 1)
    return img * VIG

def name_layers(p, t):
    """flash-bloom: each letter arrives as a blurred hot blob, snaps sharp, glow settles"""
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    dt0 = t - p['t_name']
    if dt0 < 0: return core, gin
    from kit import font
    f = font(SERIF, 112); x = (W - f.getlength(p['name'])) / 2; base = 1560; k = 0
    for ch in p['name']:
        if ch != ' ':
            dt = dt0 - k * 0.028; k += 1
            if dt > 0:
                L = text(ch, SERIF, 112, x, base, 'ls')
                s = 7.0 * math.exp(-dt / 0.07)
                a = L if s < 0.25 else np.clip(cv2.GaussianBlur(L, (0, 0), s) * (1 + s * 0.3), 0, 1)
                a = a * cl(dt / 0.05); core = np.maximum(core, a); gin += a * (1.3 + 8 * math.exp(-dt / 0.11))
        x += f.getlength(ch)
    dr = dt0 - 0.22                                                     # role line blooms in after the name
    if dr > 0:
        L = text(p['role'], INTER, 30, W / 2, 1625, 'ms', 0.24)
        s = 5.0 * math.exp(-dr / 0.06); a = L if s < 0.25 else np.clip(cv2.GaussianBlur(L, (0, 0), s) * (1 + s * 0.3), 0, 1)
        a = a * cl(dr / 0.05) * 0.78; core = np.maximum(core, a); gin += a * (0.6 + 5 * math.exp(-dr / 0.09))
    return core, gin

def render(n):
    t = n / FPS; p = next(q for q in P if q['t_in'] <= t < q['t_out'] + 1e-6) if t >= P[0]['t_in'] else P[0]
    img = shot(p, t)
    img = img * (1 - SHADE * cl((t - p['t_name'] + 0.1) / 0.2))      # floor darkens as the name arrives
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    for j in range(3):                                                  # sub-frame sampling for smooth bloom
        c_, g_ = name_layers(p, t + (j - 1) / 3 * 0.5 / FPS); core += c_ / 3; gin += g_ / 3
    if gin.max() > 0.002:
        g = glow_of(gin); img = 1 - (1 - img) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
        img = img * (1 - core[..., None]) + core[..., None] * INK
    img = img * (1 + 0.55 * math.exp(-(t - p['t_in']) / 0.045))       # flash on every cut
    g = cv2.resize(GR[(n // 2) % 6], (W, H)); img = img + g[..., None] * (0.5 + 0.5 * img)
    return np.clip(img, 0, 1)

if __name__ == '__main__':
    out = sys.argv[1]
    if out.endswith('.jpg'):
        fs = [int(x) for x in sys.argv[2].split(',')]
        tiles = [cv2.resize((render(f) * 255).astype(np.uint8), (360, 640), interpolation=cv2.INTER_AREA) for f in fs]
        cv2.imwrite(out, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR)); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(N0, N1): enc.stdin.write((render(n) * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print('done', N1 - N0)
