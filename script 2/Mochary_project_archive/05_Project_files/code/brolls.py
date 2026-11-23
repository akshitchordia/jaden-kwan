"""Procedural B-rolls for the Mochary reel. Every scene takes absolute timeline seconds T and returns (Frame, cam)."""
import sys, math, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/moch')
from kit import *

TAU = 2 * math.pi
def spike(dt, tau=0.12, k=1.0): return 0.0 if dt < 0 else k * math.exp(-dt / tau)
def app(dt, d=0.12): return cl(dt / d)
def rnd(seed): return np.random.default_rng(seed)

DOTS = np.zeros((H, W), np.float32)
for yy in range(30, H, 60):
    for xx in range(30, W, 60): cv2.circle(DOTS, (xx * 8, yy * 8), 13, 1.0, -1, cv2.LINE_AA, shift=3)

def stroke(fr, pts, a=1.0, w=2, g=0.6, acc=False):
    """draw polyline into core (or acc) and glow input"""
    if len(pts) < 2: return
    L = fr.acc if acc else fr.core
    poly(L, pts, a, w); poly(fr.gin, pts, a * g, w)
def erase(fr, pts):
    fillpoly(fr.core, pts, 0.0); fillpoly(fr.gin, pts, 0.0); fillpoly(fr.acc, pts, 0.0)
    p = np.array([[int(round(x * 8)), int(round(y * 8))] for x, y in pts], np.int32)
    cv2.fillPoly(fr.rgb, [p], (0.0, 0.0, 0.0), cv2.LINE_AA, shift=3)
def tint(fr, pts, v=0.06):
    p = np.array([[int(round(x * 8)), int(round(y * 8))] for x, y in pts], np.int32)
    cv2.fillPoly(fr.rgb, [p], (v, v * 0.96, v * 0.9), cv2.LINE_AA, shift=3)
def ell_pts(c, rx, ry, a0=0, a1=TAU, n=96, rot=0.0):
    th = np.linspace(a0, a1, n); cr, sr = math.cos(rot), math.sin(rot)
    return [(c[0] + rx * math.cos(t) * cr - ry * math.sin(t) * sr, c[1] + rx * math.cos(t) * sr + ry * math.sin(t) * cr) for t in th]
def rect_pts(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
def rot_rect(c, w, h, ang):
    ca, sa = math.cos(ang), math.sin(ang); out = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2)):
        out.append((c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca))
    return out
def put_text(fr, txt, path, size, x, y, t_on, T, anchor='ms', track=0.0, a=1.0, acc=False, peak=5.0, typed=0.0):
    if T < t_on: return
    if typed > 0:
        n = int(cl((T - t_on) / typed) * len(txt) + 0.999); txt = txt[:n]
        if not txt: return
        L = text(txt, path, size, x, y, anchor, track); dt = 1.0
        fr.core = np.maximum(fr.core, L * a) if not acc else fr.core;
        if acc: fr.acc = np.maximum(fr.acc, L * a)
        fr.gin += L * a * 0.7; return
    L = text(txt, path, size, x, y, anchor, track)
    bloom_text(fr, L, T - t_on, peak=peak, op=a, accent=acc)

# ------------------------------------------------------------------ B2  "coaching starts at 10 grand a month"
_DIG = {}
def digit_tile(d, size):
    k = (d, size)
    if k not in _DIG:
        f = font(SERIF, size); im = Image.new('L', (int(size * 0.75), int(size * 1.25)), 0)
        ImageDraw.Draw(im).text((im.width / 2, size * 1.0), str(d), font=f, fill=255, anchor='ms')
        _DIG[k] = np.asarray(im).astype(np.float32) / 255
    return _DIG[k]
def counter(fr, T, chars, x0, base, size, t0, lands, spins):
    """slot-machine counter: digit columns spin and decelerate into place; landing flashes"""
    f = font(SERIF, size); pitch = size * 1.05
    widths = [f.getlength(c) * (1.0 if c in '$,' else 1.02) for c in chars]
    x = x0 - sum(widths) / 2; di = 0
    for c, wdt in zip(chars, widths):
        if c in '$,':
            L = text(c, SERIF, size, x, base, 'ls'); bloom_text(fr, L, T - t0, peak=4); x += wdt; continue
        tl = lands[di]; target = int(c); rot = spins[di]; di += 1
        u = cl((T - t0) / (tl - t0)); p = target + rot * 10 * (1 - eoc(u))
        u2 = cl((T + 1 / FPS - t0) / (tl - t0)); spd = abs((rot * 10 * (1 - eoc(u))) - (rot * 10 * (1 - eoc(u2))))  # digits per frame
        tile_h = int(size * 1.25); col = np.zeros((tile_h, int(size * 0.75)), np.float32)
        base_d = math.floor(p); fr_ = p - base_d
        for j, dd in enumerate((base_d, base_d + 1)):
            tile = digit_tile(int(dd) % 10, size); off = int(round((j - fr_) * pitch))
            ys, ye = max(0, off), min(tile_h, tile_h + off)
            if ye > ys: col[ys:ye] = np.maximum(col[ys:ye], tile[ys - off:ye - off])
        sig = min(40.0, spd * pitch * 0.45)
        if sig > 0.6: col = cv2.GaussianBlur(col, (1, 0), sigmaX=0.01, sigmaY=sig) if False else cv2.GaussianBlur(col, (0, 0), sigmaX=0.3, sigmaY=sig)
        # vertical window fade (drum)
        yy = np.linspace(-1, 1, tile_h)[:, None]; col *= np.clip(1.25 - np.abs(yy) * 1.1, 0, 1)
        top = int(base - size * 1.0); xl = int(x + (wdt - col.shape[1]) / 2)
        a = col * app(T - t0, 0.08)
        y0c, x0c = max(0, top), max(0, xl); y1c, x1c = min(H, top + tile_h), min(W, xl + col.shape[1])
        sub = a[y0c - top:y1c - top, x0c - xl:x1c - xl]
        fr.core[y0c:y1c, x0c:x1c] = np.maximum(fr.core[y0c:y1c, x0c:x1c], sub)
        fr.gin[y0c:y1c, x0c:x1c] += sub * (0.7 + spike(T - tl, 0.1, 6) + spike(T - t0, 0.1, 4))
        x += wdt

def coin(fr, cx, cy, rx, ry, th, a=1.0, acc=False, g=0.5):
    sil = ell_pts((cx, cy), rx, ry, math.pi, TAU, 48) + ell_pts((cx, cy + th), rx, ry, 0, math.pi, 48)
    erase(fr, sil); tint(fr, sil, 0.05)
    stroke(fr, ell_pts((cx, cy), rx, ry), a, 2, g, acc)
    stroke(fr, ell_pts((cx, cy + th), rx, ry, 0, math.pi, 48), a, 2, g, acc)
    stroke(fr, [(cx - rx, cy), (cx - rx, cy + th)], a, 2, g, acc); stroke(fr, [(cx + rx, cy), (cx + rx, cy + th)], a, 2, g, acc)
    for k in range(2, 28, 2):                                        # reeding on the visible rim
        ang = math.pi * k / 28; x = cx + rx * math.cos(ang); yv = cy + ry * math.sin(ang)
        line(fr.acc if acc else fr.core, (x, yv + 3), (x, yv + th - 3), a * (0.15 + 0.25 * math.sin(ang)), 1)
    stroke(fr, ell_pts((cx, cy), rx * 0.72, ry * 0.72), a * 0.35, 1, 0.2, acc)

