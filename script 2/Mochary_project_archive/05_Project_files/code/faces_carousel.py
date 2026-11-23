"""'It finds the people…' — three stacked 3D carousels of founder portraits that spin down and lock onto the people it finds."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
U = '/root/.claude/uploads/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/'
W, H = 1080, 1920; FPS = 24000 / 1001
N0 = 826; NF = 48; T0 = N0 / FPS
# (file, face-x frac, face-y frac, crop-height frac)
SRC = [('17e8f370-image.webp', .50, .45, 1.0), ('8c68b52d-image.jpg', .44, .40, .72), ('5c241d22-image.webp', .48, .46, 1.0),
       ('019bdfa6-image.jpg', .47, .24, .48), ('b9b48272-image.jpg', .52, .34, .62), ('4e941bc2-image.webp', .48, .30, .78),
       ('79d61dd9-image.webp', .40, .47, 1.0), ('e5ca6707-image.webp', .56, .50, 1.0), ('b6477c73-image.webp', .50, .45, 1.0),
       ('77262532-image.webp', .50, .45, 1.0), ('a496b34b-image.webp', .74, .44, 1.0), ('893fb79b-image.webp', .45, .44, 1.0),
       ('7db9b87d-image.webp', .45, .42, 1.0)]
CW, CH = 600, 800                                                   # card texture size
def card_tex(f, fx, fy, hf):
    im = np.asarray(Image.open(U + f).convert('RGB')).astype(np.float32) / 255; h, w = im.shape[:2]
    ch = h * hf; cw = ch * 3 / 4
    if cw > w: cw = w; ch = cw * 4 / 3
    x0 = min(max(0, fx * w - cw / 2), w - cw); y0 = min(max(0, fy * h - ch * 0.42), h - ch)
    c = im[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    c = cv2.resize(c, (CW, CH), interpolation=cv2.INTER_AREA if c.shape[0] > CH else cv2.INTER_CUBIC)
    l = c @ np.array([.299, .587, .114], np.float32); c = l[..., None] + (c - l[..., None]) * 0.62     # unify the grades
    c = np.clip((c * np.array([1.03, 1.0, 0.95], np.float32) - 0.02) / 0.96, 0, 1)
    yy = np.linspace(0, 1, CH)[:, None, None]; c = c * (1 - 0.35 * np.clip((yy - 0.6) / 0.4, 0, 1))      # floor shade
    return c
TEX = [card_tex(*s) for s in SRC]
MASK = np.zeros((CH, CW), np.float32); cv2.rectangle(MASK, (0, 0), (CW - 1, CH - 1), 1.0, -1)
RAD = 34; MASK[:] = 0; cv2.rectangle(MASK, (RAD, 0), (CW - RAD, CH), 1, -1); cv2.rectangle(MASK, (0, RAD), (CW, CH - RAD), 1, -1)
for cx, cy in ((RAD, RAD), (CW - RAD, RAD), (RAD, CH - RAD), (CW - RAD, CH - RAD)): cv2.circle(MASK, (cx, cy), RAD, 1, -1, cv2.LINE_AA)
EDGE = np.clip(MASK - cv2.erode(MASK, np.ones((5, 5), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0), 0, 1)
EDGE2 = cv2.GaussianBlur(np.clip(MASK - cv2.erode(MASK, np.ones((15, 15), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0), 0, 1), (0, 0), 1.2)
# ---- rings
NS = 9; R = 470; CARD_W, CARD_H = 250, 333
ROWS = [dict(y=-405, dir=1, order=[0, 5, 9, 2, 11, 7, 3, 12, 8]), dict(y=0, dir=-1, order=[4, 10, 1, 6, 0, 8, 2, 12, 5]),
        dict(y=405, dir=1, order=[3, 7, 11, 1, 9, 6, 10, 4, 8])]
SPIN = 2.6 * (2 * math.pi / NS)                                       # slots travelled before locking
T_LOCK = 1.30
def cl(x): return min(1.0, max(0.0, x))
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def ang_of(t, row, i):
    u = 1 - (1 - cl(t / T_LOCK)) ** 4                                # fast in, long ease out
    stag = {0: 0.06, 1: 0.0, 2: 0.12}[ROWS.index(row)]
    u = 1 - (1 - cl((t - 0) / (T_LOCK + stag))) ** 4
    return i * 2 * math.pi / NS + row['dir'] * SPIN * (u - 1)
def cam(t):
    u = eoc(t / 1.1); D = 2150 - 600 * u - 110 * (0.5 - 0.5 * math.cos(math.pi * cl((t - 1.0) / 1.1))); tilt = 0.10 * (1 - u)
    return D, tilt
F = 1550
def project(P, D, tilt):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    y2 = y * math.cos(tilt) - z * math.sin(tilt); z2 = y * math.sin(tilt) + z * math.cos(tilt)
    s = F / (D - z2); return np.stack([540 + x * s, 960 + y2 * s], -1), D - z2
BG = None
def frame_layers(t):
    D, tilt = cam(t)
    items = []
    for row in ROWS:
        for i, k in enumerate(row['order']):
            a = ang_of(t, row, i); c, s_ = math.cos(a), math.sin(a)
            if c < -0.35: continue
            cx, cz = R * s_, R * c; tx, tz = c, -s_                     # card faces outward, tangent along ring
            hw, hh = CARD_W / 2, CARD_H / 2
            P = np.array([[cx - tx * hw, row['y'] - hh, cz - tz * hw], [cx + tx * hw, row['y'] - hh, cz + tz * hw],
                          [cx + tx * hw, row['y'] + hh, cz + tz * hw], [cx - tx * hw, row['y'] + hh, cz - tz * hw]], np.float32)
            Q, dep = project(P, D, tilt)
            front = abs(math.atan2(s_, c)) < 0.12
            if front and t > T_LOCK:
                pop = 70 * eoq((t - T_LOCK) / 0.35); P[:, 2] += pop
                Q, dep = project(P, D, tilt)
            items.append((float(dep.mean()), Q, k, c, front))
    items.sort(key=lambda r: -r[0])
    return items
def render_sub(t):
    img = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W), np.float32); G = np.zeros((H, W), np.float32)
    lock = t - T_LOCK
    for dep, Q, k, c, front in items_cache(t):
        x0, y0 = np.floor(Q.min(0)).astype(int) - 2; x1, y1 = np.ceil(Q.max(0)).astype(int) + 2
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 <= x0 or y1 <= y0: continue
        src = np.float32([[0, 0], [CW, 0], [CW, CH], [0, CH]]); M = cv2.getPerspectiveTransform(src, np.float32(Q - [x0, y0]))
        sz = (x1 - x0, y1 - y0)
        tex = cv2.warpPerspective(TEX[k], M, sz, flags=cv2.INTER_LINEAR); m = cv2.warpPerspective(MASK, M, sz, flags=cv2.INTER_LINEAR)
        e = cv2.warpPerspective(EDGE, M, sz, flags=cv2.INTER_LINEAR); e2 = cv2.warpPerspective(EDGE2, M, sz, flags=cv2.INTER_LINEAR)
        fog = 0.35 + 0.65 * cl((c + 0.35) / 1.35) ** 1.4               # cards round the back sink into the dark
        dim = 1.0
        if lock > 0: dim = 1 - 0.68 * eoc(lock / 0.25) if not front else 1.0
        col = tex * fog * dim + e[..., None] * 0.18 * fog
        if front and lock > 0:
            on = eoq(lock / 0.18); col = col * (1 + 0.5 * math.exp(-lock / 0.08))
            col = col * (1 - e2[..., None] * on) + e2[..., None] * on * np.array([0.98, 0.47, 0.2], np.float32) * 1.3
            G[y0:y1, x0:x1] += e2 * on * (1.6 + 4 * math.exp(-lock / 0.15))
        sl = (slice(y0, y1), slice(x0, x1))
        img[sl] = img[sl] * (1 - m[..., None]) + col * m[..., None]; A[sl] = np.maximum(A[sl], m)
    return img, A, G
_ic = {}
def items_cache(t):
    if t not in _ic: _ic.clear(); _ic[t] = frame_layers(t)
    return _ic[t]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BGI = (np.array([14, 13, 12], np.float32) / 255) * (1 + 0.8 * np.exp(-(((xx - 540) / 600) ** 2 + ((yy - 960) / 900) ** 2)))[..., None]
VIG = np.clip(1 - 0.3 * (((xx - 540) / 1080) ** 2 + ((yy - 960) / 1920) ** 2) * 3, 0, 1)[..., None]
rng = np.random.default_rng(5); GR = [rng.normal(0, 0.017, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def glow(a):
    sm = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 4) * 0.8 + cv2.GaussianBlur(a, (0, 0), 12) * 0.6
    for s_, wt in ((8, 0.5), (22, 0.3)): g += cv2.resize(cv2.GaussianBlur(sm, (0, 0), s_), (W, H)) * wt
    return g
def render(n):
    t = n / FPS - T0; SUB = 5 if t < 0.9 else 2
    acc = np.zeros((H, W, 3), np.float32); aA = np.zeros((H, W), np.float32); aG = np.zeros((H, W), np.float32)
    for j in range(SUB):
        tt = t + (j - (SUB - 1) / 2) / SUB * 0.5 / FPS
        i_, a_, g_ = render_sub(tt); acc += i_ / SUB; aA += a_ / SUB; aG += g_ / SUB
    img = BGI * (1 - aA[..., None]) + acc
    # soft floor reflection of the whole stack
    gg = glow(aG)[..., None] * np.array([1.0, 0.55, 0.3], np.float32)
    img = 1 - (1 - img) * (1 - np.clip(gg * 0.6, 0, 1))
    img = img * VIG * (1 + 0.55 * math.exp(-t / 0.05))
    gr = cv2.resize(GR[(n // 2) % 6], (W, H)); img = img + gr[..., None] * (0.6 + 0.4 * img)
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
