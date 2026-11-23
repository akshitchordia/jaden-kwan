"""'It finds the people…' v2 — launch-film style coverflow: spring-driven glide, parallax inside cards, depth of field, floor reflection, soft lock on one face."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
U = '/root/.claude/uploads/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/'
W, H = 1080, 1920; FPS = 24000 / 1001
N0, NF = 826, 72; T0 = N0 / FPS
SRC = [('17e8f370-image.webp', .50, .45, 1.0), ('b9b48272-image.jpg', .52, .34, .62), ('5c241d22-image.webp', .48, .46, 1.0),
       ('79d61dd9-image.webp', .40, .47, 1.0), ('019bdfa6-image.jpg', .47, .24, .48), ('e5ca6707-image.webp', .56, .50, 1.0),
       ('8c68b52d-image.jpg', .44, .40, .72), ('77262532-image.webp', .50, .45, 1.0), ('4e941bc2-image.webp', .48, .30, .78),
       ('b6477c73-image.webp', .50, .45, 1.0), ('a496b34b-image.webp', .74, .44, 1.0), ('893fb79b-image.webp', .45, .44, 1.0),
       ('7db9b87d-image.webp', .45, .42, 1.0)]
HERO = 6                                                              # Vlad Tenev ends centred
CW, CH, MARG = 600, 800, 70                                           # card texture + parallax margin
def tex(f, fx, fy, hf):
    im = np.asarray(Image.open(U + f).convert('RGB')).astype(np.float32) / 255; h, w = im.shape[:2]
    ch = h * hf; cw = ch * (CW + 2 * MARG) / CH
    if cw > w: cw = w; ch = cw * CH / (CW + 2 * MARG)
    x0 = min(max(0, fx * w - cw / 2), w - cw); y0 = min(max(0, fy * h - ch * 0.42), h - ch)
    c = im[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    c = cv2.resize(c, (CW + 2 * MARG, CH), interpolation=cv2.INTER_AREA if c.shape[0] > CH else cv2.INTER_CUBIC)
    l = c @ np.array([.299, .587, .114], np.float32); c = l[..., None] + (c - l[..., None]) * 0.66
    c = np.clip((c * np.array([1.03, 1.0, 0.95], np.float32) - 0.02) / 0.96, 0, 1)
    yy = np.linspace(0, 1, CH)[:, None, None]; c = c * (1 - 0.30 * np.clip((yy - 0.62) / 0.38, 0, 1))
    return [c, cv2.GaussianBlur(c, (0, 0), 3), cv2.GaussianBlur(c, (0, 0), 7)]
TEX = [tex(*s) for s in SRC]
RAD = 40
MASK = np.zeros((CH, CW), np.float32); cv2.rectangle(MASK, (RAD, 0), (CW - RAD, CH), 1, -1); cv2.rectangle(MASK, (0, RAD), (CW, CH - RAD), 1, -1)
for cx, cy in ((RAD, RAD), (CW - RAD, RAD), (RAD, CH - RAD), (CW - RAD, CH - RAD)): cv2.circle(MASK, (cx, cy), RAD, 1, -1, cv2.LINE_AA)
RING = cv2.GaussianBlur(np.clip(MASK - cv2.erode(MASK, np.ones((13, 13), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0), 0, 1), (0, 0), 1.0)
RIM = np.clip(MASK - cv2.erode(MASK, np.ones((4, 4), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
# ---- motion: a damped spring glides the strip and settles on the hero with one soft overshoot
def simulate():
    dt = 1e-3; p, v = HERO - 7.5, 7.5; w, z = 3.3, 0.82; out = []
    for i in range(int(3.2 / dt)):
        if i % 1 == 0: out.append(p)
        a = -w * w * (p - HERO) - 2 * z * w * v; v += a * dt; p += v * dt
    return np.array(out)
PS = simulate()
def P(t): return float(PS[min(len(PS) - 1, max(0, int(t * 1000)))])
def cl(x): return min(1.0, max(0.0, x))
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)
T_LOCK = 1.70
F = 2000.0; CY = 880
def layout(o):
    a = abs(o); sg = 1 if o >= 0 else -1
    X = sg * (585 * min(a, 1) + 520 * max(a - 1, 0))
    Z = -190 * (min(a, 1) ** 1.4) - 140 * max(a - 1, 0)
    th = -sg * 0.30 * math.sin(min(a, 1.3) / 1.3 * math.pi / 2)          # cards turn toward the lens as they arrive
    return X, Z, th
HW, HH = 262, 349
def quad(X, Z, th, D, hw=HW, hh=HH, Y=0.0):
    c, s = math.cos(th), math.sin(th)
    pts = [(X - hw * c, Y - hh, Z - hw * s), (X + hw * c, Y - hh, Z + hw * s), (X + hw * c, Y + hh, Z + hw * s), (X - hw * c, Y + hh, Z - hw * s)]
    return np.float32([[540 + x * F / (D - z), CY + y * F / (D - z)] for x, y, z in pts]), np.mean([D - z for _, _, z in pts])
def cards(t):
    p = P(t); D = F - 160 * eio((t - 1.2) / 1.8)                    # gentle push once it lands
    lock = t - T_LOCK; out = []
    for k in range(len(SRC)):
        for rep in (-13, 0, 13):
            o = (k + rep) - p
            if abs(o) > 2.4: continue
            X, Z, th = layout(o)
            hero = (k + rep) == HERO and lock > 0
            if hero: Z += 70 * eoc(lock / 0.45)
            Q, dep = quad(X, Z, th, D)
            out.append(dict(k=k, o=o, Q=Q, dep=dep, hero=hero, X=X, Z=Z, th=th, D=D))
    out.sort(key=lambda r: -r['dep'])
    return out
def warp(src, Q, x0, y0, sz):
    h, w = src.shape[:2]; M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(Q - [x0, y0]))
    return cv2.warpPerspective(src, M, sz, flags=cv2.INTER_LINEAR)
def draw(t):
    img = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32); G = np.zeros((H, W), np.float32)
    lock = t - T_LOCK
    for c in cards(t):
        a = abs(c['o']); lvl = 0 if a < 0.6 else (1 if a < 1.5 else 2)
        par = int(round(MARG - np.clip(c['o'], -1.3, 1.3) * MARG / 1.3))           # image slides inside the card
        tx = TEX[c['k']][lvl][:, par:par + CW]
        shade = 1.0 - 0.42 * cl((a - 0.1) / 1.4)
        if lock > 0 and not c['hero']: shade *= 1 - 0.55 * eoc(lock / 0.4)
        for refl in (True, False):                                  # glossy floor reflection first
            if refl:
                Qr, _ = quad(c['X'], c['Z'] + (70 * eoc(lock / 0.45) if c['hero'] else 0) * 0, c['th'], c['D'], Y=2 * HH + 18)
                Qr = Qr[[3, 2, 1, 0]]; Q = Qr
            else: Q = c['Q']
            x0, y0 = np.floor(Q.min(0)).astype(int) - 2; x1, y1 = np.ceil(Q.max(0)).astype(int) + 2
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            if x1 <= x0 or y1 <= y0: continue
            sz = (x1 - x0, y1 - y0)
            m = warp(MASK, Q, x0, y0, sz); col = warp(tx, Q, x0, y0, sz) * shade
            sl = (slice(y0, y1), slice(x0, x1))
            if refl:
                fade = np.clip(1 - (np.arange(y0, y1, dtype=np.float32) - (CY + (HH + 9) * F / c['D'])) / 230, 0, 1)[:, None] ** 2 * 0.16
                img[sl] += col * (m * fade)[..., None] * (1 - A[sl])[..., None]
                continue
            rim = warp(RIM, Q, x0, y0, sz)
            col = col + rim[..., None] * 0.22 * shade
            if c['hero']:
                on = eoc(lock / 0.3); r = warp(RING, Q, x0, y0, sz)
                col = col * (1 - r[..., None] * on) + r[..., None] * on * np.array([0.98, 0.47, 0.2], np.float32) * 1.25
                G[sl] += r * on * (1.4 + 3.5 * math.exp(-lock / 0.2))
            img[sl] = img[sl] * (1 - m[..., None]) + col * m[..., None]; A[sl] = np.maximum(A[sl], m)
    return img, A, G
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BG = (np.array([13, 12, 11], np.float32) / 255) * (1 + 1.1 * np.exp(-(((xx - 540) / 520) ** 2 + ((yy - 820) / 700) ** 2)))[..., None]
FLOOR = np.clip((yy - (CY + HH)) / 600, 0, 1)[..., None]
BG = BG * (1 - 0.35 * FLOOR)
VIG = np.clip(1 - 0.32 * (((xx - 540) / 1080) ** 2 + ((yy - 900) / 1920) ** 2) * 3, 0, 1)[..., None]
rng = np.random.default_rng(5); GR = [rng.normal(0, 0.016, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def glow(a):
    sm = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 5) * 0.8 + cv2.GaussianBlur(a, (0, 0), 14) * 0.6
    for s_, wt in ((9, 0.5), (24, 0.3)): g += cv2.resize(cv2.GaussianBlur(sm, (0, 0), s_), (W, H)) * wt
    return g
def render(n):
    t = n / FPS - T0
    vel = abs(P(t + 0.01) - P(t - 0.01)) / 0.02                        # cards per second
    SUB = int(min(8, max(1, round(vel * 0.9))))
    acc = np.zeros((H, W, 3), np.float32); aA = np.zeros((H, W), np.float32); aG = np.zeros((H, W), np.float32)
    for j in range(SUB):
        tt = t + ((j + 0.5) / SUB - 0.5) * 0.5 / FPS
        i_, a_, g_ = draw(tt); acc += i_ / SUB; aA += a_ / SUB; aG += g_ / SUB
    img = BG * (1 - aA[..., None]) + acc
    gg = glow(aG)[..., None] * np.array([1.0, 0.55, 0.3], np.float32)
    img = 1 - (1 - img) * (1 - np.clip(gg * 0.55, 0, 1))
    img = img * VIG * (1 + 0.45 * math.exp(-t / 0.06))
    img = img + cv2.resize(GR[(n // 2) % 6], (W, H))[..., None] * (0.6 + 0.4 * img)
    return np.clip(img, 0, 1)

if __name__ == '__main__':
    out = sys.argv[1]
    if out.endswith('.jpg'):
        fs = [int(x) for x in sys.argv[2].split(',')]
        tiles = [cv2.resize((render(f) * 255).astype(np.uint8), (360, 640), interpolation=cv2.INTER_AREA) for f in fs]
        cv2.imwrite(out, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR)); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(N0, N0 + NF): enc.stdin.write((render(n) * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print('done', N0, N0 + NF)