def B2(T):
    fr = Frame(); t0 = 13.84
    NC = 13; base = 1300; th = 30
    for i in range(NC):
        tl = 14.05 + i * 0.13
        if T < tl - 0.30: break
        u = cl((T - (tl - 0.30)) / 0.30); y_land = base - i * th
        y = lerp(y_land - min(300, y_land - 860), y_land, u * u)
        if T > tl: y = y_land - 10 * math.exp(-(T - tl) / 0.05) * math.sin((T - tl) * 40)
        last = i == NC - 1
        coin(fr, 540, y, 250, 74, th, a=0.95 * app(T - (tl - 0.30), 0.08), acc=last, g=0.6 + spike(T - tl, 0.1, 3))
    counter(fr, T, '$10,000', 540, 700, 196, 13.90, [15.52, 15.60, 15.68, 15.76, 15.84], [5, 7, 8, 9, 10])
    put_text(fr, '/ MONTH', MONO, 42, 540, 800, 16.08, T, track=0.22, acc=True, typed=0.25)
    z = 1.0 + 0.06 * eio((T - t0) / 2.6); return fr, (z, 540, 900, 0, 30 - 40 * eio((T - t0) / 2.6))

# ------------------------------------------------------------------ B3  "every session ends with you writing down an action"
def cursive(x0, y0, words, lw=29, gap=30, seed=3):
    r = rnd(seed); strokes = []; x = x0
    for nl in words:
        pts = []; a = lw / TAU; b = 8.5
        hs = r.uniform(0.6, 1.0, nl); tall = r.random(nl) < 0.25
        for k in range(nl):
            for s in np.linspace(0, TAU, 18, endpoint=False):
                h = (34 if tall[k] else 16) * hs[k]
                pts.append((x + a * s - b * math.sin(s) + k * lw, y0 - h * (1 - math.cos(s)) / 2))
        pts.append((x + nl * lw, y0)); strokes.append(pts); x += nl * lw + gap
    return strokes
CARD = (150, 330, 930, 1290); ROWS = [520 + k * 112 for k in range(7)]
OLD = [cursive(330, ROWS[0] - 8, [4, 6, 3], seed=11), cursive(330, ROWS[1] - 8, [7, 2, 5], seed=12)]
NEW = cursive(330, ROWS[2] - 8, [6, 3, 7], seed=5)
def checkbox(fr, x, y, s, a, p=1.0, acc=False, g=0.5):
    stroke(fr, partial(rect_pts(x, y, x + s, y + s), p), a, 2, g, acc)
def check(fr, x, y, s, p, a=1.0, acc=True, g=2.0):
    pts = [(x + s * 0.18, y + s * 0.52), (x + s * 0.42, y + s * 0.78), (x + s * 0.95, y - s * 0.05)]
    stroke(fr, partial(pts, p), a, 5, g, acc)
def draw_strokes(fr, strokes, p, a, w=3, g=0.4):
    tot = sum(len(s) for s in strokes); n = p * tot; done = 0; tip = None
    for s in strokes:
        k = n - done
        if k <= 0: break
        part = partial(s, min(1, k / len(s))); stroke(fr, part, a, w, g); tip = part[-1] if part else tip; done += len(s)
    return tip
def B3(T):
    fr = Frame(); t0 = 19.23
    x0, y0, x1, y1 = CARD; pc = eoq((T - t0) / 0.55)
    sil = rect_pts(x0, y0, x1, y1); tint(fr, sil, 0.045 * pc)
    stroke(fr, partial(sil, pc), 0.6, 2, 0.6 + spike(T - t0, 0.15, 2))
    for k, ry in enumerate(ROWS):
        pk = eoq((T - t0 - 0.12 - k * 0.04) / 0.5)
        if pk > 0: line(fr.core, (230, ry), (230 + 620 * pk, ry), 0.16, 1)
    put_text(fr, 'SESSION 14', MONO, 26, 230, 430, t0 + 0.2, T, anchor='ls', track=0.18, a=0.7, typed=0.3)
    put_text(fr, 'NEXT ACTION', MONO, 22, 850, 430, t0 + 0.35, T, anchor='rs', track=0.18, a=0.45, typed=0.3)
    for k in range(2):                                            # earlier sessions: written + ticked, dimmed
        pk = eoq((T - t0 - 0.25 - k * 0.12) / 0.5)
        if pk > 0:
            draw_strokes(fr, OLD[k], pk, 0.38, 2, 0.15); checkbox(fr, 248, ROWS[k] - 52, 44, 0.38)
            check(fr, 248, ROWS[k] - 52, 44, pk, 0.38, acc=False, g=0.1)
    pb = eoq((T - 20.15) / 0.35)
    if pb > 0: checkbox(fr, 248, ROWS[2] - 52, 44, 0.95, pb, g=0.6 + spike(T - 20.15, 0.12, 2))
    pw = cl((T - 20.40) / 0.95); pw = pw * pw * (3 - 2 * pw) * 0.25 + pw * 0.75
    tip = None
    if pw > 0: tip = draw_strokes(fr, NEW, pw, 1.0, 3, 0.8)
    pc2 = eoc((T - 21.40) / 0.22)
    if pc2 > 0: check(fr, 248, ROWS[2] - 52, 44, pc2, g=2.5 + spike(T - 21.4, 0.12, 6))
    # pen: follows the tip while writing, then glides to the checkbox
    pen_at = None
    if T < 20.40: pen_at = (lerp(900, 330, eoc((T - 19.6) / 0.8)), lerp(1150, ROWS[2] - 8, eoc((T - 19.6) / 0.8)))
    elif T < 21.36: pen_at = tip or (330, ROWS[2] - 8)
    else:
        u = eic((T - 21.36) / 0.2); ck = (248 + 44 * 0.95, ROWS[2] - 52 - 2)
        end = NEW[-1][-1]; pen_at = (lerp(end[0], ck[0], u), lerp(end[1], ck[1], u)) if u < 1 else ck
        if T > 21.62: pen_at = (ck[0] + 260 * eic((T - 21.62) / 0.4), ck[1] + 220 * eic((T - 21.62) / 0.4))
    if pen_at and T > 19.6:
        px, py = pen_at; ang = math.radians(-58); L_ = 300; wv = 13
        dx, dy = math.cos(ang), math.sin(ang); nx, ny = -dy, dx
        tipp = (px, py); b0 = (px + dx * 40, py + dy * 40); b1 = (px + dx * L_, py + dy * L_)
        body = [(b0[0] + nx * wv, b0[1] + ny * wv), (b1[0] + nx * wv, b1[1] + ny * wv), (b1[0] - nx * wv, b1[1] - ny * wv), (b0[0] - nx * wv, b0[1] - ny * wv)]
        cone = [tipp, (b0[0] + nx * wv, b0[1] + ny * wv), (b0[0] - nx * wv, b0[1] - ny * wv), tipp]
        a = app(T - 19.6, 0.15)
        erase(fr, body + [body[0]]); erase(fr, cone); tint(fr, body, 0.06)
        stroke(fr, body + [body[0]], 0.85 * a, 2, 0.4); stroke(fr, cone, 0.85 * a, 2, 0.4)
        line(fr.core, (b0[0] + dx * 60 + nx * wv, b0[1] + dy * 60 + ny * wv), (b0[0] + dx * 60 - nx * wv, b0[1] + dy * 60 - ny * wv), 0.5 * a, 1)
        if 20.4 <= T < 21.36: circle(fr.gin, tipp, 6, 3.0, fill=True)
    z = 1.1 + 0.08 * eio((T - t0) / 3.0) + 0.12 * eic((T - 21.3) / 0.7)
    return fr, (z, 400, ROWS[2] - 30, 0, 0)

