"""Mochary reel – opening B-roll (1.17–7.30 s):
Altman -> Reddit CEO (Huffman) -> 'one coach' = glowing ? silhouette -> $1,000,000,000 -> ? resolves into Matt Mochary.
Rendered over the zoomed talking head, colour-halftone print texture on the animation only."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
SRC = S + 'out/Mochary_zoom_v1.mp4'
W, H = 1080, 1920; FPS = 24000 / 1001
N_OUT = int(sys.argv[2]) if len(sys.argv) > 2 else 192          # render 0–8.0 s
F_IN, F_OUT = 28, 175                                              # 1.168 s … 7.299 s (frames 28–174 are animation)
FONT_N = S + 'fd/newsreader-latin-500-normal.ttf'; FONT_T = S + 'fd/newsreader-600.ttf'; FONT_L = S + 'fd/inter-600.ttf'

def cl(x): return min(1.0, max(0.0, x))
def eiq(x): x = cl(x); return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2       # in-out quint
def eic(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)

# ------------------------------------------------------------------ sprites (world space, rendered at 2x)
K = 2.0
def bust(name, crop, width_world, desat=0.78):
    im = cv2.cvtColor(cv2.imread(S + f'moch/cut/{name}.png'), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    m = cv2.imread(S + f'moch/cut/{name}_m.png', 0).astype(np.float32) / 255
    x0, y0, x1, y1 = crop; im = im[y0:y1, x0:x1]; m = m[y0:y1, x0:x1]
    w = int(width_world * K); h = int(w * im.shape[0] / im.shape[1])
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_CUBIC if w > im.shape[1] else cv2.INTER_AREA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    if w > (x1 - x0):                                                # small source: light unsharp after upscale
        im = np.clip(im + (im - cv2.GaussianBlur(im, (0, 0), 2.0)) * 0.6, 0, 1)
    g = im @ np.array([0.299, 0.587, 0.114], np.float32)
    im = g[..., None] + (im - g[..., None]) * desat                   # unify the three photos
    im = np.clip((im - 0.03) * 1.08, 0, 1) ** 1.05
    yy = np.linspace(0, 1, h)[:, None]
    fade = 1 - eic_arr((yy - 0.62) / 0.36)                           # busts dissolve into the black at the bottom
    a = m * fade
    return im.astype(np.float32), a.astype(np.float32), m.astype(np.float32)
def eic_arr(x):
    x = np.clip(x, 0, 1); return np.where(x < 0.5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)

BW = 440                                                             # bust width in world px
ALT = bust('altman', (170, 40, 1110, 1293), BW)
HUF = bust('huffman', (190, 0, 1590, 1867), BW)
MOC = bust('mochary', (0, 0, 450, 600), BW, desat=0.85)
POS = {'alt': (270, 430), 'huf': (810, 430), 'moc': (540, 1290)}   # bust top-centre in world
# silhouette of the coach = Mochary's own outline (so the reveal is a true resolve)
_, MOC_A, MOC_M = MOC
er = cv2.erode(MOC_M, np.ones((9, 9), np.uint8))
RIM = np.clip(cv2.GaussianBlur(MOC_M - er, (0, 0), 3) * 1.8, 0, 1) * (1 - eic_arr((np.linspace(0, 1, MOC_M.shape[0])[:, None] - 0.45) / 0.4))

def text_sprite(txt, font, size, track=0.0, pad=60):
    f = ImageFont.truetype(font, int(size * K))
    w = int(sum(f.getlength(c) for c in txt) + track * size * K * (len(txt) - 1)) + 2 * pad
    asc, desc = f.getmetrics(); h = asc + desc + 2 * pad
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); x = pad
    for c in txt:
        d.text((x, pad + asc), c, font=f, fill=255, anchor='ls'); x += f.getlength(c) + track * size * K
    return np.asarray(im).astype(np.float32) / 255, pad + asc          # sprite, baseline row
LAB_ALT = text_sprite('SAM ALTMAN', FONT_L, 26, 0.16)
LAB_HUF = text_sprite('STEVE HUFFMAN', FONT_L, 26, 0.16)
SUB_HUF = text_sprite('REDDIT CEO', FONT_L, 19, 0.2)
SUB_ALT = text_sprite('OPENAI', FONT_L, 19, 0.2)
QM = text_sprite('?', FONT_T, 300, 0.0)

# ------------------------------------------------------------------ counter $1,000,000,000 (reel per digit, like the 5M)
CN = 128; FCN = ImageFont.truetype(FONT_N, int(CN * K))
GL = {}
for c in '0123456789$,':
    asc, desc = FCN.getmetrics(); im = Image.new('L', (int(FCN.getlength('0') * 1.6), asc + desc + 40), 0)
    ImageDraw.Draw(im).text((im.width / 2, 20 + asc), c, font=FCN, fill=255, anchor='ms'); GL[c] = np.asarray(im).astype(np.float32) / 255
DIGW = max(FCN.getlength(d) for d in '0123456789'); COMW = FCN.getlength(',') * 1.1; DOLW = FCN.getlength('$') * 1.05
CELLH = int(GL['0'].shape[0] * 0.78)
FMT = '$1,000,000,000'
T_NUM = 3.86
REELS = []; j = 0; xpos = 0.0; LAYOUT = []
for c in FMT:
    wch = DOLW if c == '$' else COMW if c == ',' else DIGW
    LAYOUT.append((c, xpos + wch / 2)); xpos += wch
    if c.isdigit():
        REELS.append((len(LAYOUT) - 1, 10 * math.ceil(1 + j * 0.4) + int(c), 0.78 + 0.055 * j)); j += 1
CW_TOT = xpos
gh, gw = GL['0'].shape
STRIP = np.zeros((CELLH * 30 + gh, gw), np.float32)
for k in range(30): STRIP[k * CELLH:k * CELLH + gh] = np.maximum(STRIP[k * CELLH:k * CELLH + gh], GL[str(k % 10)])
yv = np.arange(gh)[:, None].astype(np.float32); rows = np.where(GL['0'].max(1) > 0.05)[0]; R0, R1 = rows[0] - 10, rows[-1] + 10
CMASK = np.clip(np.minimum((yv - (R0 - 22)) / 22, ((R1 + 22) - yv) / 22), 0, 1)
def counter_sprite(t):
    """returns (core, glowgain) sprite of the counter in its own space (2x)."""
    out = np.zeros((gh, int(CW_TOT) + 4), np.float32); gin = np.zeros_like(out)
    dt = t - T_NUM
    if dt < 0: return out, gin
    ent = cl(dt / 0.05); sig = 6 * math.exp(-dt / 0.06)
    reel_of = {li: (tot, dur) for li, tot, dur in REELS}
    for li, (c, cx) in enumerate(LAYOUT):
        if li in reel_of:
            tot, dur = reel_of[li]; p = cl(dt / dur); pos = tot * eoq(p)
            # 8-sample motion blur inside the reel
            acc = np.zeros((gh, gw), np.float32)
            v = tot * 5 * (1 - p) ** 4 / dur / FPS * 0.5                  # half-frame travel (180° shutter)
            for s in range(8):
                ps = (pos - v * (s / 7 - 0.5)) % 10
                acc += cv2.warpAffine(STRIP, np.float32([[1, 0, 0], [0, 1, -(10 + ps) * CELLH]]), (gw, gh), flags=cv2.INTER_LINEAR)
            g = acc / 8 * CMASK
            land = T_NUM + dur; lb = 1 + 3.2 * math.exp(-(t - land) / 0.09) if t >= land else 1.0
        else:
            g = GL[c] * CMASK; lb = 1.0
        x0 = int(round(cx - gw / 2)); a = g * ent
        if sig > 0.25: a = np.clip(cv2.GaussianBlur(a, (0, 0), sig) * (1 + sig * 0.3), 0, 1)
        sl = out[:, max(0, x0):x0 + gw]; out[:, max(0, x0):x0 + gw] = np.maximum(sl, a[:, :sl.shape[1]])
        gin[:, max(0, x0):x0 + gw] += a[:, :sl.shape[1]] * lb * (1 + 6 * math.exp(-dt / 0.085))
    return out, gin

# ------------------------------------------------------------------ camera keys: (time, scale, cx, cy) in world space
CAM = [(1.168, 1.30, 270, 760), (1.50, 1.335, 270, 760), (2.10, 1.00, 540, 790), (2.50, 1.02, 540, 800),
       (3.12, 0.86, 540, 1180), (5.17, 0.89, 540, 1185), (6.30, 1.70, 540, 1500), (7.30, 1.80, 540, 1500)]
def cam(t):
    for (t0, s0, x0, y0), (t1, s1, x1, y1) in zip(CAM, CAM[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            small = abs(s1 - s0) < 0.06 and abs(x1 - x0) < 5 and abs(y1 - y0) < 20
            e = eio(u) if small else eiq(u)
            return s0 + (s1 - s0) * e, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    return CAM[-1][1:]

def place(canvas, spr, alpha, wx, wy, camv, anchor='tc', sprite_scale=1.0):
    """warp a 2x world sprite into the screen. anchor 'tc' = (wx,wy) is top-centre, 'c' = centre, 'bl' baseline-centre."""
    s, cx, cy = camv; sc = s / K * sprite_scale
    h, w = spr.shape[:2]
    if anchor == 'tc': ox, oy = w / 2, 0
    elif anchor == 'c': ox, oy = w / 2, h / 2
    else: ox, oy = w / 2, anchor
    X = (wx - cx) * s + W / 2; Y = (wy - cy) * s + H / 2
    M = np.float32([[sc, 0, X - sc * ox], [0, sc, Y - sc * oy]])
    return cv2.warpAffine(spr, M, (W, H), flags=cv2.INTER_LINEAR), (cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR) if alpha is not None else None)

def flash(dt, tau=0.12, amp=5.0): return 1 + amp * math.exp(-dt / tau) if dt >= 0 else 0
def appear(dt, d=0.08): return cl(dt / d) if dt >= 0 else 0.0

def frame_layers(t):
    """returns photo-layer RGB (premultiplied), emissive core (L) and glow-input (L) for time t."""
    camv = cam(t); s = camv[0]
    rgb = np.zeros((H, W, 3), np.float32); core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    bg_out = 1 - eic((t - 5.17) / 0.55)                              # Altman/Huffman/lines/counter leave as we push into the ?
    # --- busts
    for key, spr, t_on in (('alt', ALT, 1.125), ('huf', HUF, 1.52)):
        dt = t - t_on
        if dt < 0 or bg_out <= 0: continue
        im, a, m = spr; wx, wy = POS[key]
        a2 = a * appear(dt, 0.07) * bg_out
        sig = 5 * math.exp(-dt / 0.07)
        if sig > 0.3: im = cv2.GaussianBlur(im, (0, 0), sig); a2 = cv2.GaussianBlur(a2, (0, 0), sig)
        pim, pa = place(None, im * a2[..., None], a2, wx, wy, camv)
        boost = 1 + 0.9 * math.exp(-dt / 0.06)                           # body flash: burns bright then settles
        rgb = rgb * (1 - pa[..., None]) + np.clip(pim * boost, 0, 1)
        gin += pa * 0.9 * math.exp(-dt / 0.09)
    # --- labels + nodes + connecting lines
    nodes = {'alt': (270, 1062), 'huf': (810, 1062)}
    for key, lab, sub, t_on in (('alt', LAB_ALT, SUB_ALT, 1.40), ('huf', LAB_HUF, SUB_HUF, 1.72)):
        dt = t - t_on
        if dt < 0 or bg_out <= 0: continue
        a = appear(dt, 0.05) * bg_out; sig = 4 * math.exp(-dt / 0.06)
        for spr, (wy, op) in ((lab, (1100, 0.92)), (sub, (1140, 0.55))):
            L, base = spr; Lb = cv2.GaussianBlur(L, (0, 0), sig) * (1 + sig * 0.3) if sig > 0.3 else L
            pl, _ = place(None, np.clip(Lb, 0, 1) * a * op, None, nodes[key][0], wy, camv, anchor=base)
            core = np.maximum(core, pl); gin += pl * flash(dt, 0.085, 6.0) * 0.6
    # line Altman -> Huffman, then branch down to the ?
    def wline(p0, p1, prog, width=2.2, op=0.75):
        if prog <= 0: return
        x0, y0 = p0; x1, y1 = p1; xe, ye = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog
        sc, cx, cy = camv
        P0 = ((x0 - cx) * sc + W / 2, (y0 - cy) * sc + H / 2); P1 = ((xe - cx) * sc + W / 2, (ye - cy) * sc + H / 2)
        L = np.zeros((H, W), np.float32)
        cv2.line(L, (int(P0[0] * 8), int(P0[1] * 8)), (int(P1[0] * 8), int(P1[1] * 8)), op, max(1, int(width * sc)), cv2.LINE_AA, shift=3)
        for P in (P0,):
            cv2.circle(L, (int(P[0] * 8), int(P[1] * 8)), int(5.5 * sc * 8), 1.0, -1, cv2.LINE_AA, shift=3)
        if prog >= 1: cv2.circle(L, (int(P1[0] * 8), int(P1[1] * 8)), int(5.5 * sc * 8), 1.0, -1, cv2.LINE_AA, shift=3)
        L *= bg_out; np.maximum(core, L, out=core); gin[:] += L * 0.9
        # travelling pulse (the message being passed)
        return P0, P1
    lp = eiq((t - 1.80) / 0.42)
    wline((290, 1062), (790, 1062), lp)
    if 1.80 <= t <= 2.45:                                                # bright pulse running along the line
        u = eiq((t - 1.80) / 0.55); px = 290 + 500 * u
        sc, cx, cy = camv; P = ((px - cx) * sc + W / 2, (1062 - cy) * sc + H / 2)
        L = np.zeros((H, W), np.float32); cv2.circle(L, (int(P[0]), int(P[1])), int(4 * sc), 1.0, -1, cv2.LINE_AA)
        gin += L * 6 * bg_out
    wline((540, 1062), (540, 1278), eiq((t - 2.72) / 0.32))
    # --- the coach: silhouette with glowing ?, then the reveal
    T_Q, T_REV = 2.98, 6.47
    dq = t - T_Q
    if dq >= 0:
        im, a, m = MOC; wx, wy = POS['moc']
        sil_a = a * appear(dq, 0.10)
        w_in = math.exp(-dq / 0.07) * 0.8
        rev = eic((t - T_REV - 0.05) / 0.22) if t >= T_REV else 0.0              # silhouette -> photo
        dark = np.full_like(im, 0.075) * np.array([1, 1, 1.04], np.float32)
        body = dark * (1 - rev) + im * rev
        sig = 5 * math.exp(-dq / 0.08)
        bl = cv2.GaussianBlur(body, (0, 0), sig) if sig > 0.3 else body
        pim, pa = place(None, bl * sil_a[..., None], sil_a, wx, wy, camv)
        # reveal flash: the body burns white for a moment (Nikita-style), then lets go
        dr = t - T_REV
        if dr >= 0:
            rise, hold, rel = 0.06, 0.05, 0.30
            w_ = eic(dr / rise) if dr < rise else 1.0 if dr < rise + hold else 1 - eic((dr - rise - hold) / rel)
        else: w_ = 0.0
        rgb = rgb * (1 - pa[..., None]) + pim
        w_ = max(w_, w_in)
        rgb = rgb * (1 - pa[..., None] * w_) + pa[..., None] * w_ * 1.0
        gin += pa * (1.1 * w_ + 0.6 * math.exp(-dq / 0.09))
        # rim light on the silhouette (fades as he is revealed)
        rim, _ = place(None, RIM * appear(dq, 0.12) * (1 - rev) * 0.55, None, wx, wy, camv)
        core = np.maximum(core, rim * 0.6); gin += rim * 0.8
        # the question mark, centred on the head
        if rev < 1:
            L, base = QM; qa = appear(dq - 0.04, 0.06) * (1 - rev) * (1 - w_)
            sigq = 6 * math.exp(-(dq - 0.04) / 0.07) if dq > 0.04 else 6
            Lq = cv2.GaussianBlur(L, (0, 0), sigq) * (1 + sigq * 0.3) if sigq > 0.3 else L
            breathe = 1 + 0.08 * math.sin((t - T_Q) * 2 * math.pi * 0.7)
            pq, _ = place(None, np.clip(Lq, 0, 1) * qa, None, wx + 4, wy + 192, camv, anchor='c')
            core = np.maximum(core, pq); gin += pq * (flash(dq - 0.04, 0.10, 7.0) * 0.8 * breathe if dq > 0.04 else 0)
    # --- counter
    if t >= T_NUM and bg_out > 0:
        cc, cg = counter_sprite(t)
        pc, _ = place(None, cc * bg_out, None, 540, 1790, camv, anchor='c')
        pg, _ = place(None, cg * bg_out, None, 540, 1790, camv, anchor='c')
        core = np.maximum(core, pc); gin += pg * 0.7
    return rgb, core, gin

# ------------------------------------------------------------------ title "Matt Mochary" behind the subject (screen space)
FT = ImageFont.truetype(FONT_T, 150)
def title(t, t0=6.50, base=690):
    txt = 'Matt Mochary'; tr = 0.08 - 0.11 * eoq((t - t0) / 0.9); TS = 150
    tot = sum(FT.getlength(c) for c in txt) + tr * TS * (len(txt) - 1); x = (W - tot) / 2
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32); k = 0
    for c in txt:
        if c != ' ':
            dt = t - t0 - k * 0.035; k += 1
            if dt > 0:
                im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).text((x, base), c, font=FT, fill=255, anchor='ls')
                Lc = np.asarray(im).astype(np.float32) / 255
                sg = 7.0 * math.exp(-dt / 0.07); a = Lc if sg < 0.25 else np.clip(cv2.GaussianBlur(Lc, (0, 0), sg) * (1 + sg * 0.3), 0, 1)
                a = a * min(1, dt / 0.05); core = np.maximum(core, a); gin += a * (1.5 + 9 * math.exp(-dt / 0.11))
        x += FT.getlength(c) + tr * TS
    return core, gin

def glow_of(a):
    small = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, H)) * wt
    return g
GCOL = np.array([1.0, 0.98, 0.95], np.float32)

# ------------------------------------------------------------------ halftone print texture (TBH colour mode)
CELL = 7.0; ang = math.radians(45)
Yg, Xg = np.mgrid[0:H, 0:W].astype(np.float32)
u = (Xg * math.cos(ang) + Yg * math.sin(ang)) / CELL; v = (-Xg * math.sin(ang) + Yg * math.cos(ang)) / CELL
DIST = np.sqrt((u - np.floor(u) - 0.5) ** 2 + (v - np.floor(v) - 0.5) ** 2).astype(np.float32)
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
# faint room: a dark warm radial so the black has depth and the paper grain reads
BG = (np.clip(1 - (((Xg - W / 2) / (W * 0.9)) ** 2 + ((Yg - H * 0.48) / (H * 0.7)) ** 2), 0, 1) ** 2 * 0.055)[..., None] * np.array([1.0, 0.96, 0.9], np.float32)

def anim_frame(t, n):
    # temporal supersampling: 6 sub-frames while the camera moves, 2 otherwise
    c0, c1 = cam(t - 0.25 / FPS), cam(t + 0.25 / FPS)
    moving = abs(c0[0] - c1[0]) > 0.002 or abs(c0[1] - c1[1]) > 0.5 or abs(c0[2] - c1[2]) > 0.5
    ns = 6 if moving else 1
    rgb = np.zeros((H, W, 3), np.float32); core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32)
    for k in range(ns):
        tt = t + ((k + 0.5) / ns - 0.5) * 0.5 / FPS if ns > 1 else t
        tt = max(tt, F_IN / FPS)
        r_, c_, g_ = frame_layers(tt); rgb += r_ / ns; core += c_ / ns; gin += g_ / ns
    fr = BG + rgb * (1 - 0)
    # title behind Mochary
    if t >= 6.50:
        tc, tg = title(t)
        g = glow_of(tg); fr2 = 1 - (1 - fr) * (1 - np.clip(g[..., None] * GCOL * 0.85, 0, 1)); fr2 = fr2 * (1 - tc[..., None]) + tc[..., None]
        im, a, m = MOC; _, pa = place(None, a, a, POS['moc'][0], POS['moc'][1], cam(t))
        fr = fr2 * (1 - pa[..., None]) + fr * pa[..., None]          # he stays in front of his name
    g = glow_of(gin)
    fr = 1 - (1 - fr) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
    fr = fr * (1 - core[..., None]) + core[..., None]
    return halftone(np.clip(fr, 0, 1).astype(np.float32), n)

if __name__ == '__main__':
    out = sys.argv[1]
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-frames:v', str(N_OUT), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-i', SRC, '-map', '0:v', '-map', '1:a', '-t', str(N_OUT / FPS), '-c:v', 'libx264', '-crf', '15', '-preset', 'medium',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(N_OUT):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = n / FPS
        if F_IN <= n < F_OUT:
            fr = (anim_frame(t, n) * 255 + 0.5).astype(np.uint8)
        else:
            fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
        enc.stdin.write(fr.tobytes())
        if n % 24 == 0: print('frame', n, flush=True)
    enc.stdin.close(); enc.wait(); print('done')
