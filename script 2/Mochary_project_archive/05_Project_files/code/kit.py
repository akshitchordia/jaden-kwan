"""Shared toolkit for the Mochary B-rolls: easing, drawing on a float canvas, glow, flash-bloom text, halftone print."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
W, H = 1080, 1920; FPS = 24000 / 1001
SERIF = S + 'fd/newsreader-600.ttf'; SERIF5 = S + 'fd/newsreader-latin-500-normal.ttf'; MONO = S + 'fd/plexmono-500.ttf'
INK = np.array([1.0, 0.965, 0.915], np.float32)          # warm paper white
ACC = np.array([0.98, 0.47, 0.20], np.float32)           # one burnt-orange accent
BGC = np.array([0.055, 0.050, 0.047], np.float32)

def cl(x): return min(1.0, max(0.0, x))
def eio(x): x = cl(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def eic(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def eiq(x): x = cl(x); return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def back(x, s=1.4): x = cl(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, u): return a + (b - a) * u

class Frame:
    """rgb: lit pixels (premult over black), core: white emissive (text/lines), gin: glow input, acc: orange emissive."""
    def __init__(self):
        self.rgb = np.zeros((H, W, 3), np.float32); self.core = np.zeros((H, W), np.float32)
        self.gin = np.zeros((H, W), np.float32); self.acc = np.zeros((H, W), np.float32)
    def add(self, o, k=1.0):
        self.rgb += o.rgb * k; self.core += o.core * k; self.gin += o.gin * k; self.acc += o.acc * k

P8 = lambda x, y: (int(round(x * 8)), int(round(y * 8)))
def line(L, p0, p1, a=1.0, w=2):
    cv2.line(L, P8(*p0), P8(*p1), float(a), max(1, int(round(w))), cv2.LINE_AA, shift=3)
def poly(L, pts, a=1.0, w=2, closed=False):
    p = np.array([[int(round(x * 8)), int(round(y * 8))] for x, y in pts], np.int32)
    cv2.polylines(L, [p], closed, float(a), max(1, int(round(w))), cv2.LINE_AA, shift=3)
def fillpoly(L, pts, a=1.0):
    p = np.array([[int(round(x * 8)), int(round(y * 8))] for x, y in pts], np.int32)
    cv2.fillPoly(L, [p], float(a), cv2.LINE_AA, shift=3)
def circle(L, c, r, a=1.0, w=2, fill=False):
    cv2.circle(L, P8(*c), int(round(r * 8)), float(a), -1 if fill else max(1, int(round(w))), cv2.LINE_AA, shift=3)
def arc(L, c, r, a0, a1, a=1.0, w=2, n=None):
    n = n or max(8, int(abs(a1 - a0) * r / 6))
    th = np.linspace(a0, a1, n); pts = [(c[0] + r * math.cos(t), c[1] + r * math.sin(t)) for t in th]
    poly(L, pts, a, w)
def partial(pts, p):
    """first fraction p (by length) of a polyline"""
    if p <= 0: return []
    pts = np.array(pts, np.float32); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); tot = seg.sum(); goal = tot * min(1, p)
    out = [tuple(pts[0])]; acc = 0
    for i, s in enumerate(seg):
        if acc + s >= goal:
            f = (goal - acc) / max(s, 1e-6); out.append(tuple(pts[i] + (pts[i + 1] - pts[i]) * f)); return out
        acc += s; out.append(tuple(pts[i + 1]))
    return out

_fcache = {}
def font(path, size):
    k = (path, size)
    if k not in _fcache: _fcache[k] = ImageFont.truetype(path, size)
    return _fcache[k]
_tcache = {}
def text(txt, path, size, x, y, anchor='ms', track=0.0):
    k = (txt, path, size, int(x), int(y), anchor, track)
    if k in _tcache: return _tcache[k]
    f = font(path, size); im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    if track == 0: d.text((x, y), txt, font=f, fill=255, anchor=anchor)
    else:
        tot = sum(f.getlength(c) for c in txt) + track * size * (len(txt) - 1)
        xx = x - tot / 2 if anchor[0] == 'm' else x - tot if anchor[0] == 'r' else x
        for c in txt: d.text((xx, y), c, font=f, fill=255, anchor='l' + anchor[1]); xx += f.getlength(c) + track * size
    a = np.asarray(im).astype(np.float32) / 255
    if len(_tcache) > 400: _tcache.clear()
    _tcache[k] = a; return a
def bloom_text(fr, L, dt, peak=7.0, op=1.0, accent=False):
    """caption-language reveal: blurred white blob -> sharp, glow exposure spike that settles"""
    if dt < 0: return
    s = 6 * math.exp(-dt / 0.06)
    a = np.clip(cv2.GaussianBlur(L, (0, 0), s) * (1 + s * 0.3), 0, 1) if s > 0.25 else L
    a = a * cl(dt / 0.05) * op
    if accent: fr.acc = np.maximum(fr.acc, a)
    else: fr.core = np.maximum(fr.core, a)
    fr.gin += a * (0.6 + peak * math.exp(-dt / 0.085))

def glow_of(a):
    small = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, H)) * wt
    return g

# ---------------- halftone print texture (same as TBH / opener)
CELL = 7.0; _ang = math.radians(45)
Yg, Xg = np.mgrid[0:H, 0:W].astype(np.float32)
_u = (Xg * math.cos(_ang) + Yg * math.sin(_ang)) / CELL; _v = (-Xg * math.sin(_ang) + Yg * math.cos(_ang)) / CELL
DIST = np.sqrt((_u - np.floor(_u) - 0.5) ** 2 + (_v - np.floor(_v) - 0.5) ** 2).astype(np.float32)
_rng = np.random.default_rng(4)
def _n(sig, amp): n = _rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32); return cv2.resize(cv2.GaussianBlur(n, (0, 0), sig), (W, H)) * amp
FIBER = _n(3, 0.035) + _n(0.6, 0.02)
GRAINS = [_rng.normal(0, 0.018, (H, W)).astype(np.float32) for _ in range(6)]
VIGN = np.clip(1 - 0.16 * (((Xg - W / 2) / (W * 0.7)) ** 2 + ((Yg - H / 2) / (H * 0.7)) ** 2), 0.82, 1)[..., None]
ROOM = (np.clip(1 - (((Xg - W / 2) / (W * 0.95)) ** 2 + ((Yg - H * 0.46) / (H * 0.72)) ** 2), 0, 1) ** 2)[..., None]
def halftone(f, n):
    L = cv2.GaussianBlur(f @ np.array([0.299, 0.587, 0.114], np.float32), (0, 0), CELL * 0.32)
    L = np.clip(L, 0, 1) ** 0.75; r = 0.76 * np.sqrt(1 - L)
    ink = cv2.GaussianBlur(np.clip((r - DIST) * CELL * 0.9 + 0.5, 0, 1), (0, 0), 0.45)
    tex = (1 + FIBER + GRAINS[(n // 2) % 6])[..., None]
    out = f * (1 - 0.42 * ink[..., None]); out = out * (0.93 + 0.07 * tex) * np.array([1.0, 0.985, 0.95], np.float32) + 0.012
    return np.clip(out * VIGN, 0, 1)
GCOL = np.array([1.0, 0.98, 0.95], np.float32)
def compose(fr, n, flash=0.0):
    base = BGC + ROOM * 0.05 * np.array([1.0, 0.95, 0.88], np.float32)
    img = base * (1 - np.clip(fr.rgb.max(2, keepdims=True), 0, 1)) + fr.rgb
    g = glow_of(fr.gin + fr.acc * 1.2)
    gc = np.clip(g[..., None] * GCOL * 0.75, 0, 1)
    ga = glow_of(fr.acc)[..., None] * ACC * 0.9
    img = 1 - (1 - img) * (1 - gc) * (1 - np.clip(ga, 0, 1))
    img = img * (1 - fr.core[..., None]) + fr.core[..., None] * INK
    img = img * (1 - fr.acc[..., None]) + fr.acc[..., None] * ACC
    img = img * (1 + flash)
    return halftone(np.clip(img, 0, 1).astype(np.float32), n)