# ------------------------------------------------------------------ B4  "I'll check in with you at the end of the week"
DAYS = 'MTWTFSS'; BS, BG = 112, 22; BX0 = (W - (7 * BS + 6 * BG)) / 2; BY = 800
def bx(i): return BX0 + i * (BS + BG)
def B4(T):
    fr = Frame(); t0 = 22.25
    put_text(fr, 'WEEK 37', MONO, 24, BX0, 690, t0 + 0.05, T, anchor='ls', track=0.2, a=0.5, typed=0.25)
    for i, d in enumerate(DAYS):
        ti = t0 + 0.03 + i * 0.045; p = eoq((T - ti) / 0.4)
        if p <= 0: continue
        fri = i == 4
        on = fri and T >= 23.40
        sq = rect_pts(bx(i), BY, bx(i) + BS, BY + BS)
        if on:
            fillpoly(fr.acc, sq[:-1], 0.85 * app(T - 23.40, 0.06)); fr.gin += 0  # filled orange
        stroke(fr, partial(sq, p), 0.85 if i < 5 else 0.4, 2, 0.5 + spike(T - ti, 0.12, 1.5))
        L = text(d, MONO, 30, bx(i) + BS / 2, BY - 22, 'ms')
        bloom_text(fr, L, T - ti - 0.05, peak=3, op=0.75 if i < 5 else 0.35)
        if on:
            Ld = text(d, MONO, 30, bx(i) + BS / 2, BY - 22, 'ms'); fr.core *= (1 - Ld); fr.acc = np.maximum(fr.acc, Ld)
    # hopping light: Mon -> Fri
    hops = [22.42, 22.66, 22.90, 23.14, 23.38]
    for i in range(4):
        if T > hops[i] + 0.22: circle(fr.core, (bx(i) + BS / 2, BY + BS / 2), 7, 0.55, fill=True)
    if hops[0] <= T < 23.42:
        k = min(3, int((T - hops[0]) / 0.24)); u = cl((T - hops[k]) / 0.24)
        xa, xb = bx(k) + BS / 2, bx(k + 1) + BS / 2; x = lerp(xa, xb, eic(u)); y = BY + BS / 2 - 90 * math.sin(math.pi * u)
        circle(fr.core, (x, y), 10, 1.0, fill=True); circle(fr.gin, (x, y), 12, 4.0, fill=True)
    if T >= 23.40: fr.gin += 0; circle(fr.gin, (bx(4) + BS / 2, BY + BS / 2), 60, spike(T - 23.40, 0.12, 6), fill=True)
    # marker circle around Friday
    pr = eoc((T - 23.55) / 0.42)
    if pr > 0:
        c = (bx(4) + BS / 2, BY + BS / 2); pts = []
        for s in np.linspace(0, 1.12, 90):
            a = -2.2 + s * TAU; r = 108 + 10 * math.sin(s * 9) + 14 * s
            pts.append((c[0] + r * math.cos(a) * 1.05, c[1] + r * math.sin(a) * 0.95))
        stroke(fr, partial(pts, pr), 1.0, 5, 2.0 + spike(T - 23.55, 0.15, 3), acc=True)
    put_text(fr, 'CHECK-IN', MONO, 26, bx(4) + BS / 2, BY + BS + 120, 23.70, T, track=0.2, acc=True, typed=0.2)
    z = 1.0 + 0.28 * eio((T - t0 - 0.9) / 1.1); return fr, (z, bx(4) + BS / 2, BY + BS / 2, 0, 0)

# ------------------------------------------------------------------ B5  isometric room: couch reader + desk worker
def box(x0, x1, y0, y1, z0, z1):
    P = np.array([(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], np.float32)
    F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return P, F
class Cam3:
    def __init__(s, yaw, pitch, dist, f, cx, cy, tgt):
        s.cy_, s.sy = math.cos(yaw), math.sin(yaw); s.cp, s.sp = math.cos(pitch), math.sin(pitch)
        s.d, s.f, s.cx, s.cyy, s.t = dist, f, cx, cy, np.array(tgt, np.float32)
    def cam(s, P):
        P = np.asarray(P, np.float32) - s.t; x = P[..., 0] * s.cy_ + P[..., 2] * s.sy; z = -P[..., 0] * s.sy + P[..., 2] * s.cy_; y = P[..., 1]
        y2 = y * s.cp - z * s.sp; z2 = y * s.sp + z * s.cp
        return x, y2, z2 + s.d
    def __call__(s, P):
        x, y, z = s.cam(P); return np.stack([s.cx + s.f * x / z, s.cyy - s.f * y / z], -1), z
def draw_box(fr, C, bx_, a, g=0.5, fillv=0.05, acc=False):
    P, F = bx_; S2, _ = C(P)
    for f in F:
        q = S2[list(f)]; ar = 0.5 * np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])
        if ar > 0: continue                                      # back face
        pts = [tuple(p) for p in q] + [tuple(q[0])]
        erase(fr, pts); tint(fr, pts, fillv); stroke(fr, pts, a, 2, g, acc)
