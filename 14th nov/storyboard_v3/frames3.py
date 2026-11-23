"""Storyboard v3: real assets, reference language, no slop (no tags, labels, placeholders or drawn stand-ins)."""
import sys, os, numpy as np, cv2, onnxruntime as ort
sys.path.insert(0, '/home/claude/sb'); sys.path.insert(0, '/home/claude/sb2')
from kit import *
from seg import matte as human_matte
from PIL import ImageFont
A = '/mnt/user-data/uploads/Video editor/14th nov/aquired assest/'
OUT = '/home/claude/sb3/out/'; os.makedirs(OUT, exist_ok=True)
INTER = '/home/claude/sb/fonts/Inter.ttf'

def inter(size, wght=500, opsz=32):
    f = ImageFont.truetype(INTER, size); f.set_variation_by_axes([opsz, wght]); return f
def serif_i(size): return ImageFont.truetype(SERIF_I, size)
def load(p): return cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255

_isn = None
def object_matte(img):
    global _isn
    if _isn is None: _isn = ort.InferenceSession('/home/claude/isnet-general-use.onnx', providers=['CPUExecutionProvider'])
    h, w = img.shape[:2]
    x = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_AREA) - 0.5
    o = _isn.run(None, {_isn.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-6)
    a = cv2.resize(o, (w, h), interpolation=cv2.INTER_CUBIC)
    return cv2.GaussianBlur(np.clip((a - .2) / .6, 0, 1), (0, 0), 1.0)

def cover(img, cx=.5, cy=.5, zoom=1.0):
    """fill 1080x1920 from any image, centred on (cx, cy) fractions"""
    h, w = img.shape[:2]
    s = max(W / w, H / h) * zoom
    r = cv2.resize(img, (int(w * s + .5), int(h * s + .5)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    x0 = int(np.clip(r.shape[1] * cx - W / 2, 0, r.shape[1] - W)); y0 = int(np.clip(r.shape[0] * cy - H / 2, 0, r.shape[0] - H))
    return r[y0:y0 + H, x0:x0 + W].copy()

def place(img, sub, alpha, cx, cy, height, shadow=.45):
    """composite a cutout (sub, alpha) scaled to `height`, centred at cx, bottom-anchored at cy"""
    s = height / sub.shape[0]
    sub = cv2.resize(sub, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
    al = cv2.resize(alpha, (sub.shape[1], sub.shape[0]), interpolation=cv2.INTER_LINEAR)
    lay = np.zeros_like(img); A_ = np.zeros((H, W), np.float32)
    x0, y0 = int(cx - sub.shape[1] / 2), int(cy - sub.shape[0])
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + sub.shape[1]), min(H, y0 + sub.shape[0])
    lay[ys:ye, xs:xe] = sub[ys - y0:ye - y0, xs - x0:xe - x0]; A_[ys:ye, xs:xe] = al[ys - y0:ye - y0, xs - x0:xe - x0]
    if shadow:
        sh = blur(np.roll(A_, 24, 0), 30) * shadow; img = img * (1 - sh[..., None])
    return img * (1 - A_[..., None]) + lay * A_[..., None], A_

def look(img, vig=.6, bloom=.16, seed=1, warm=0.0):
    b = blur(np.clip(img - .55, 0, 1), 26); img = img + b * bloom
    if warm: img = img * np.array([1 + warm, 1, 1 - warm])
    return grain(vignette(img, vig), .022, seed)

def wcap(img, words, y, size=50, live=1, color=WARM):
    f = inter(size, 520); gap = size * .55; ws = [tlen(w, f) for w in words]
    x = 478.5 - (sum(ws) + gap * (len(words) - 1)) / 2
    for i, (w, wd) in enumerate(zip(words, ws)):
        mk = text_mask(w, f, (x, y)); a = .45 if (live and i >= len(words) - live and len(words) > 1) else 1.0
        img = img * (1 - (blur(np.roll(mk, 3, 0), 6) * .5 * a)[..., None]); img = comp(img, mk, color, a); x += wd + gap
    return img

def big(img, txt, fnt, xy, color, anchor='ms', glow=.25, shadow=.3, tracking=0):
    mk = text_mask(txt, fnt, xy, anchor, tracking=tracking)
    if shadow: img = img * (1 - (blur(np.roll(mk, 10, 0), 20) * shadow)[..., None])
    if glow: img = add(img, blur(mk, 30), color, glow)
    return comp(img, mk, color, 1)

def plane(img, page, quad, dim=0.0):
    """warp a flat page onto a tilted quad (3D plane) with soft shadow"""
    h, w = page.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    warped = cv2.warpPerspective(page, M, (W, H), flags=cv2.INTER_AREA)
    al = cv2.warpPerspective(np.ones((h, w), np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
    sh = blur(np.roll(al, 40, 0), 40) * .6; img = img * (1 - sh[..., None])
    img = img * (1 - al[..., None]) + warped * al[..., None]
    if dim: img = img * (1 - dim * al[..., None])
    return img, al, M

def studio(top=(0.93, 0.93, 0.92), bot=(0.80, 0.80, 0.80)):
    img = vgrad(top, bot, 1.1); return img

# ------------------------------------------------------------------ frames
def v01():  # At MIT, Alexandr Wang: night dome, MIT behind him
    bg = load(A + 'B01_mit_dome_c_night.jpg')
    img = cover(bg, .5, .42, 1.0) * np.array([.86, .92, 1.05])
    img = blur(img, 1.0) * .9
    img = big(img, 'MIT', inter(400, 860), (640, 1080), WARM, glow=.2, shadow=.35, tracking=-6)
    ya = load(A + 'B01_wang_young_a.jpg')
    full = human_matte(ya)
    crop = ya[110:830, 1060:1420].copy(); al = full[110:830, 1060:1420].copy()
    al[:, :70] = 0
    img, _ = place(img, crop * np.array([.95, .97, 1.03]), al, 300, 1960, 1180, shadow=.5)
    img = look(img, .6, .14, 1)
    return wcap(img, ['At', 'MIT', 'Alexandr', 'Wang'], 330, 50)

def v05():  # scaleapi.com, June 2016, one night
    page = load(A + 'B04_scaleapi_2016_a_jun24.png')[0:1100]
    img = canvas((0.02, 0.025, 0.04)); img = blob(img, 540, 900, 600, (.35, .45, .7), .25)
    img, al, M = plane(img, page, [[90, 560], [1010, 470], [1050, 1330], [60, 1290]])
    shade = np.linspace(.15, .55, W)[None, :, None]
    img = img * (1 - shade * al[..., None])
    img = add(img, blur(al, 60), (.45, .6, 1.0), .12)
    img = look(img, .65, .2, 5)
    return wcap(img, ['one', 'night'], 360, 52, live=0)

def v06():  # Product Hunt, a week later
    page = load(A + 'B05_producthunt_2016_a.png')[0:1500]
    img = canvas((0.05, 0.045, 0.045)); img = blob(img, 540, 900, 600, (1, .7, .5), .12)
    img, al, M = plane(img, page, [[60, 420], [1000, 500], [1020, 1440], [40, 1380]], dim=.35)
    # light the tagline band only (no highlighter, no box)
    band = np.zeros((1500, 1440), np.float32); band[150:330, 30:1000] = 1
    band = cv2.warpPerspective(cv2.GaussianBlur(band, (0, 0), 25), M, (W, H))
    img = img * (1 + .55 * band[..., None])
    img = big(img, 'a week later.', serif_i(150), (540, 1620), WARM, glow=.25, shadow=.5)
    return look(img, .6, .14, 6)

def v07():  # Random engineers showed up (real CVPR crowd)
    img = cover(load('/home/claude/sb3/expo19.jpg'), .5, .5, 1.05) * np.array([.92, .95, 1.02])
    img = look(img, .6, .14, 7)
    return wcap(img, ['random', 'engineers', 'showed', 'up'], 1250, 52)

def v08():  # Cruise wordmark behind the real car
    car = load(A + 'B07_cruise_car_b.jpg')
    crop = car[1100:4100, 900:7000]
    al = object_matte(crop)
    img = studio((0.95, 0.95, 0.94), (0.78, 0.78, 0.79))
    img = big(img, 'Cruise', inter(320, 860), (540, 980), (1.0, 0.36, 0.20), glow=0, shadow=0, tracking=-8)
    img, _ = place(img, crop, al, 540, 1390, 470, shadow=.55)
    img = look(img, .45, .04, 8)
    return wcap(img, ['then', 'Cruise', 'reached', 'out'], 420, 52, color=(0.1, 0.1, 0.11))

def v09():  # self-driving: real dashcam, boxes only, no labels
    img = cover(load('/home/claude/sb3/dash_2s.jpg'), .5, .5, 1.0) * .95
    img = look(img, .45, .2, 9)
    for (x0, y0, x1, y1) in [(110, 1036, 390, 1230), (610, 1024, 718, 1158), (448, 1070, 506, 1176), (875, 1086, 1000, 1170)]:
        img = comp(img, box_mask(x0, y0, x1, y1, 3, 22), WARM, 1)
        img = comp(img, box_mask(x0, y0, x1, y1, 1), WARM, .3)
    return wcap(img, ['all', 'in', 'on', 'self-driving'], 420, 52)

def v10():  # booth to booth: Wang sticker over the real CVPR floor
    img = cover(load('/home/claude/sb3/expo.jpg'), .5, .5, 1.0)
    img = blur(img, 6) * .7
    yb = load(A + 'B01_wang_young_b.jpg')
    full = object_matte(yb)
    ys, xs = np.where(full > .5)
    y0, y1, x0, x1 = max(0, ys.min() - 20), ys.max(), max(0, xs.min() - 20), min(yb.shape[1], xs.max() + 20)
    crop = yb[y0:y1, x0:x1]; al = full[y0:y1, x0:x1].copy(); al[-14:] = 0
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
    border = np.clip(cv2.dilate(al, k) - al, 0, 1)
    stick = crop * al[..., None] + np.ones_like(crop) * .97 * border[..., None]
    al2 = np.clip(al + border, 0, 1)
    img, _ = place(img, stick, al2, 560, 1300, 640, shadow=.6)
    img = look(img, .55, .12, 10)
    return wcap(img, ['booth', 'to', 'booth'], 380, 54)

def v12():  # huge budgets: real AI plate, type in the sky
    img = cover(load(A + 'B11_ai_huge_budgets_b.png'), .5, .55, 1.0)
    img = big(img, 'a few customers,', inter(84, 320), (540, 470), (0.12, 0.2, 0.2), glow=0, shadow=0)
    img = big(img, 'huge budgets.', inter(120, 820), (540, 600), (0.12, 0.2, 0.2), glow=0, shadow=0)
    return look(img, .45, .05, 12)

def v13():  # Meta wordmark behind the official portrait
    p = load(A + 'B12_wang_recent_a.jpg')
    crop = p[400:7200, 200:5560]
    small = cv2.resize(crop, (1072, 1360), interpolation=cv2.INTER_AREA)
    al = human_matte(small)
    img = studio((0.94, 0.94, 0.95), (0.80, 0.81, 0.84))
    img = big(img, 'Meta', inter(360, 860), (540, 820), (0.06, 0.40, 0.98), glow=0, shadow=0, tracking=-8)
    img, _ = place(img, small, al, 540, 1930, 1300, shadow=.4)
    img = look(img, .45, .04, 13)
    return wcap(img, ['now', 'running', 'AI', 'at', 'Meta'], 420, 52, color=(0.1, 0.1, 0.11))

def v14():  # his real post, light on the line
    post = load(A + 'B13_july_post_a.png')[0:1500]
    img = canvas((0.035, 0.035, 0.04)); img = blob(img, 540, 900, 650, (.6, .7, 1), .12)
    img, al, M = plane(img, post, [[110, 430], [990, 470], [1000, 1380], [90, 1340]], dim=.3)
    band = np.zeros((1500, 1650), np.float32); band[150:420, 40:1600] = 1
    band = cv2.warpPerspective(cv2.GaussianBlur(band, (0, 0), 30), M, (W, H))
    img = img * (1 + .5 * band[..., None])
    return look(img, .6, .14, 14)

def v14b():  # real payoff: the agent placed the order
    img = cover(load('/home/claude/sb3/tyler_order.jpg'), .36, .5, 1.35)
    img = img * .92
    img = big(img, 'refill your fridge', serif_i(120), (540, 1500), (0.10, 0.10, 0.11), glow=0, shadow=0)
    return look(img, .55, .05, 15)

def v16():  # end: full circle
    img = canvas((0.97, 0.95, 0.90)); img = vignette(img, .45)
    img = comp(img, text_mask('full circle.', serif_i(150), (540, 980), 'ms'), (0.13, 0.12, 0.11), 1)
    return grain(img, .015, 16)

FR = {k: v for k, v in globals().items() if k.startswith('v') and k[1:3].isdigit()}
if __name__ == '__main__':
    for n in (sys.argv[1:] or sorted(FR)):
        save(FR[n](), OUT + n + '.png'); print('ok', n, flush=True)
