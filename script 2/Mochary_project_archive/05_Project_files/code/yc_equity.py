"""'But founders still give up seven percent for a demo day deadline and the batch.' — YC-branded B-roll (43.38–47.85)."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
U = '/root/.claude/uploads/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/'
W, H = 1080, 1920; FPS = 24000 / 1001; K = 2
N0, N1 = int(round(43.38 * FPS)), int(round(47.85 * FPS))
YC = (251, 101, 30); WHITE = (255, 255, 255)
def F(s, w='600'): return ImageFont.truetype(S + f'fd/inter-{w}.ttf', int(s * K))
def cl(x): return min(1.0, max(0.0, x))
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eic(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def back(x, s=1.5): x = cl(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, u): return a + (b - a) * u
# ---- the Y glyph, lifted from the supplied logo
_lg = np.asarray(Image.open(U + 'ceb80d97-image.png').convert('RGB')).astype(np.float32)
_ym = np.clip((_lg.min(2) - 120) / 110, 0, 1)                          # white Y on orange
_ym = _ym[:, 4:362]                                                    # square-ish
YMASK = Image.fromarray((cv2.resize(_ym, (512, 512), interpolation=cv2.INTER_CUBIC).clip(0, 1) * 255).astype(np.uint8))
def logo(im, cx, cy, size, a=1.0, inverse=True):
    """white square with an orange Y (as it sits on an orange field)"""
    s = int(size * K); x0, y0 = int(cx * K - s / 2), int(cy * K - s / 2)
    sq = Image.new('RGBA', (s, s), WHITE + (int(255 * a),) if inverse else YC + (int(255 * a),))
    ym = YMASK.resize((s, s), Image.LANCZOS)
    col = Image.new('RGBA', (s, s), (YC if inverse else WHITE) + (255,))
    sq.paste(col, (0, 0), Image.fromarray((np.asarray(ym).astype(np.float32) * a).astype(np.uint8)))
    im.alpha_composite(sq, (x0, y0))
# ---- topographic contour field (like YC's brand backdrop), slowly flowing
yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32) * 2
def topo(t):
    f = (np.sin(xx / 310 + 0.7 * np.sin(yy / 420 + t * 0.25)) + np.sin(yy / 260 - 0.5 * np.cos(xx / 380 - t * 0.2)) * 0.8
         + np.sin((xx + yy) / 520 + t * 0.15) * 0.6) * 4.2
    gy, gx = np.gradient(f); g = np.sqrt(gx ** 2 + gy ** 2) / 2 + 1e-3
    d = np.abs(f - np.round(f)) / g
    ln = np.exp(-(d / 1.1) ** 2)
    return cv2.resize(ln, (W, H), interpolation=cv2.INTER_LINEAR)
# ---- timeline
T_DISC, T_LOGO, T_CUT, T_FLY, T_7 = 43.40, 43.66, 44.26, 44.62, 44.66
T_ARRIVE = T_FLY + 0.62
T_DEMO, T_BATCH = 45.26, 46.80
DISC_C, DISC_R = (540, 1130), 300
WEDGE = (-90.0, -90.0 + 25.2)                                           # 7% of the circle, pointing at the logo
LETTERS = 'ABCDEFGHJKLMNPRSTVWZQOUXY'
rng = np.random.default_rng(11); MARKS = list(rng.integers(0, 8, 70))
def mark(d, m, x, y, r, col):
    """simple startup-logo marks"""
    R = lambda v: v * K
    if m == 0: d.ellipse([R(x - r), R(y - r), R(x + r), R(y + r)], fill=col)
    elif m == 1: d.ellipse([R(x - r), R(y - r), R(x + r), R(y + r)], outline=col, width=int(R(r * 0.32)))
    elif m == 2: d.polygon([(R(x), R(y - r)), (R(x + r), R(y + r * 0.8)), (R(x - r), R(y + r * 0.8))], fill=col)
    elif m == 3: d.pieslice([R(x - r), R(y - r), R(x + r), R(y + r)], 180, 360, fill=col)
    elif m == 4: d.rounded_rectangle([R(x - r * 0.85), R(y - r * 0.85), R(x + r * 0.85), R(y + r * 0.85)], radius=int(R(r * 0.25)), fill=col)
    elif m == 5:
        w_ = r * 0.36; d.rectangle([R(x - w_), R(y - r), R(x + w_), R(y + r)], fill=col); d.rectangle([R(x - r), R(y - w_), R(x + r), R(y + w_)], fill=col)
    elif m == 6:
        for i in range(3): d.rectangle([R(x - r + i * r * 0.75), R(y - r * 0.2 - i * r * 0.4), R(x - r + i * r * 0.75 + r * 0.5), R(y + r)], fill=col)
    else: d.polygon([(R(x), R(y - r)), (R(x + r), R(y)), (R(x), R(y + r)), (R(x - r), R(y))], fill=col)
def scene(T):
    im = Image.new('RGBA', (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # logo: pops in, catches the slice, then rises to sit as an anchor
    up = eic((T - T_DEMO) / 0.55)
    ls = back((T - T_LOGO) / 0.45) * (1 + 0.10 * math.exp(-max(0, T - T_ARRIVE) / 0.12) * (T > T_ARRIVE))
    ly = lerp(470, 330, up); lsize = lerp(170, 120, up) * ls
    if T >= T_LOGO: logo(im, 540, ly, lsize, a=cl((T - T_LOGO) / 0.12))
    # --- scene 1: the company, 100% -> 93%
    out1 = eic((T - T_DEMO) / 0.32)
    if T >= T_DISC and out1 < 1:
        s = back((T - T_DISC) / 0.55) * (1 - 0.35 * out1); r = DISC_R * s; cx, cy = DISC_C[0], DISC_C[1] + 260 * out1
        A = int(255 * (1 - out1) * cl((T - T_DISC) / 0.1))
        detached = T >= T_FLY
        if detached: d.pieslice([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], WEDGE[1], WEDGE[0] + 360, fill=WHITE + (A,))
        else: d.ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], fill=WHITE + (A,))
        # the cut: two orange lines score the slice before it lifts out
        pc = eoc((T - T_CUT) / 0.3)
        if pc > 0 and not detached:
            for ang in WEDGE:
                a_ = math.radians(ang); d.line([(cx * K, cy * K), ((cx + r * pc * math.cos(a_)) * K, (cy + r * pc * math.sin(a_)) * K)], fill=YC + (A,), width=int(5 * K))
        pct = 100 - 7 * eoc((T - T_FLY) / 0.45)
        d.text((cx * K, (cy + 175 * s) * K), f'{pct:.0f}%', font=F(128 * s), fill=YC + (A,), anchor='ms')
        d.text((cx * K, (cy + 52 * s) * K), 'YOUR COMPANY', font=F(27 * s), fill=YC + (int(A * 0.85),), anchor='ms')
    # the 7% slice flies up into the logo
    if T >= T_FLY and T < T_ARRIVE + 0.05:
        u = eic((T - T_FLY) / (T_ARRIVE - T_FLY))
        sx, sy = DISC_C; tx, ty = 540 - 12, 470 + 70                    # tip travels from the disc centre up into the logo
        lift = eoc((T - T_FLY) / 0.22) * 40                               # first it lifts out of the disc
        px = lerp(sx, tx, u) + 60 * math.sin(math.pi * u); py = lerp(sy - lift, ty, u)
        sc = lerp(1.0, 0.22, u ** 1.3); rot = -12 * math.sin(math.pi * u)
        r = DISC_R * sc; pts = [(px, py)]
        for a in np.linspace(WEDGE[0], WEDGE[1], 24):
            a_ = math.radians(a + rot); pts.append((px + r * math.cos(a_), py + r * math.sin(a_)))
        lab = (px + r * 0.62 + 46, py - r * 0.55)
        # pivot the wedge around its tip so it travels as a piece
        d.polygon([(x * K, y * K) for x, y in pts], fill=WHITE + (int(255 * (1 - cl((T - T_ARRIVE + 0.06) / 0.06))),))
    a7 = cl((T - T_7) / 0.12) * (1 - eic((T - T_DEMO) / 0.3))
    if a7 > 0:
        off = 40 * (1 - eoq((T - T_7) / 0.5))
        d.text((300 * K, (820 + off) * K), '7%', font=F(170), fill=WHITE + (int(255 * a7),), anchor='ms')
        d.text((300 * K, (870 + off) * K), 'GOES TO YC', font=F(26), fill=WHITE + (int(220 * a7 * cl((T - T_7 - 0.12) / 0.15)),), anchor='ms')
    # --- scene 2: demo day countdown
    a2 = cl((T - T_DEMO - 0.12) / 0.2) * (1 - eic((T - T_BATCH + 0.04) / 0.14))
    if a2 > 0:
        rise = 40 * (1 - eoq((T - T_DEMO - 0.12) / 0.5))
        d.text((540 * K, (700 + rise) * K), 'DEMO DAY', font=F(44), fill=WHITE + (int(255 * a2),), anchor='ms')
        # rolling weeks counter 12 -> 0
        u = cl((T - 45.45) / 1.05); v = 12 * (1 - eic(u)); cur = math.floor(v); fr_ = v - cur
        box = Image.new('L', (W * K, 420 * K), 0); bd = ImageDraw.Draw(box); pitch = 330
        for j, num in enumerate((cur, cur + 1)):
            if num > 12: continue
            yb = 330 + (j - fr_) * pitch * -1 + 0
            bd.text((540 * K, (300 + (fr_ - j) * pitch + rise) * K), f'{num:02d}', font=F(320), fill=255, anchor='ms')
        col = Image.new('RGBA', box.size, WHITE + (255,))
        bx = np.asarray(box).astype(np.float32); yv = np.linspace(-1, 1, bx.shape[0])[:, None]
        bx = bx * np.clip((0.62 - np.abs(yv)) / 0.14, 0, 1) * a2
        im.alpha_composite(Image.merge('RGBA', (*col.split()[:3], Image.fromarray(bx.astype(np.uint8)))), (0, 760 * K))
        d.text((540 * K, (1190 + rise) * K), 'WEEKS TO GO', font=F(28, '500'), fill=WHITE + (int(225 * a2),), anchor='ms')
        # progress bar
        bw = 640; bx0 = 540 - bw / 2; byy = 1270 + rise
        d.rounded_rectangle([bx0 * K, byy * K, (bx0 + bw) * K, (byy + 10) * K], radius=5 * K, fill=WHITE + (int(70 * a2),))
        d.rounded_rectangle([bx0 * K, byy * K, (bx0 + max(10, bw * eic(u))) * K, (byy + 10) * K], radius=5 * K, fill=WHITE + (int(255 * a2),))
    # --- scene 3: the batch
    if T >= T_BATCH:
        cols, rows, ts, gap = 7, 9, 104, 22; gw = cols * ts + (cols - 1) * gap; gx0 = 540 - gw / 2; gy0 = 560
        la = cl((T - T_BATCH - 0.05) / 0.2)
        d.text((540 * K, 488 * K), 'THE BATCH  ·  W26', font=F(30), fill=WHITE + (int(255 * la),), anchor='ms')
        for r_ in range(rows):
            for c_ in range(cols):
                x = gx0 + c_ * (ts + gap) + ts / 2; y = gy0 + r_ * (ts + gap) + ts / 2
                dist = math.hypot(x - 540, y - 1060); dt = T - T_BATCH - 0.04 - dist / 2600
                if dt <= 0: continue
                s = back(dt / 0.32, 1.8) * ts / 2; aa = cl(dt / 0.08)
                d.rounded_rectangle([(x - s) * K, (y - s) * K, (x + s) * K, (y + s) * K], radius=int(s * 0.28 * K), fill=WHITE + (int(255 * aa),))
                if s > 14: mark(d, MARKS[r_ * cols + c_], x, y, s * 0.42, YC + (int(255 * aa),))
    return im
# ---- compositing
gy_, gx_ = np.mgrid[0:H, 0:W].astype(np.float32)
LIGHT = (1 + 0.10 * np.exp(-(((gx_ - 540) / 700) ** 2 + ((gy_ - 860) / 1000) ** 2)) - 0.08 * (((gx_ - 540) / 900) ** 2 + ((gy_ - 960) / 1400) ** 2))[..., None]
BGC = np.array(YC, np.float32) / 255
rngg = np.random.default_rng(6); GR = [rngg.normal(0, 0.012, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def cam(T):
    z = 1.0 + 0.035 * eio((T - 43.38) / 4.5); return z
def render(n):
    T = n / FPS; im = scene(T)
    a = np.asarray(im).astype(np.float32) / 255
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    z = cam(T); M = np.float32([[z, 0, 540 * (1 - z)], [0, z, 960 * (1 - z)]]); a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    al = a[..., 3:4]; col = a[..., :3]
    tp = topo(T - 43.38)[..., None]
    bg = BGC * LIGHT * (1 - 0.15 * tp)                                  # thin darker contour lines
    sh = cv2.GaussianBlur(al[..., 0], (0, 0), 16); sh = np.roll(sh, 12, axis=0)[..., None]
    bg = bg * (1 - 0.22 * sh)
    img = bg * (1 - al) + col * al
    img = img * (1 + 0.35 * math.exp(-(T - 43.38) / 0.05))
    img = img + cv2.resize(GR[(n // 2) % 6], (W, H))[..., None] * 0.8
    return np.clip(img, 0, 1)

if __name__ == '__main__':
    out = sys.argv[1]
    if out.endswith('.jpg'):
        fs = [int(x) for x in sys.argv[2].split(',')]
        tiles = [cv2.resize((render(f) * 255).astype(np.uint8), (300, 533), interpolation=cv2.INTER_AREA) for f in fs]
        cv2.imwrite(out, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR)); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(N0, N1): enc.stdin.write((render(n) * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print('done', N0, N1)