def obj_depth(C, bx_): _, z = C(bx_[0]); return float(z.mean())
def B5(T):
    fr = Frame(); t0 = 25.88; u = eio((T - t0) / 4.5)
    C = Cam3(math.radians(lerp(40, 26, u)), math.radians(27), 9.0, lerp(1180, 1260, u), 540, 860, (0.0, 0.9, -0.3))
    def P2(p): s, _ = C(np.array([p], np.float32)); return tuple(s[0])
    # room shell: floor grid + two walls draw in
    pr = eoq((T - t0) / 0.7)
    fl = [(-3, 0, -2.2), (3, 0, -2.2), (3, 0, 1.6), (-3, 0, 1.6), (-3, 0, -2.2)]
    stroke(fr, partial([P2(p) for p in fl], pr), 0.45, 2, 0.3 + spike(T - t0, 0.15, 1.5))
    for k in range(1, 10):
        x = -3 + k * 0.6; pk = eoq((T - t0 - 0.1 - k * 0.025) / 0.5)
        if pk > 0: line(fr.core, P2((x, 0, -2.2)), P2((x, 0, lerp(-2.2, 1.6, pk))), 0.12, 1)
    for k in range(1, 7):
        z = -2.2 + k * 0.6 * 0.95; pk = eoq((T - t0 - 0.1 - k * 0.03) / 0.5)
        if pk > 0: line(fr.core, P2((-3, 0, z)), P2((lerp(-3, 3, pk), 0, z)), 0.12, 1)
    wb = [(-3, 0, -2.2), (-3, 2.6, -2.2), (3, 2.6, -2.2), (3, 0, -2.2)]; wl = [(-3, 0, 1.6), (-3, 2.6, 1.6), (-3, 2.6, -2.2)]
    stroke(fr, partial([P2(p) for p in wb], pr), 0.4, 2, 0.3); stroke(fr, partial([P2(p) for p in wl], pr), 0.4, 2, 0.3)
    pw = eoq((T - t0 - 0.3) / 0.5)
    if pw > 0:
        win = [(-0.6, 1.1, -2.2), (0.9, 1.1, -2.2), (0.9, 2.2, -2.2), (-0.6, 2.2, -2.2), (-0.6, 1.1, -2.2)]
        stroke(fr, partial([P2(p) for p in win], pw), 0.5, 2, 0.4)
        line(fr.core, P2((0.15, 1.1, -2.2)), P2((0.15, lerp(1.1, 2.2, pw), -2.2)), 0.4, 1); line(fr.core, P2((-0.6, 1.65, -2.2)), P2((lerp(-0.6, 0.9, pw), 1.65, -2.2)), 0.4, 1)
        # moon light on the floor through the window
    # objects (appear time, list of boxes, alpha, acc)
    OBJ = []
    couch = [box(-2.7, -0.7, 0, 0.42, -1.9, -1.05), box(-2.7, -0.7, 0, 0.98, -2.12, -1.88), box(-2.92, -2.7, 0, 0.62, -2.12, -1.05), box(-0.7, -0.48, 0, 0.62, -2.12, -1.05)]
    OBJ += [(26.55, b, 0.9, False, 'couch') for b in couch]
    desk = [box(0.6, 2.7, 0.72, 0.8, -2.05, -1.25)] + [box(x, x + 0.06, 0, 0.72, z, z + 0.06) for x in (0.66, 2.58) for z in (-1.98, -1.36)]
    OBJ += [(26.80, b, 0.9, False, 'desk') for b in desk]
    chair = [box(1.45, 1.95, 0.38, 0.46, -1.0, -0.55), box(1.45, 1.95, 0.46, 0.72, -0.6, -0.54), box(1.66, 1.74, 0, 0.38, -0.81, -0.74)]
    OBJ += [(26.90, b, 0.8, False, 'chair') for b in chair]
    reader = [box(-1.95, -1.45, 0.42, 1.08, -1.78, -1.5), box(-1.95, -1.47, 0.42, 0.56, -1.5, -1.1), box(-1.93, -1.49, 0, 0.42, -1.12, -0.98)]
    OBJ += [(27.30, b, 1.0, False, 'reader') for b in reader]
    worker = [box(1.47, 1.93, 0.46, 1.12, -1.0, -0.72), box(1.47, 1.93, 0.46, 0.58, -1.32, -1.0), box(1.49, 1.91, 0, 0.46, -1.36, -1.22)]
    OBJ += [(27.50, b, 1.0, False, 'worker') for b in worker]
    lap = [box(1.42, 1.98, 0.8, 0.83, -1.78, -1.45)]
    OBJ += [(27.0, b, 0.9, False, 'lap') for b in lap]
    lamp = [box(-0.32, -0.26, 0, 1.55, -2.0, -1.94)]
    OBJ += [(26.7, b, 0.6, False, 'lamp') for b in lamp]
    items = [(obj_depth(C, b), ta, b, a, ac, nm) for ta, b, a, ac, nm in OBJ if T >= ta]
    heads = {'reader': ((-1.7, 1.27, -1.62), 27.30), 'worker': ((1.70, 1.32, -0.88), 27.50)}
    for nm, (hp, ta) in heads.items():
        if T >= ta: _, z = C(np.array([hp])); items.append((float(z[0]) - 0.01, ta, ('head', hp), 1.0, False, nm))
    items.sort(key=lambda r: -r[0])
    for dep, ta, b, a, ac, nm in items:
        dt = T - ta; ap = app(dt, 0.1) * a; g = 0.5 + spike(dt, 0.12, 3)
        if nm == 'couch': g += spike(T - 28.26, 0.15, 2.5)
        if isinstance(b[0], str):
            c2, z = C(np.array([b[1]])); r = C.f * 0.2 / float(z[0]); c = tuple(c2[0])
            pts = ell_pts(c, r, r); erase(fr, pts); tint(fr, pts, 0.05); stroke(fr, pts, ap, 2, g)
            continue
        draw_box(fr, C, b, ap, g)
    # book in the reader's hands: a page that lights up on "read"
    if T >= 27.30:
        bk = [(-1.92, 0.82, -1.36), (-1.48, 0.82, -1.36), (-1.48, 1.04, -1.42), (-1.92, 1.04, -1.42), (-1.92, 0.82, -1.36)]
        pts = [P2(p) for p in bk]; erase(fr, pts); lit = cl((T - 28.70) / 0.12)
        stroke(fr, pts, app(T - 27.3, 0.1), 2, 0.5); line(fr.core, P2((-1.70, 0.82, -1.36)), P2((-1.70, 1.04, -1.42)), 0.8, 1)
        if lit > 0: fillpoly(fr.core, pts[:-1], 0.85 * lit); fillpoly(fr.gin, pts[:-1], lit * (1.2 + spike(T - 28.7, 0.15, 5)))
    # lamp shade glow
    if T >= 26.7:
        sh = [P2(p) for p in [(-0.48, 1.45, -1.97), (-0.1, 1.45, -1.97), (-0.18, 1.72, -1.97), (-0.40, 1.72, -1.97), (-0.48, 1.45, -1.97)]]
        erase(fr, sh); stroke(fr, sh, 0.7, 2, 0.6); fillpoly(fr.gin, sh[:-1], 0.6)
    # laptop screen (orange, brightens on "admin")
    if T >= 27.0:
        sc = [P2(p) for p in [(1.44, 0.83, -1.78), (1.96, 0.83, -1.78), (1.96, 1.18, -1.86), (1.44, 1.18, -1.86), (1.44, 0.83, -1.78)]]
        erase(fr, sc); br = 0.35 + 0.55 * cl((T - 29.35) / 0.15)
        fillpoly(fr.acc, sc[:-1], br * app(T - 27.0, 0.1)); stroke(fr, sc, 0.9, 2, 0.4)
        fr.gin += 0
        if T > 29.35: circle(fr.gin, P2((1.7, 1.0, -1.82)), 40, spike(T - 29.35, 0.15, 3), fill=True)
    # dashed link between the two heads: one person reads, the other gets the work done
    pl = eic((T - 29.55) / 0.5)
    if pl > 0:
        a_, b_ = P2((-1.7, 1.62, -1.62)), P2((1.70, 1.67, -0.88)); mid = ((a_[0] + b_[0]) / 2, min(a_[1], b_[1]) - 170)
        curve = [((1 - s) ** 2 * a_[0] + 2 * (1 - s) * s * mid[0] + s * s * b_[0], (1 - s) ** 2 * a_[1] + 2 * (1 - s) * s * mid[1] + s * s * b_[1]) for s in np.linspace(0, 1, 80)]
        part = partial(curve, pl)
        for k in range(0, len(part) - 1, 4): stroke(fr, part[k:k + 3], 0.9, 2, 0.8, acc=True)
        circle(fr.acc, part[-1], 7, 1.0, fill=True); circle(fr.gin, part[-1], 10, 3, fill=True)
    return fr, (1.0 + 0.05 * u, 540, 900, 0, 0)

