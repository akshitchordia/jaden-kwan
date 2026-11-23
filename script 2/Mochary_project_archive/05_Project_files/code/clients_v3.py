"""Client file v3: real interview footage stacked as editorial panels, documentary-style name tags."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
W, H = 1080, 1920; FPS = 24000 / 1001
N0, N1 = 189, 262                                   # timeline frames (7.88s -> 10.93s)
T0 = N0 / FPS
VX, VY = 144, 66                                    # video rect inside the screen recording
PW, PH, GAP = 1080, 596, 16
P = [dict(src=S + 'cf3/alt.mkv', ss=6.00, crop=(230, 0, 1300, 722), t_in=7.88, t_name=8.20, name='Sam Altman', role='CEO, OPENAI', sat=0.5),
     dict(src=S + 'cf3/arm.mkv', ss=3.80, crop=(190, 0, 1300, 722), t_in=8.82, t_name=8.92, name='Brian Armstrong', role='CEO, COINBASE', sat=0.7),
     dict(src=S + 'cf3/ten.mkv', ss=5.30, crop=(600, 22, 940, 522), t_in=9.78, t_name=9.88, name='Vlad Tenev', role='CEO, ROBINHOOD', sat=0.32)]
def load(p):
    d = N1 / FPS - p['t_in'] + 0.2
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(p['ss']), '-t', str(d), '-i', p['src'], '-vf', 'fps=30', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 1080, 1920, 3)
for p in P: p['fr'] = load(p); print(p['name'], len(p['fr']), flush=True)

def cl(x): return min(1.0, max(0.0, x))
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def tops(n):
    tot = n * PH + (n - 1) * GAP; y0 = (H - tot) / 2
    return [y0 + i * (PH + GAP) for i in range(n)]
def grade(img, sat=0.55):
    f = img.astype(np.float32) / 255
    l = f @ np.array([0.299, 0.587, 0.114], np.float32)
    f = l[..., None] + (f - l[..., None]) * sat                      # pull the loud blue backdrops down
    f = f * np.array([1.03, 1.0, 0.95], np.float32)                   # warm
    f = np.clip((f - 0.03) / 0.95, 0, 1) ** 1.05
    return f
PV = None
def panel(p, t):
    k = min(len(p['fr']) - 1, int(round((t - p['t_in']) * 30)))
    fr = p['fr'][max(0, k)]
    x, y, w, h = p['crop']; z = 1 + 0.045 * eio((t - p['t_in']) / 3.0); w2, h2 = w / z, h / z
    cx, cy = x + w / 2, y + h * 0.45
    x0, y0 = cx - w2 / 2, max(0, cy - h2 * 0.45)
    M = np.float32([[PW / w2, 0, -(VX + x0) * PW / w2], [0, PH / h2, -(VY + y0) * PH / h2]])
    out = cv2.warpAffine(fr, M, (PW, PH), flags=cv2.INTER_LANCZOS4)
    global PV
    if PV is None:
        yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
        PV = np.clip(1 - 0.35 * (((xx - PW / 2) / PW) ** 2 + ((yy - PH / 2) / PH) ** 2) * 1.6, 0, 1)[..., None]
    return grade(out, p['sat']) * PV
F_NAME = ImageFont.truetype(S + 'fd/newsreader-600.ttf', 60); F_ROLE = ImageFont.truetype(S + 'fd/inter-600.ttf', 24)
def tag_layer(p):
    im = Image.new('L', (PW, PH), 0); d = ImageDraw.Draw(im)
    d.text((64, PH - 74), p['name'], font=F_NAME, fill=255, anchor='ls')
    x = 66
    for ch in p['role']: d.text((x, PH - 36), ch, font=F_ROLE, fill=170, anchor='ls'); x += F_ROLE.getlength(ch) + 24 * 0.16
    return np.asarray(im).astype(np.float32) / 255
for p in P: p['tag'] = tag_layer(p)
SHADE = np.clip((np.arange(PH, dtype=np.float32) - PH * 0.55) / (PH * 0.45), 0, 1)[:, None, None] ** 1.4 * 0.62
ACC = np.array([0.98, 0.47, 0.20], np.float32); INK = np.array([1.0, 0.965, 0.915], np.float32); BG = np.array([0.05, 0.047, 0.044], np.float32)
rng = np.random.default_rng(9); GR = [rng.normal(0, 0.022, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]

def render(n):
    t = n / FPS; img = np.empty((H, W, 3), np.float32); img[:] = BG
    vis = [p for p in P if t >= p['t_in']]; nv = len(vis)
    # layout: slots for nv panels; the stack glides from the previous layout
    cur, prev = tops(nv), tops(max(1, nv - 1))
    u = eoq((t - vis[-1]['t_in']) / 0.55)
    for i, p in enumerate(vis):
        new = i == nv - 1
        if new and nv > 1: y = (1 - u) * (H + 40) + u * cur[i]
        elif new: y = (1 - u) * (cur[i] + 140) + u * cur[i]
        else: y = (1 - u) * prev[i] + u * cur[i]
        pan = panel(p, t)
        pan = pan * (1 - SHADE)                                       # gentle floor shade for the name
        a_in = eoq((t - p['t_in']) / 0.25) if nv == 1 or not new else 1.0
        # name tag: text rises out of a mask line, accent bar grows first
        dt = t - p['t_name']
        if dt > 0:
            bar = eoq(dt / 0.25); bh = int(96 * bar)
            if bh > 0: pan[PH - 34 - bh:PH - 34, 40:44] = ACC
            r = eoq((dt - 0.06) / 0.45)
            if r > 0:
                tg = p['tag']; off = int(round((1 - r) * 34))
                L = np.zeros_like(tg); L[:PH - off] = tg[off:]
                L[PH - 28:] = 0                                        # mask line: text emerges from under it
                pan = pan * (1 - L[..., None] * r) + INK * L[..., None] * r
        y0 = int(round(y)); ys, ye = max(0, y0), min(H, y0 + PH)
        if ye > ys: img[ys:ye] = img[ys:ye] * (1 - a_in) + pan[ys - y0:ye - y0] * a_in
    # quick exposure kiss on each arrival, grain
    fl = sum(0.35 * math.exp(-(t - p['t_in']) / 0.05) for p in vis)
    img = img * (1 + fl)
    g = cv2.resize(GR[(n // 2) % 6], (W, H), interpolation=cv2.INTER_LINEAR)
    img = img + g[..., None] * (0.6 + 0.4 * img)
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
