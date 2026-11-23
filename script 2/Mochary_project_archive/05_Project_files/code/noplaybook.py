"""Mochary reel – 'and his whole playbook is online for anybody to read' (10.89–13.56 s).
His YouTube channel: start on his face + name, the page starts scrolling, then pulls back into an endless wall of free videos.
Writes the cumulative preview 0–14.2 s (open_v2 + this, over the zoomed talking head)."""
import sys, math, subprocess, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
SHOT = '/root/.claude/uploads/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/240a4cd0-image.png'
PREV = S + 'out/Mochary_open_v2.mp4'; ZOOM = S + 'out/Mochary_zoom_v1.mp4'
W, H = 1080, 1920; FPS = 24000 / 1001
F0, F1 = 261, 261
N_OUT = int(sys.argv[2]) if len(sys.argv) > 2 else 340; N_PREV = 278
def cl(x): return min(1.0, max(0.0, x))
def eiq(x): x = cl(x); return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2
def eic(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def ein(x): x = cl(x); return x ** 3
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5

src = cv2.cvtColor(cv2.imread(SHOT), cv2.COLOR_BGR2RGB)
# ------------------------------------------------------------------ world mosaic (1 px = 1 world unit)
CARDS = [src[471:912, 140:733], src[471:912, 756:1350], src[471:912, 1373:1967]]
CW, CH = 600, int(441 * 600 / 593)
CARDS = [cv2.resize(c, (CW, CH), interpolation=cv2.INTER_AREA) for c in CARDS]
def rounded(img, r=18):
    h, w = img.shape[:2]; m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for p in [(r, r), (w - r, r), (r, h - r), (w - r, h - r)]: cv2.circle(m, p, r, 255, -1, cv2.LINE_AA)
    return m
PX, PY = 660, CH + 70
HEADER = cv2.resize(src[15:300, 130:1270], (1260, int(285 * 1260 / 1140)), interpolation=cv2.INTER_CUBIC)
HX0, HY0 = -630, -HEADER.shape[0] - 90                  # header top-left (world), central page = columns k=-1,0
order = [0, 1, 2, 1, 2, 0, 2, 0, 1]
def build(sc, X0, X1, Y0, Y1):
    MW, MH = int((X1 - X0) * sc), int((Y1 - Y0) * sc)
    mos = np.zeros((MH, MW, 3), np.uint8); mos[:] = (17, 17, 18)
    cw, ch = int(CW * sc), int(CH * sc)
    cards = [cv2.resize(c, (cw, ch), interpolation=cv2.INTER_AREA) for c in CARDS]
    rm = rounded(cards[0], max(2, int(18 * sc)))[..., None] / 255.0
    for k in range(-6, 6):
        cx = 330 + PX * k; central = k in (-1, 0)
        for r in range(-9 if not central else 0, 18):
            cy = r * PY
            card = cards[order[(r * 3 + k * 2) % 9]]
            if not central: card = (card.astype(np.float32) * 0.42 + 6).astype(np.uint8)
            x, y = int((cx - CW / 2 - X0) * sc), int((cy - Y0) * sc)
            if x < 0 or y < 0 or x + cw > MW or y + ch > MH: continue
            mos[y:y + ch, x:x + cw] = (card * rm + mos[y:y + ch, x:x + cw] * (1 - rm)).astype(np.uint8)
    hd = cv2.resize(HEADER, (int(HEADER.shape[1] * sc), int(HEADER.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    hy, hx = int((HY0 - Y0) * sc), int((HX0 - X0) * sc)
    mos[hy:hy + hd.shape[0], hx:hx + hd.shape[1]] = hd
    return mos, sc, X0, Y0
LV_A = build(1.0, -1700, 1700, HY0 - 1400, 2700)                     # sharp, around the header
LV_B = build(0.36, -330 - 6 * PX, 330 + 5 * PX, -9 * PY - 200, 18 * PY)  # the whole wall
LV_C = (cv2.resize(LV_B[0], (LV_B[0].shape[1] // 2, LV_B[0].shape[0] // 2), interpolation=cv2.INTER_AREA), 0.18, LV_B[2], LV_B[3])
# link line in the header (for the highlight sweep): crop x 275–642, y 195 (crop px) -> world
LX0 = HX0 + 275 * 1260 / 1140; LX1 = HX0 + 642 * 1260 / 1140; LY = HY0 + 202 * 1260 / 1140

# ------------------------------------------------------------------ camera (time, scale, world cx, cy)
HC = (HX0 + 520, HY0 + 560)
CAM = [(F0 / FPS, 1.30, HC[0], HC[1], None), (11.45, 1.36, HC[0] + 10, HC[1] + 6, 'drift'),
       (12.15, 0.70, 0, 1150, 'in'), (13.20, 0.215, 0, 2350, 'io'), (F1 / FPS, 0.205, 0, 2450, 'drift')]
def cam(t):
    for a, b in zip(CAM, CAM[1:]):
        if t <= b[0]:
            u = (t - a[0]) / (b[0] - a[0]); kind = b[4]
            e = (u if kind == 'drift' else ein(u) * 0.55 + u * 0.45 if kind == 'in' else eoq(u))
            # 'in' leg accelerates into the scroll, 'io' leg keeps that speed and settles (out-quint) into the wall
            return tuple(a[i] + (b[i] - a[i]) * e for i in (1, 2, 3))
    return CAM[-1][1:4]

def view(t):
    s, cx, cy = cam(t)
    img, sc, X0, Y0 = LV_A if s > 0.5 else LV_B if s > 0.24 else LV_C
    ss = s / sc
    M = np.float32([[ss, 0, W / 2 - ss * (cx - X0) * sc], [0, ss, H / 2 - ss * (cy - Y0) * sc]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(17, 17, 18)).astype(np.float32) / 255, (s, cx, cy)

def glow_of(a):
    small = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, H)) * wt
    return g
GCOL = np.array([1.0, 0.98, 0.95], np.float32)
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
EDGE = np.clip(1 - 0.5 * (((Xg - W / 2) / (W * 0.75)) ** 2 + ((Yg - H / 2) / (H * 0.62)) ** 2), 0.35, 1)[..., None]

def render(t, n):
    c0, c1 = cam(t - 0.25 / FPS), cam(t + 0.25 / FPS)
    speed = abs(c0[1] - c1[1]) + abs(c0[2] - c1[2]) + abs(c0[0] - c1[0]) * 400
    ns = 1 if speed < 1 else 10 if speed > 60 else 6
    acc = np.zeros((H, W, 3), np.float32)
    for k in range(ns):
        tt = t + ((k + 0.5) / ns - 0.5) * 0.5 / FPS if ns > 1 else t
        img, _ = view(max(tt, F0 / FPS)); acc += img / ns
    s, cx, cy = cam(t)
    d = t - F0 / FPS
    fr = acc * EDGE * (1 + 0.5 * math.exp(-d / 0.06))                  # cut lands with a short exposure flash
    # glow sweep under the channel link (the playbook lives there)
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    p = eic((t - 11.02) / 0.32)
    if p > 0:
        x0 = (LX0 - cx) * s + W / 2; x1 = x0 + ((LX1 - LX0) * s) * p; y = (LY - cy) * s + H / 2
        fade = 1 - cl((t - 11.95) / 0.25)
        cv2.line(core, (int(x0 * 8), int(y * 8)), (int(x1 * 8), int(y * 8)), 1.0 * fade, max(2, int(3 * s)), cv2.LINE_AA, shift=3)
        gin += core * (1.2 + 4 * math.exp(-max(0, t - 11.34) / 0.1))
    g = glow_of(gin); fr = 1 - (1 - fr) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1)); fr = fr * (1 - core[..., None]) + core[..., None]
    return halftone(np.clip(fr, 0, 1).astype(np.float32), n)

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        tiles = []
        for t in [10.9, 11.0, 11.3, 11.5, 11.7, 11.9, 12.1, 12.4, 12.8, 13.2, 13.5]:
            fr = render(t, int(t * FPS)); im = cv2.resize((fr[..., ::-1] * 255).astype(np.uint8), (270, 480)); cv2.putText(im, f'{t}', (4, 18), 0, 0.55, (0, 255, 255), 1); tiles.append(im)
        tiles.append(np.zeros_like(tiles[0])); cv2.imwrite(S + 'moch/pb_still.jpg', np.vstack([np.hstack(tiles[:6]), np.hstack(tiles[6:])])); sys.exit()
    out = sys.argv[1]
    d1 = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', PREV, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    d2 = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ZOOM, '-frames:v', str(N_OUT), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-i', ZOOM, '-map', '0:v', '-map', '1:a', '-t', str(N_OUT / FPS), '-c:v', 'libx264', '-crf', '14', '-preset', 'medium',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(N_OUT):
        z = d2.stdout.read(W * H * 3); o = d1.stdout.read(W * H * 3) if n < N_PREV else b''
        if F0 <= n < F1: fr = (render(n / FPS, n) * 255 + 0.5).astype(np.uint8).tobytes()
        else: fr = o if len(o) == W * H * 3 else z
        enc.stdin.write(fr)
    enc.stdin.close(); enc.wait(); print('done')