# ------------------------------------------------------------------ B6  funnel: many readers in, a few buyers out
FTOP, FNECK = 330, 1010
def fw(y): return 24 + 356 * cl((FNECK - y) / (FNECK - FTOP)) ** 1.7
_r6 = rnd(66); NP = 720
P6 = dict(ts=_r6.uniform(34.25, 37.9, NP), xr=_r6.uniform(-0.93, 0.93, NP), v=_r6.uniform(560, 820, NP), die=_r6.uniform(0.25, 0.97, NP), rr=_r6.uniform(2.2, 3.8, NP))
BUY = [36.62, 36.85, 37.05, 37.30, 37.52, 37.78, 38.0]
def B6(T):
    fr = Frame(); t0 = 34.40
    pf = eoq((T - t0) / 0.6)
    L_ = [(540 - fw(y), y) for y in np.linspace(FTOP, FNECK, 60)] + [(540 - 24, FNECK + 90)]
    R_ = [(540 + fw(y), y) for y in np.linspace(FTOP, FNECK, 60)] + [(540 + 24, FNECK + 90)]
    g = 0.6 + spike(T - t0, 0.15, 2)
    stroke(fr, partial(L_, pf), 0.9, 2, g); stroke(fr, partial(R_, pf), 0.9, 2, g)
    stroke(fr, partial(ell_pts((540, FTOP), 380, 46), pf), 0.7, 2, g)
    for k in range(1, 6):                                             # contour rings
        y = FTOP + (FNECK - FTOP) * (k / 6) ** 0.8; pk = eoq((T - t0 - 0.2 - k * 0.05) / 0.4)
        if pk > 0: stroke(fr, partial(ell_pts((540, y), fw(y), 46 * fw(y) / 380 + 2), pk), 0.18, 1, 0.1)
    # readers falling in
    for i in range(NP):
        dt = T - P6['ts'][i]
        if dt < 0: continue
        y = 60 + P6['v'][i] * dt + 160 * dt * dt
        if y > FTOP: x = 540 + P6['xr'][i] * fw(y)
        else: x = 540 + P6['xr'][i] * 380
        dd = FTOP + P6['die'][i] * (FNECK - FTOP); a = 0.85
        if y > dd: a *= max(0, 1 - (y - dd) / 70)
        if a <= 0.01: continue
        circle(fr.core, (x, y), P6['rr'][i], a, fill=True)
    # buyers: pass through the neck and line up below, orange
    for k, tb in enumerate(BUY):
        if T < tb - 0.5: continue
        u = (T - (tb - 0.5)) / 0.5
        if u < 1: x = 540 + (k % 2 * 2 - 1) * 0.2 * fw(lerp(700, FNECK, u)) * (1 - u); y = lerp(700, FNECK + 60, u * u); acc = u > 0.8
        else:
            v = eoq((T - tb) / 0.45); tx = 540 + (k - 3) * 54; x = lerp(540, tx, v); y = lerp(FNECK + 60, 1190, v); acc = True
        if acc:
            circle(fr.acc, (x, y), 9, 1.0, fill=True); circle(fr.gin, (x, y), 11, 2.0 + spike(T - tb, 0.12, 5), fill=True)
        else: circle(fr.core, (x, y), 4, 1.0, fill=True)
    # clock: sweeps on "don't have the time"
    if T > 36.25:
        c = (860, 1120); r = 58; a = app(T - 36.25, 0.1)
        stroke(fr, ell_pts(c, r, r), 0.7 * a, 2, 0.5 + spike(T - 36.25, 0.12, 2))
        for k in range(12):
            an = k * TAU / 12; line(fr.core, (c[0] + 0.82 * r * math.cos(an), c[1] + 0.82 * r * math.sin(an)), (c[0] + 0.94 * r * math.cos(an), c[1] + 0.94 * r * math.sin(an)), 0.6 * a, 1)
        an = -math.pi / 2 + (T - 36.25) * 9.0
        line(fr.core, c, (c[0] + 0.78 * r * math.cos(an), c[1] + 0.78 * r * math.sin(an)), a, 2)
        an2 = -math.pi / 2 + (T - 36.25) * 0.75
        line(fr.core, c, (c[0] + 0.5 * r * math.cos(an2), c[1] + 0.5 * r * math.sin(an2)), a, 3)
    z = 1.0 + 0.10 * eio((T - t0) / 4.1); return fr, (z, 540, lerp(700, 1150, eio((T - t0) / 4.1)), 0, 0)

# ------------------------------------------------------------------ B7  "YC is similar in shape. Tons of their advice is free."
def ring_shape(fr, c, T, ta, a=1.0, scale=1.0):
    dt = T - ta
    if dt < 0: return
    n = 24; r = 150 * scale
    for k in range(n):
        an = -math.pi / 2 + k * TAU / n; p = app(dt - k * 0.012, 0.1)
        if p <= 0: continue
        circle(fr.core, (c[0] + r * math.cos(an), c[1] + r * math.sin(an)), 7 * scale, a * p, fill=True)
        fr.gin[0:1] += 0
    stroke(fr, ell_pts(c, r * 1.32, r * 1.32), 0.25 * a * app(dt, 0.3), 1, 0.2)
    for k in range(n):
        an = -math.pi / 2 + k * TAU / n; p = app(dt - 0.25 - k * 0.01, 0.15)
        if p > 0: line(fr.core, (c[0] + r * 0.30 * math.cos(an), c[1] + r * 0.30 * math.sin(an)), (c[0] + r * 0.82 * math.cos(an), c[1] + r * 0.82 * math.sin(an)), 0.18 * a * p, 1)
    circle(fr.acc, c, 24 * scale, a * app(dt - 0.3, 0.1), fill=True)
    circle(fr.gin, c, 30 * scale, a * (1 + spike(dt - 0.3, 0.12, 4)), fill=True)
_r7 = rnd(77); NCARD = 54
C7 = dict(ang=_r7.uniform(0, TAU, NCARD), dist=_r7.uniform(220, 900, NCARD), dep=_r7.uniform(0.55, 1.35, NCARD), rot=_r7.uniform(-0.5, 0.5, NCARD),
          spin=_r7.uniform(-0.4, 0.4, NCARD), dl=_r7.uniform(0, 0.35, NCARD), free=_r7.random(NCARD) < 0.3, lines=_r7.integers(2, 5, NCARD))
def B7(T):
    fr = Frame(); t0 = 39.85; CY = 820
    slide = eiq((T - 40.62) / 0.6); fade = 1 - cl((T - 41.70) / 0.2)
    if fade > 0:
        lx = lerp(300, 540, slide); rx_ = lerp(780, 540, slide)
        ring_shape(fr, (lx, CY), T, 39.90, a=fade); ring_shape(fr, (rx_, CY), T, 39.95, a=fade)
        if T > 41.2: circle(fr.gin, (540, CY), 190, spike(T - 41.22, 0.15, 1.2), fill=False)
        la = (1 - cl((T - 40.55) / 0.15)) * fade
        if la > 0:
            put_text(fr, 'MOCHARY', MONO, 26, 300, CY + 255, 39.95, T, track=0.2, a=0.7 * la)
            put_text(fr, 'YC', MONO, 26, 780, CY + 255, 40.0, T, track=0.2, a=0.7 * la)
        if T > 40.62:
            put_text(fr, 'SAME SHAPE', MONO, 24, 540, CY + 255, 41.22, T, track=0.25, a=0.6 * fade, typed=0.25)
    if T > 41.62:
        order = np.argsort(C7['dep'])
        for i in order:
            dt = T - 41.66 - C7['dl'][i]
            if dt < 0: continue
            u = eoq(dt / 0.75); d = C7['dep'][i]; an = C7['ang'][i]
            dist = C7['dist'][i] * u + 30 * dt
            c = (540 + math.cos(an) * dist, CY + math.sin(an) * dist * 1.25 + 40 * dt * d)
            s = d * lerp(0.3, 1.0, u); w_, h_ = 92 * s, 120 * s; ang = C7['rot'][i] + C7['spin'][i] * dt
            pts = rot_rect(c, w_, h_, ang); a = cl(0.35 + 0.6 * (d - 0.55) / 0.8) * app(dt, 0.08)
            erase(fr, pts); tint(fr, pts, 0.05 * d)
            fl = 42.70 <= T and C7['free'][i]
            stroke(fr, pts, a, 2, 0.4 + spike(dt, 0.12, 1.5), acc=fl)
            ca, sa = math.cos(ang), math.sin(ang)
            for k in range(int(C7['lines'][i])):
                yy = -h_ / 2 + h_ * (0.22 + 0.15 * k); x0_, x1_ = -w_ * 0.32, w_ * (0.32 if k % 2 == 0 else 0.1)
                line(fr.core, (c[0] + x0_ * ca - yy * sa, c[1] + x0_ * sa + yy * ca), (c[0] + x1_ * ca - yy * sa, c[1] + x1_ * sa + yy * ca), a * 0.5, 1)
            if fl:
                yy = h_ * 0.30; x0_, x1_ = -w_ * 0.32, w_ * 0.32
                line(fr.acc, (c[0] + x0_ * ca - yy * sa, c[1] + x0_ * sa + yy * ca), (c[0] + x1_ * ca - yy * sa, c[1] + x1_ * sa + yy * ca), 1.0, max(2, int(6 * s)))
                fr.gin += 0
        if T > 42.7: circle(fr.gin, (540, CY), 500, spike(T - 42.72, 0.12, 0.5), fill=True)
        ring_shape(fr, (540, CY), T, 39.9, a=0.0)
        circle(fr.acc, (540, CY), 24, 1.0, fill=True); circle(fr.gin, (540, CY), 30, 1.2, fill=True)
    z = 1.0 + 0.04 * eio((T - t0) / 1.8) - 0.06 * eic((T - 41.62) / 0.8); return fr, (z, 540, CY, 0, 0)

