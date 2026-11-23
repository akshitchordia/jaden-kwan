"""Mochary reel – 'He's worked with Altman, Brian Armstrong, Vlad Tenev' as a client file (7.88–10.89 s).
Writes a 0–11.6 s preview: opening animation (Mochary_open_v1) + this sequence over the zoomed talking head."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
OPEN = S + 'out/Mochary_open_v1.mp4'; ZOOM = S + 'out/Mochary_zoom_v1.mp4'
W, H = 1080, 1920; FPS = 24000 / 1001
N_OUT = 278
MONO = S + 'fd/plexmono-500.ttf'; SERIF = S + 'fd/newsreader-600.ttf'

def cl(x): return min(1.0, max(0.0, x))
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)

# ------------------------------------------------------------------ cards
FX0, FY0, FW, FH = 70, 230, 940, 1180            # the file photo window
CARDS = [
    dict(src='cut/altman2_src.png', crop=(435, 0, 1155, 900), face=(620, 120, 355, 440), name='Sam Altman', role='CEO  ·  OPENAI', sat=0.55,
         t0=189 / FPS, tn=8.19, t1=212 / FPS, n=1),
    dict(src='cut/armstrong_src.jpg', crop=(365, 135, 1435, 1472), face=(655, 360, 495, 610), name='Brian Armstrong', role='CEO  ·  COINBASE', sat=0.25,
         t0=212 / FPS, tn=212 / FPS, t1=235 / FPS, n=2),
    dict(src='cut/tenev_src.jpg', crop=(27, 0, 1413, 1733), face=(320, 290, 680, 790), name='Vlad Tenev', role='CEO  ·  ROBINHOOD', sat=0.5,
         t0=235 / FPS, tn=235 / FPS, t1=262 / FPS, n=3),
]
for c in CARDS:
    im = cv2.cvtColor(cv2.imread(S + 'moch/' + c['src']), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    x0, y0, x1, y1 = c['crop']; im = im[y0:y1, x0:x1]
    k = 2 * FW / (x1 - x0)                                                     # sprite at 2x the window
    im = cv2.resize(im, (2 * FW, int(round((y1 - y0) * k))), interpolation=cv2.INTER_CUBIC if k > 1 else cv2.INTER_AREA)
    if k > 1: im = np.clip(im + (im - cv2.GaussianBlur(im, (0, 0), 2.2)) * 0.55, 0, 1)
    g = im @ np.array([0.299, 0.587, 0.114], np.float32)
    im = g[..., None] + (im - g[..., None]) * c['sat']                              # unify three very different stage colours
    im = np.clip((im - 0.04) * 1.12, 0, 1) ** 1.08
    c['img'] = im.astype(np.float32); c['k'] = k
    fx, fy, fw, fh = c['face']; c['fbox'] = ((fx - x0) * k, (fy - y0) * k, fw * k, fh * k)   # face box in sprite px

def txt_layer(txt, font, size, x, y, track=0.0, anchor='ls', upto=None):
    f = ImageFont.truetype(font, size); im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    chars = txt if upto is None else txt[:upto]
    if anchor == 'rs':
        tot = sum(f.getlength(ch) for ch in txt) + track * size * (len(txt) - 1); x = x - tot
    for ch in chars:
        d.text((x, y), ch, font=f, fill=255, anchor='ls'); x += f.getlength(ch) + track * size
    return np.asarray(im).astype(np.float32) / 255

# static chrome
HEAD = txt_layer('CLIENT FILE', MONO, 24, 72, 152, 0.18)
CHROME = np.zeros((H, W), np.float32)
cv2.rectangle(CHROME, (FX0, FY0), (FX0 + FW, FY0 + FH), 0.22, 1, cv2.LINE_AA)
for (cx, cy, dx, dy) in [(FX0, FY0, 1, 1), (FX0 + FW, FY0, -1, 1), (FX0, FY0 + FH, 1, -1), (FX0 + FW, FY0 + FH, -1, -1)]:
    cv2.line(CHROME, (cx, cy), (cx + 26 * dx, cy), 0.9, 2, cv2.LINE_AA); cv2.line(CHROME, (cx, cy), (cx, cy + 26 * dy), 0.9, 2, cv2.LINE_AA)
NUMS = {n: txt_layer(f'0{n} / 03', MONO, 24, 1008, 152, 0.18, anchor='rs') for n in (1, 2, 3)}
NAMES = {c['n']: txt_layer(c['name'], SERIF, 98, 70, 1548, -0.02) for c in CARDS}
ROLES = {c['n']: [txt_layer(c['role'], MONO, 28, 74, 1608, 0.16, upto=u) for u in range(len(c['role']) + 1)] for c in CARDS}
TAGS = {c['n']: txt_layer(f'CLIENT 0{c["n"]}', MONO, 21, 0, 40, 0.16) for c in CARDS}

def glow_of(a):
    small = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, H)) * wt
    return g
GCOL = np.array([1.0, 0.98, 0.95], np.float32)
# halftone print texture (TBH colour mode)
CELL = 7.0; ang = math.radians(45)
Yg, Xg = np.mgrid[0:H, 0:W].astype(np.float32)
u_ = (Xg * math.cos(ang) + Yg * math.sin(ang)) / CELL; v_ = (-Xg * math.sin(ang) + Yg * math.cos(ang)) / CELL
DIST = np.sqrt((u_ - np.floor(u_) - 0.5) ** 2 + (v_ - np.floor(v_) - 0.5) ** 2).astype(np.float32)
rng = np.random.default_rng(4)
def _n(sig, amp): n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32); return cv2.resize(cv2.GaussianBlur(n, (0, 0), sig), (W, H)) * amp
FIBER = _n(3, 0.035) + _n(0.6, 0.02)
GRAINS = [rng.normal(0, 0.018, (H, W)).astype(np.float32) for _ in range(6)]
VIGN = np.clip(1 - 0.16 * (((Xg - W / 2) / (W * 0.7)) ** 2 + ((Yg - H / 2) / (H * 0.7)) ** 2), 0.82, 1)[..., None]
def halftone(f, n):
    L = cv2.GaussianBlur(f @ np.array([0.299, 0.587, 0.114], np.float32), (0, 0), CELL * 0.32)
    L = np.clip(L, 0, 1) ** 0.75; r = 0.76 * np.sqrt(1 - L)
    ink = cv2.GaussianBlur(np.clip((r - DIST) * CELL * 0.9 + 0.5, 0, 1), (0, 0), 0.45)
    tex = (1 + FIBER + GRAINS[(n // 2) % 6])[..., None]
    out = f * (1 - 0.42 * ink[..., None]); out = out * (0.93 + 0.07 * tex) * np.array([1.0, 0.985, 0.95], np.float32) + 0.012
    return np.clip(out * VIGN, 0, 1)
# window vignette: the photo falls off into the black at its edges and bottom
wy, wx = np.mgrid[0:FH, 0:FW].astype(np.float32)
WIN_V = (np.clip(1 - 0.55 * (((wx - FW / 2) / (FW * 0.62)) ** 2 + ((wy - FH * 0.42) / (FH * 0.62)) ** 2), 0.25, 1) *
         (1 - 0.55 * np.clip((wy - FH * 0.62) / (FH * 0.38), 0, 1) ** 1.5))[..., None]

def card_frame(c, t):
    d = t - c['t0']; dur = c['t1'] - c['t0']
    # slow push-in on the face inside the window
    z = 1.0 + 0.06 * eio(d / dur)
    fx, fy, fw, fh = c['fbox']; fcx, fcy = fx + fw / 2, fy + fh / 2
    s = z / 2                                                                # sprite is 2x
    tx, ty = FW / 2, FH * 0.42                                               # face centre lands here at z=1 … then drifts as we push
    ox = FW / 2 - s * fcx * (1.0 if z == 1 else 1.0); oy = (fcy * 0.5) * (1 - 0) - s * fcy + (fcy * 0.5 - fcy * 0.5)
    # anchor: keep the face centre fixed in the window while zooming
    base_s = 0.5; fc_win = (fcx * base_s, fcy * base_s)
    M = np.float32([[s, 0, fc_win[0] - s * fcx], [0, s, fc_win[1] - s * fcy]])
    win = cv2.warpAffine(c['img'], M, (FW, FH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    sig = 4.5 * math.exp(-d / 0.05)
    if sig > 0.3: win = cv2.GaussianBlur(win, (0, 0), sig)
    win = win * WIN_V * (1 + 0.55 * math.exp(-d / 0.06))                   # cut lands with a short exposure flash
    fr = np.zeros((H, W, 3), np.float32); fr[FY0:FY0 + FH, FX0:FX0 + FW] = np.clip(win, 0, 1)
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    # chrome (always on), number flashes on each new card
    core = np.maximum(core, CHROME)
    # tracking box: locks onto the face (screen coords)
    bx, by, bw, bh = (fx * s + fc_win[0] - s * fcx + FX0, fy * s + fc_win[1] - s * fcy + FY0, fw * s, fh * s)
    p = eoq(d / 0.32); grow = 1.45 - 0.45 * p; offx, offy = 46 * (1 - p), -34 * (1 - p)
    cx, cy = bx + bw / 2 + offx, by + bh / 2 + offy; hw, hh = bw * grow / 2, bh * grow / 2
    L = np.zeros((H, W), np.float32); a = cl(d / 0.06)
    x0, y0, x1, y1 = cx - hw, cy - hh, cx + hw, cy + hh; arm = min(hw, hh) * 0.42
    P = lambda x, y: (int(round(x * 8)), int(round(y * 8)))
    for (X, Y, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        cv2.line(L, P(X, Y), P(X + arm * dx, Y), 1.0, 3, cv2.LINE_AA, shift=3); cv2.line(L, P(X, Y), P(X, Y + arm * dy), 1.0, 3, cv2.LINE_AA, shift=3)
    cv2.rectangle(L, P(x0, y0), P(x1, y1), 0.22, 1, cv2.LINE_AA, shift=3)
    for (X, Y, dx, dy) in [((x0 + x1) / 2, y0, 0, 1), ((x0 + x1) / 2, y1, 0, -1), (x0, (y0 + y1) / 2, 1, 0), (x1, (y0 + y1) / 2, -1, 0)]:
        cv2.line(L, P(X, Y), P(X + 14 * dx, Y + 14 * dy), 0.8, 2, cv2.LINE_AA, shift=3)
    lock = 1 + 2.5 * math.exp(-(d - 0.32) / 0.09) if d >= 0.32 else 1.0
    core = np.maximum(core, L * a * 0.95); gin += L * a * 0.6 * lock
    # tag above the box (after lock)
    if d >= 0.30:
        tg = TAGS[c['n']]; ta = cl((d - 0.30) / 0.06)
        Mt = np.float32([[1, 0, x0], [0, 1, y0 - 54]]); tl = cv2.warpAffine(tg, Mt, (W, H)) * ta
        core = np.maximum(core, tl * 0.9); gin += tl * (0.4 + 2.5 * math.exp(-(d - 0.30) / 0.08))
    # name (flash-bloom, same language as the captions) + role typed in
    dn = t - c['tn']
    if dn >= 0:
        Ln = NAMES[c['n']]; sg = 6 * math.exp(-dn / 0.06)
        an = np.clip(cv2.GaussianBlur(Ln, (0, 0), sg) * (1 + sg * 0.3), 0, 1) if sg > 0.25 else Ln
        an = an * cl(dn / 0.05); core = np.maximum(core, an); gin += an * (1 + 7 * math.exp(-dn / 0.085))
        k = int(cl((dn - 0.08) / (0.018 * len(c['role']))) * len(c['role'])) if dn > 0.08 else 0
        rl = ROLES[c['n']][k] * 0.62; core = np.maximum(core, rl); gin += rl * 0.4
    return fr, core, gin

def render(t, n):
    c = [c for c in CARDS if c['t0'] - 1e-6 <= t < c['t1'] - 1e-6][0]
    fr, core, gin = card_frame(c, t)
    g = glow_of(gin); fr = 1 - (1 - fr) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
    fr = fr * (1 - core[..., None]) + core[..., None]
    return halftone(np.clip(fr, 0, 1).astype(np.float32), n)

if __name__ == '__main__':
    out = sys.argv[1]
    d1 = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', OPEN, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    d2 = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ZOOM, '-frames:v', str(N_OUT), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-i', ZOOM, '-map', '0:v', '-map', '1:a', '-t', str(N_OUT / FPS), '-c:v', 'libx264', '-crf', '15', '-preset', 'medium',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(N_OUT):
        z = d2.stdout.read(W * H * 3); o = d1.stdout.read(W * H * 3) if n < 192 else b''
        t = n / FPS
        if CARDS[0]['t0'] - 1e-6 <= t < CARDS[-1]['t1'] - 1e-6:
            fr = (render(t, n) * 255 + 0.5).astype(np.uint8).tobytes()
        else:
            fr = o if len(o) == W * H * 3 else z
        enc.stdin.write(fr)
    enc.stdin.close(); enc.wait(); print('done')