# ------------------------------------------------------------------ B8  "give up seven percent for a demo day deadline and the batch"
PC = (540, 760); PR = 270; SL = [0.0, 0.07, 0.36, 0.62, 0.80, 1.0]
def wedge_pts(c, r, a0, a1, n=40):
    return [c] + [(c[0] + r * math.cos(a), c[1] + r * math.sin(a)) for a in np.linspace(a0, a1, n)] + [c]
def B8(T):
    fr = Frame(); t0 = 43.38
    A = lambda f: -math.pi / 2 + f * TAU
    pieA = 1 - cl((T - 45.25) / 0.25)
    if pieA > 0:
        pd = eoq((T - t0) / 0.6); out = eoq((T - 44.62) / 0.45)
        # rest of pie
        stroke(fr, partial(ell_pts(PC, PR, PR, A(SL[1]), A(1.0), 120), pd), 0.9 * pieA, 2, 0.5 + spike(T - t0, 0.15, 2))
        for k, f in enumerate(SL[1:-1]):
            pk = eoq((T - t0 - 0.2 - k * 0.07) / 0.35)
            if pk > 0: stroke(fr, [PC, (PC[0] + PR * pk * math.cos(A(f)), PC[1] + PR * pk * math.sin(A(f)))], 0.55 * pieA, 2, 0.3)
        for k in range(1, 5):
            stroke(fr, partial(ell_pts(PC, PR * k / 5, PR * k / 5, A(0.07), A(1.0), 80), pd), 0.08 * pieA, 1, 0.05)
        # the 7% slice
        mid = A(0.035); off = 70 * out; c7 = (PC[0] + off * math.cos(mid), PC[1] + off * math.sin(mid))
        wp = wedge_pts(c7, PR + 8 * out, A(0), A(0.07))
        if pd > 0.3:
            if out > 0: fillpoly(fr.acc, wp[:-1], 0.9 * cl(out * 3) * pieA); fillpoly(fr.gin, wp[:-1], (1 + spike(T - 44.62, 0.15, 5)) * pieA)
            stroke(fr, wp, pieA, 2, 0.6, acc=out > 0)
        put_text(fr, '7%', SERIF, 190, 540, 1230, 44.66, T, a=pieA, peak=6)
        put_text(fr, 'FOUNDER EQUITY', MONO, 24, 540, 420, t0 + 0.15, T, track=0.25, a=0.5 * pieA, typed=0.3)
    # countdown ring
    if T > 45.20:
        a = app(T - 45.20, 0.15) * (1 - cl((T - 46.72) / 0.12)); u = cl((T - 45.35) / 1.3)
        if a > 0:
            stroke(fr, ell_pts(PC, PR, PR, A(u), A(1.0), 160), a, 4, 0.8 + spike(T - 45.2, 0.15, 2))
            stroke(fr, ell_pts(PC, PR, PR), 0.15 * a, 2, 0.1)
            for k in range(60):
                an = A(k / 60); l1 = PR + 22; l2 = PR + (40 if k % 5 == 0 else 32)
                line(fr.core, (PC[0] + l1 * math.cos(an), PC[1] + l1 * math.sin(an)), (PC[0] + l2 * math.cos(an), PC[1] + l2 * math.sin(an)), (0.6 if k % 5 == 0 else 0.3) * a, 1)
            hd = (PC[0] + PR * math.cos(A(u)), PC[1] + PR * math.sin(A(u))); circle(fr.acc, hd, 10, a, fill=True); circle(fr.gin, hd, 14, 2.5 * a, fill=True)
            wk = max(0, 12 - int(u * 12.999))
            L = text(f'{wk:02d}', SERIF, 200, PC[0], PC[1] + 70, 'ms'); fr.core = np.maximum(fr.core, L * a); fr.gin += L * a * (0.8 + 2.5 * math.exp(-((T - 45.35) % (1.3 / 12)) / 0.04))
            L2 = text('WEEKS TO DEMO DAY', MONO, 22, PC[0], PC[1] + 130, 'ms', 0.22); fr.core = np.maximum(fr.core, L2 * a * 0.6); fr.gin += L2 * a * 0.4
    # the batch: a grid of founders
    if T > 46.70:
        for r_ in range(9):
            for c_ in range(8):
                x = 540 + (c_ - 3.5) * 92; y = 760 + (r_ - 4) * 92; d = math.hypot(x - 540, y - 760)
                dt = T - 46.72 - d / 1400; p = eoq(dt / 0.25)
                if p <= 0: continue
                me = (r_, c_) == (4, 4)
                circle(fr.acc if me else fr.core, (x, y), 16 * back(dt / 0.3), 1.0 if me else 0.85, fill=me, w=2)
                circle(fr.gin, (x, y), 16, (2.5 if me else 0.6) + spike(dt, 0.12, 2), fill=False, w=3)
    z = 1.0 + 0.07 * eio((T - t0) / 4.4); return fr, (z, 540, 760, 0, 0)

# ------------------------------------------------------------------ B9  machine that just does the job
M9 = 24
GEARS = [dict(N=20, c=(400, 600)), dict(N=13), dict(N=9)]
def gear_layout():
    g1, g2, g3 = GEARS; rp = lambda g: M9 * g['N'] / 2
    a12 = math.radians(28); g2['c'] = (g1['c'][0] + (rp(g1) + rp(g2)) * math.cos(a12), g1['c'][1] + (rp(g1) + rp(g2)) * math.sin(a12)); g2['a'] = a12
    a23 = math.radians(112); g3['c'] = (g2['c'][0] + (rp(g2) + rp(g3)) * math.cos(a23), g2['c'][1] + (rp(g2) + rp(g3)) * math.sin(a23)); g3['a'] = a23
gear_layout()
def gear_pts(c, N, phi):
    rp = M9 * N / 2; ro, rr = rp + M9 * 0.9, rp - M9 * 1.05; tau = TAU / N; pts = []
    for k in range(N):
        th = phi + k * tau
        for fa, r in ((-0.5, rr), (-0.25, rr), (-0.11, ro), (0.11, ro), (0.25, rr)):
            pts.append((c[0] + r * math.cos(th + fa * tau), c[1] + r * math.sin(th + fa * tau)))
    return pts + [pts[0]]
def B9(T):
    fr = Frame(); t0 = 48.95
    sp = eic((T - t0) / 0.6); phi1 = 0.95 * (T - t0) - 0.95 * 0.3 * (1 - sp)
    g1, g2, g3 = GEARS; tau = lambda g: TAU / g['N']
    ph = [phi1]
    ph.append(-(g1['N'] / g2['N']) * (ph[0] - g2['a']) + g2['a'] + math.pi + tau(g2) / 2)
    ph.append(-(g2['N'] / g3['N']) * (ph[1] - g3['a']) + g3['a'] + math.pi + tau(g3) / 2)
    for i, g in enumerate(GEARS):
        ta = t0 + 0.05 + i * 0.12; p = eoq((T - ta) / 0.55)
        if p <= 0: continue
        pts = gear_pts(g['c'], g['N'], ph[i]); erase(fr, pts); tint(fr, pts, 0.05)
        stroke(fr, partial(pts, p), 0.95, 2, 0.6 + spike(T - ta, 0.15, 2))
        rp = M9 * g['N'] / 2; c = g['c']
        stroke(fr, partial(ell_pts(c, rp * 0.62, rp * 0.62), p), 0.35, 1, 0.2)
        stroke(fr, ell_pts(c, rp * 0.2, rp * 0.2), 0.9 * p, 2, 0.5)
        nh = 5 if g['N'] > 10 else 4
        for k in range(nh):
            an = ph[i] + k * TAU / nh; hc = (c[0] + rp * 0.42 * math.cos(an), c[1] + rp * 0.42 * math.sin(an))
            stroke(fr, ell_pts(hc, rp * 0.13, rp * 0.13, n=40), 0.6 * p, 2, 0.3)
        circle(fr.acc if i == 2 else fr.core, c, 7, p, fill=True)
    # conveyor: identical parcels, perfectly spaced, checked by a light gate
    y = 1240; pc = eoq((T - t0 - 0.2) / 0.6)
    stroke(fr, partial([(110, y), (970, y)], pc), 0.8, 2, 0.4); stroke(fr, partial([(110, y + 34), (970, y + 34)], pc), 0.4, 1, 0.2)
    for k in range(12):
        x = 140 + k * 74; an = -(T - t0) * 4.0
        if pc > (x - 110) / 860:
            circle(fr.core, (x, y + 17), 13, 0.5, w=1); line(fr.core, (x, y + 17), (x + 13 * math.cos(an), y + 17 + 13 * math.sin(an)), 0.5, 1)
    gx = g3['c'][0]
    if T > t0 + 0.5:
        ga = app(T - t0 - 0.5, 0.2); line(fr.acc, (gx, g3['c'][1] + 120), (gx, y - 4), 0.5 * ga, 1); fr.gin[int(g3['c'][1] + 120):int(y), int(gx) - 1:int(gx) + 2] += 0.6 * ga
    v = 150; sp_ = 150
    for k in range(-2, 8):
        x = 110 + ((T - t0) * v) % sp_ + k * sp_ - sp_
        if x < 90 or x > 990: continue
        a = app(T - t0 - 0.4, 0.2) * cl((x - 90) / 40) * cl((990 - x) / 40)
        bp = rect_pts(x - 30, y - 62, x + 30, y - 2); erase(fr, bp); tint(fr, bp, 0.06)
        done = x > gx
        stroke(fr, bp, a, 2, 0.4, acc=False)
        line(fr.core, (x - 30, y - 44), (x + 30, y - 44), 0.35 * a, 1)
        if done:
            check(fr, x - 14, y - 36, 28, 1.0, a, acc=True, g=1.0);
            k_ = (x - gx) / v
            if k_ < 0.2: circle(fr.gin, (gx, y - 32), 50, spike(k_, 0.06, 3), fill=True)
    z = 1.0 + 0.07 * eio((T - t0) / 3.7); return fr, (z, 540, 860, 0, 0)

# ------------------------------------------------------------------ B10  habit loop; behaviour change breaks out
LC = (540, 820); LR = 230; TEX = 54.40
def loop_angle(T): return -math.pi / 2 + (T - 52.62) * TAU / 1.05
def B10(T):
    fr = Frame(); t0 = 52.62
    p = eoq((T - t0) / 0.5); dim = 1 - 0.7 * cl((T - TEX) / 0.5)
    for k, (dr, a) in enumerate(((0, 0.45), (-10, 0.14), (10, 0.14), (-20, 0.07), (20, 0.07))):
        stroke(fr, partial(ell_pts(LC, LR + dr, LR + dr, -math.pi / 2, 1.5 * math.pi, 140), p), a * dim, 1 if k else 2, 0.2)
    # arrowheads around the loop (direction of the habit)
    for k in range(4):
        an = -math.pi / 2 + k * TAU / 4 + 0.4; c = (LC[0] + LR * math.cos(an), LC[1] + LR * math.sin(an)); tg = an + math.pi / 2
        pts = [(c[0] - 14 * math.cos(tg - 0.5), c[1] - 14 * math.sin(tg - 0.5)), c, (c[0] - 14 * math.cos(tg + 0.5), c[1] - 14 * math.sin(tg + 0.5))]
        stroke(fr, pts, 0.5 * p * dim, 2, 0.2)
    if T < TEX:
        an = loop_angle(T)
        for j in range(26):
            a2 = an - j * 0.06; c = (LC[0] + LR * math.cos(a2), LC[1] + LR * math.sin(a2))
            circle(fr.core, c, 9 - j * 0.25, (1 - j / 26) ** 1.5, fill=True)
        c = (LC[0] + LR * math.cos(an), LC[1] + LR * math.sin(an)); circle(fr.gin, c, 12, 3.0, fill=True)
    else:
        an = loop_angle(TEX); e = (LC[0] + LR * math.cos(an), LC[1] + LR * math.sin(an)); tg = (-math.sin(an), math.cos(an))
        tgt = (900, 330); c1 = (e[0] + tg[0] * 280, e[1] + tg[1] * 280); c2 = (tgt[0] - 80, tgt[1] + 260)
        curve = [((1 - s) ** 3 * e[0] + 3 * (1 - s) ** 2 * s * c1[0] + 3 * (1 - s) * s * s * c2[0] + s ** 3 * tgt[0],
                  (1 - s) ** 3 * e[1] + 3 * (1 - s) ** 2 * s * c1[1] + 3 * (1 - s) * s * s * c2[1] + s ** 3 * tgt[1]) for s in np.linspace(0, 1, 120)]
        u = eic((T - TEX) / 0.95); part = partial(curve, u)
        stroke(fr, part, 1.0, 4, 1.5, acc=True)
        hd = part[-1]; circle(fr.acc, hd, 10, 1.0, fill=True); circle(fr.gin, hd, 14, 4.0, fill=True)
        if u >= 1:
            dt = T - TEX - 0.95; r = 26 * back(dt / 0.3)
            stroke(fr, ell_pts(tgt, r, r), 1.0, 3, 2 + spike(dt, 0.12, 4), acc=True)
            stroke(fr, ell_pts(tgt, r + 30 * eoq(dt / 0.6), r + 30 * eoq(dt / 0.6)), 0.6 * (1 - cl(dt / 0.6)), 2, 0.5, acc=True)
    z = 1.0 + 0.06 * eio((T - t0) / 3.1); dx = -90 * eio((T - TEX) / 1.2); dy = 150 * eio((T - TEX) / 1.2)
    return fr, (z, 540, 820, dx, dy)

# ------------------------------------------------------------------ B11  fitness / coaching / new software
def plate(fr, x, cy, w, h, a, g):
    pts = [(x - w / 2, cy - h / 2), (x + w / 2, cy - h / 2), (x + w / 2, cy + h / 2), (x - w / 2, cy + h / 2), (x - w / 2, cy - h / 2)]
    erase(fr, pts); tint(fr, pts, 0.06); stroke(fr, pts, a, 2, g)
    line(fr.core, (x, cy - h / 2 + 10), (x, cy + h / 2 - 10), a * 0.3, 1)
def B11(T):
    fr = Frame()
    if T < 56.50:                                                 # dumbbell
        ta = 55.72; lift = eio((T - ta - 0.15) / 0.5); cy = 840 - 120 * lift; tilt = 0
        g = 0.5 + spike(T - ta, 0.15, 2)
        pb = eoq((T - ta) / 0.3)
        stroke(fr, [(540 - 360 * pb, cy), (540 + 360 * pb, cy)], 0.9, 6, g)
        for s in (-1, 1):
            for k, (dx, w, h) in enumerate(((170, 34, 300), (212, 34, 250), (252, 30, 190))):
                if T > ta + 0.05 + k * 0.05: plate(fr, 540 + s * dx, cy, w, h, app(T - ta - 0.05 - k * 0.05, 0.08), g)
            stroke(fr, [(540 + s * 145, cy - 30), (540 + s * 145, cy + 30)], 0.8, 3, g)
        for k in range(9): line(fr.core, (440 + k * 25, cy - 9), (452 + k * 25, cy + 9), 0.5, 1)  # knurling
        stroke(fr, [(220, 1060), (860, 1060)], 0.3, 1, 0.1)
        shadow = ell_pts((540, 1075), 380 - 60 * lift, 14); stroke(fr, shadow, 0.15, 1, 0.05)
        return fr, (1.0 + 0.05 * eio((T - ta) / 0.8), 540, 820, 0, 0)
    if T < 57.15:                                                 # 1-on-1: two chairs facing
        ta = 56.50; g = 0.5 + spike(T - ta, 0.15, 2); p = eoq((T - ta) / 0.35)
        for s in (-1, 1):
            x = 540 + s * 230; seat = 880
            ch = [(x + s * 100, 560 + 140), (x + s * 100, seat), (x - s * 90, seat), (x - s * 90, 1080)]
            stroke(fr, partial(ch, p), 0.95, 3, g); stroke(fr, partial([(x + s * 100, seat), (x + s * 100, 1080)], p), 0.95, 3, g)
            hip = (x + s * 62, seat - 10); neck = (x + s * 38, 712); hc = (x + s * 30, 650)
            knee = (x - s * 92, seat - 22); foot = (x - s * 104, 1080)
            stroke(fr, partial(ell_pts(hc, 44, 44), p), 1.0, 3, g)
            stroke(fr, partial([neck, hip, knee, foot], p), 1.0, 4, g)
            stroke(fr, partial([(neck[0] - s * 6, neck[1] + 40), (x - s * 40, 800), (x - s * 70, 830)], p), 0.8, 3, g * 0.8)
        pl = eic((T - ta - 0.2) / 0.35)
        if pl > 0:
            a_, b_ = (540 - 150, 640), (540 + 150, 640)
            for k in range(9):
                xk = lerp(a_[0], b_[0], k / 8)
                if (k / 8) <= pl: circle(fr.core, (xk, 640), 4, 0.8, fill=True)
            xd = lerp(a_[0], b_[0], (0.5 + 0.5 * math.sin((T - ta) * 9)))
            circle(fr.acc, (xd, 640), 9, pl, fill=True); circle(fr.gin, (xd, 640), 12, 3 * pl, fill=True)
        stroke(fr, [(160, 1080), (920, 1080)], 0.3, 1, 0.1)
        return fr, (1.0 + 0.05 * eio((T - ta) / 0.65), 540, 820, 0, 0)
    ta = 57.15; g = 0.5 + spike(T - ta, 0.15, 2)                  # install progress bar
    x0, x1, y0, h = 160, 920, 800, 64; pb = eoq((T - ta) / 0.3)
    stroke(fr, partial(rect_pts(x0, y0, x1, y0 + h), pb), 0.9, 2, g)
    keys = [(57.25, 0.0), (57.45, 0.18), (57.62, 0.22), (57.85, 0.55), (58.0, 0.61), (58.25, 0.93), (58.38, 1.0)]
    v = 0.0
    for (ta_, va), (tb_, vb) in zip(keys, keys[1:]):
        if T >= ta_: v = lerp(va, vb, eic((T - ta_) / (tb_ - ta_)))
    done = T >= 58.38
    if v > 0:
        fx = x0 + 6 + (x1 - x0 - 12) * v; pts = rect_pts(x0 + 6, y0 + 6, fx, y0 + h - 6)
        fillpoly(fr.acc if done else fr.core, pts[:-1], 0.95); fillpoly(fr.gin, pts[:-1], 1.0 + spike(T - 58.38, 0.12, 5))
        for k in range(int((fx - x0) / 22)):
            xx = x0 + 10 + k * 22; line(fr.core, (xx, y0 + h - 8), (xx + 14, y0 + 8), 0.0 if done else 0.25, 2)
    lbl = 'INSTALLED' if done else 'INSTALLING'
    L = text(lbl, MONO, 26, x0, y0 - 28, 'ls', 0.2); a = app(T - ta - 0.1, 0.1)
    if done: fr.acc = np.maximum(fr.acc, L * a)
    else: fr.core = np.maximum(fr.core, L * a * 0.8)
    fr.gin += L * a * 0.5
    L = text(f'{int(round(v * 100)):3d}%', MONO, 26, x1, y0 - 28, 'rs', 0.1); fr.core = np.maximum(fr.core, L * a * 0.8); fr.gin += L * a * 0.5
    # files streaming into the bar
    r = rnd(int(T * 1000) % 7 + 1)
    for k in range(14):
        ph_ = ((T - ta) * 0.9 + k / 14) % 1.0; x = lerp(x0 + 40, x1 - 40, (k * 0.618) % 1); y = lerp(420, y0 - 60, ph_)
        if T - ta < 0.15 or v >= 1: break
        a2 = math.sin(math.pi * ph_) * 0.6; sz = 16
        stroke(fr, rect_pts(x - sz / 2, y - sz * 0.65, x + sz / 2, y + sz * 0.65), a2, 1, 0.3)
    return fr, (1.0 + 0.06 * eio((T - ta) / 1.45), 540, 820, 0, 0)

BEATS = [('B2', 13.84, 16.47, B2), ('B3', 19.23, 22.25, B3), ('B4', 22.25, 24.25, B4), ('B5', 25.88, 30.40, B5), ('B6', 34.40, 38.55, B6),
         ('B7', 39.85, 43.38, B7), ('B8', 43.38, 47.85, B8), ('B9', 48.95, 52.62, B9), ('B10', 52.62, 55.72, B10), ('B11', 55.72, 58.60, B11)]
CUTS = [55.72, 56.50, 57.15]          # internal hard cuts that get a flash too

def finish(fr, cam):
    z, ax, ay, dx, dy = cam
    M = np.float32([[z, 0, ax * (1 - z) + dx], [0, z, ay * (1 - z) + dy]])
    for k in ('core', 'gin', 'acc'): setattr(fr, k, cv2.warpAffine(getattr(fr, k), M, (W, H), flags=cv2.INTER_LINEAR))
    fr.rgb = cv2.warpAffine(fr.rgb, M, (W, H), flags=cv2.INTER_LINEAR)
    z2 = 1 + (z - 1) * 0.35; M2 = np.float32([[z2, 0, 540 * (1 - z2) + dx * 0.3], [0, z2, 960 * (1 - z2) + dy * 0.3]])
    d = cv2.warpAffine(DOTS, M2, (W, H), flags=cv2.INTER_LINEAR) * 0.075
    fr.rgb += d[..., None] * INK * (1 - np.clip(fr.core, 0, 1))[..., None]
    return fr

def render_frame(name, n, ss=2):
    nm, t0, t1, fn = next(b for b in BEATS if b[0] == name)
    acc = None
    for j in range(ss):
        T = (n + (j + 0.5) / ss * 0.5 - 0.25) / FPS
        T = max(T, t0 + 0.001)
        fr, cam = fn(T); fr = finish(fr, cam)
        if acc is None: acc = fr
        else: acc.add(fr)
    if ss > 1:
        for k in ('rgb', 'core', 'gin', 'acc'): setattr(acc, k, getattr(acc, k) / ss)
    T = n / FPS; starts = [t0] + [c for c in CUTS if t0 <= c < t1]
    st = max(s for s in starts if s <= T + 1e-6) if any(s <= T + 1e-6 for s in starts) else t0
    flash = 0.9 * math.exp(-(T - st) / 0.045)
    return compose(acc, n, flash)
