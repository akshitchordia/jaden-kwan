"""Storyboard v2: the fridge reel rebuilt in the reference edit's language."""
import sys, os, numpy as np, cv2
sys.path.insert(0, '/home/claude/sb'); sys.path.insert(0, '/home/claude/sb2')
from kit import *
import frames as F1
from seg import matte
from PIL import ImageFont
OUT = '/home/claude/sb2/out/'; os.makedirs(OUT, exist_ok=True)
INTER = '/home/claude/sb/fonts/Inter.ttf'
SB = '/mnt/user-data/uploads/Video editor/14th nov/_work/sbframes/'

def inter(size, wght=500, opsz=32):
    f = ImageFont.truetype(INTER, size); f.set_variation_by_axes([opsz, wght]); return f

def load(p):
    return cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255

def look(img, vig=.62, bloom=.18, seed=1):
    """reference finish: heavy vignette, soft bloom, fine grain"""
    b = blur(np.clip(img - .55, 0, 1), 24)
    img = img + b * bloom
    img = vignette(img, vig)
    return grain(img, .022, seed)

def wcap(img, words, y=1170, size=50, live=1, color=WARM):
    """word-by-word micro caption (reference): Inter Medium, wide word gaps, newest word half-lit"""
    f = inter(size, 520)
    gap = size * .55
    ws = [tlen(w, f) for w in words]
    x = 478.5 - (sum(ws) + gap * (len(words) - 1)) / 2
    for i, (w, wd) in enumerate(zip(words, ws)):
        mk = text_mask(w, f, (x, y))
        a = .45 if i >= len(words) - live and live and len(words) > 1 else 1.0
        img = img * (1 - (blur(np.roll(mk, 3, 0), 6) * .5 * a)[..., None])
        img = comp(img, mk, color, a)
        x += wd + gap
    return img

def behind(img, alpha, txt, fnt, xy, color=WARM, anchor='ms', glow=.5, shadow=.35):
    """big type layered behind the subject (depth)"""
    mk = text_mask(txt, fnt, xy, anchor)
    lay = img.copy()
    if shadow: lay = lay * (1 - (blur(np.roll(mk, 10, 0), 18) * shadow)[..., None])
    lay = add(lay, blur(mk, 30), color, .25 * glow)
    lay = comp(lay, mk, color, 1)
    a = alpha[..., None]
    return img * a + lay * (1 - a)

def handles(img, x0, y0, x1, y1, label=None, color=WARM):
    img = comp(img, box_mask(x0, y0, x1, y1, 2), color, .9)
    for x in (x0, (x0 + x1) / 2, x1):
        for y in (y0, (y0 + y1) / 2, y1):
            if x == (x0 + x1) / 2 and y == (y0 + y1) / 2: continue
            img = comp(img, rect_mask(x - 9, y - 9, x + 9, y + 9), color, 1)
    if label:
        img = comp(img, text_mask(label, inter(34, 560), ((x0 + x1) / 2, y1 - 22), 'ms'), color, 1)
    return img

def article(img, label, seed=5):
    """white news/web page backdrop placeholder (real screenshot goes here)"""
    img[:] = (0.93, 0.93, 0.92)
    rng = np.random.default_rng(seed)
    img = comp(img, rect_mask(80, 300, 900, 345), (0.18, 0.18, 0.2), 1)
    img = comp(img, rect_mask(80, 365, 640, 410), (0.18, 0.18, 0.2), 1)
    for y in range(450, 560, 34): img = comp(img, rect_mask(80, y, 1000 - rng.integers(0, 260), y + 14), (0.65, 0.65, 0.66), 1)
    for y in range(1260, 1700, 38): img = comp(img, rect_mask(80, y, 1000 - rng.integers(0, 300), y + 14), (0.72, 0.72, 0.73), 1)
    img = comp(img, text_mask(label, inter(24, 500), (80, 270)), (0.45, 0.45, 0.47), 1)
    return img

def inset(img, sub, x0, y0, x1, y1, italic=None):
    h, w = int(y1 - y0), int(x1 - x0)
    sh, sw = sub.shape[:2]
    s = max(w / sw, h / sh); r = cv2.resize(sub, (int(sw * s) + 1, int(sh * s) + 1))
    oy, ox = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    img = img * (1 - (blur(rect_mask(x0 + 8, y0 + 18, x1 + 8, y1 + 18), 22) * .45)[..., None])
    img[int(y0):int(y0) + h, int(x0):int(x0) + w] = r[oy:oy + h, ox:ox + w]
    if italic:
        f = ImageFont.truetype(SERIF_I, 96)
        mk = text_mask(italic, f, ((x0 + x1) / 2, y1 - 40), 'ms')
        img = img * (1 - (blur(np.roll(mk, 4, 0), 10) * .6)[..., None]); img = comp(img, mk, WARM, 1)
    return img

def persp_grid(img, color=(.5, .5, .55), a=.35):
    """tilted dark floor grid"""
    src = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
    dst = np.float32([[300, 520], [880, 470], [1180, 1800], [-120, 1880]])
    M = cv2.getPerspectiveTransform(src, dst)
    m = np.zeros((H, W), np.float32)
    for k in np.linspace(0, 1, 9):
        for p, q in (((k, 0), (k, 1)), ((0, k), (1, k))):
            pts = cv2.perspectiveTransform(np.float32([[p, q]]), M)[0]
            cv2.line(m, tuple(int(v) for v in pts[0]), tuple(int(v) for v in pts[1]), 1.0, 2, cv2.LINE_AA)
    return comp(img, blur(m, .8), color, a), M

def car_silhouette(img, cx, cy, s=1.0, color=(0.08, 0.08, 0.09)):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    w, h = 520 * s, 230 * s
    d.rounded_rectangle([cx - w / 2, cy - h * .25, cx + w / 2, cy + h * .45], int(60 * s), fill=255)
    d.rounded_rectangle([cx - w * .32, cy - h * .62, cx + w * .30, cy - h * .05], int(70 * s), fill=255)
    d.rounded_rectangle([cx - w * .12, cy - h * .80, cx + w * .10, cy - h * .58], int(20 * s), fill=255)  # roof sensor
    for x in (cx - w * .3, cx + w * .3): d.ellipse([x - 62 * s, cy + h * .25, x + 62 * s, cy + h * .25 + 124 * s], fill=255)
    mk = blur(np.asarray(m, np.float32) / 255, 1.2)
    return comp(img, mk, color, 1), mk

def person_silhouette(cx, top, s=1.0):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse([cx - 92 * s, top, cx + 92 * s, top + 225 * s], fill=255)                       # head
    d.rounded_rectangle([cx - 48 * s, top + 190 * s, cx + 48 * s, top + 300 * s], int(20 * s), fill=255)  # neck
    d.polygon([(cx - 70 * s, top + 270 * s), (cx - 250 * s, top + 330 * s), (cx - 300 * s, top + 420 * s), (cx - 315 * s, top + 900 * s),
               (cx + 315 * s, top + 900 * s), (cx + 300 * s, top + 420 * s), (cx + 250 * s, top + 330 * s), (cx + 70 * s, top + 270 * s)], fill=255)
    mk = np.asarray(m, np.float32) / 255
    mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    return blur(mk, 1.5)

def placeholder_fill(img, mk, label, ink=(.9, .9, .9)):
    """grey halftone stand-in for a real cutout"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.deg2rad(45); u = (xx * np.cos(a) + yy * np.sin(a)) / 7; v = (-xx * np.sin(a) + yy * np.cos(a)) / 7
    dots = (np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2) < .33).astype(np.float32)
    tone = .30 + .10 * dots
    img = img * (1 - (blur(np.roll(mk, 18, 0), 22) * .35)[..., None])
    img = img * (1 - mk[..., None]) + tone[..., None] * mk[..., None]
    img = add(img, np.clip(mk - blur(np.roll(mk, -5, 0), 2), 0, 1), (1, 1, 1), .45)
    return img

# ------------------------------------------------------------------ frames
def s01():  # HOOK: $14 Billion behind his head
    img = load(SB + 'face_1.25.jpg'); a = matte(img)
    f = inter(200, 760, 32)
    while tlen('$14 Billion', f) > 930: f = inter(f.size - 6, 760, 32)
    img = behind(img, a, '$14 Billion', f, (540, 470))
    img = look(img, .45, .12, 1)
    return wcap(img, ['Meta', 'paid', '$14', 'billion'], 1210, 52)

def s02():  # article backdrop + inset fridge, serif italic
    img = article(canvas(), 'REAL ARTICLE GOES HERE · META × SCALE AI, 2025')
    fr = F1.fridge_plate(1.0, 1.0)
    img = inset(img, fr[700:1300], 110, 640, 970, 1200, 'a camera in a fridge')
    img = look(img, .55, .05, 2)
    return wcap(img, ['started', 'with', 'a', 'camera'], 1330, 46, color=(0.12, 0.12, 0.13))

def polaroid(img, x0, y0, w, sub, angle, seed, caption=None):
    def content(c):
        h_, w_ = c.shape[:2]
        s = cv2.resize(sub, (w_ - 40, h_ - 120)); c[22:22 + s.shape[0], 20:20 + s.shape[1]] = s
        if caption: c = local_text(c, caption, inter(26, 500), (24, h_ - 40), (0.3, 0.3, 0.32))
        return c
    return paper(img, x0, y0, x0 + w, y0 + w * 1.18, angle, (0.96, 0.95, 0.93), seed=seed, shadow=.6, content=content)

def s03():  # polaroid desk on orange grid paper
    img = canvas((0.72, 0.30, 0.13))
    yy, xx = np.mgrid[0:H, 0:W]
    grid = (((xx % 46) < 2) | ((yy % 46) < 2)).astype(np.float32)
    img = comp(img, grid, (0.86, 0.45, 0.25), .5)
    rng = np.random.default_rng(3)
    dap = blur(rng.random((H // 16, W // 16)).astype(np.float32), 3); dap = cv2.resize(dap, (W, H))
    img = img * (0.72 + .5 * dap[..., None])
    ph = np.ones((400, 400, 3), np.float32) * .5
    yy2, xx2 = np.mgrid[0:400, 0:400]
    ph[((xx2 - 200) ** 2 / 70 ** 2 + (yy2 - 150) ** 2 / 90 ** 2) < 1] = .22
    ph[((xx2 - 200) ** 2 / 190 ** 2 + (yy2 - 420) ** 2 / 170 ** 2) < 1] = .22
    dome = np.ones((400, 400, 3), np.float32) * np.array([.38, .42, .5])
    dome[((xx2 - 200) ** 2 / 120 ** 2 + (yy2 - 230) ** 2 / 110 ** 2) < 1] = (.78, .78, .74)
    dome[230:400, 60:340] = (.74, .73, .70)
    for x in range(80, 330, 36): dome[250:400, x:x + 12] = (.55, .55, .53)
    fr = cv2.resize(F1.fridge_plate(1.0, 1.0)[850:1250, 200:900], (400, 400))
    img = polaroid(img, 520, 560, 400, dome, 7, 31, 'MIT')
    img = polaroid(img, 170, 900, 380, fr, -6, 32, 'the fridge')
    img = polaroid(img, 540, 1040, 400, ph, 4, 33, 'Wang, 2015')
    pen = rect_mask(830, 1500, 860, 1760, 15)
    pen = cv2.warpAffine(pen, cv2.getRotationMatrix2D((845, 1630), -25, 1), (W, H))
    img = img * (1 - (blur(np.roll(pen, 16, 1), 10) * .5)[..., None]); img = comp(img, pen, (0.12, 0.12, 0.13), 1)
    t1 = text_mask('Alexandr', inter(118, 760), (110, 420)); t2 = text_mask('Wang · MIT', inter(78, 380), (114, 510))
    M = cv2.getRotationMatrix2D((300, 460), 6, 1)
    for t, c in ((t1, (0.25, 0.10, 0.04)), (t2, (0.45, 0.22, 0.10))):
        img = comp(img, cv2.warpAffine(t, M, (W, H)), c, 1)
    return look(img, .6, .08, 3)

def s04():  # fridge cam with selection handles
    img = F1.fridge_plate(1.0, 1.0); img = F1.arm(img, 660, 1035)
    img = look(img, .55, .1, 4)
    img = handles(img, 290, 900, 1000, 1150, 'catch them')
    return wcap(img, ['build', 'a', 'camera', 'to'], 420, 50)

def s05():  # glitch: it couldn't work
    img = F1.fridge_plate(1.0, 1.0); img = F1.arm(img, 660, 1035)
    img = look(img, .5, .1, 5)
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], 18, 1); out[..., 2] = np.roll(img[..., 2], -14, 1)
    rng = np.random.default_rng(9)
    for _ in range(9):
        y = rng.integers(250, 1700); h = rng.integers(20, 90); dx = rng.integers(-120, 120)
        out[y:y + h] = np.roll(out[y:y + h], dx, 1)
    band = slice(820, 1010); out[band] = 1 - out[band] * np.array([.3, 1, 1])
    f = ImageFont.truetype(SERIF_I, 170)
    mk = text_mask("couldn't", f, (500, 1240), 'ms')
    red = np.roll(mk, 10, 1)
    out = comp(out, red, (1, .2, .2), .8); out = comp(out, np.roll(mk, -8, 1), (.2, .9, 1), .6); out = comp(out, mk, WARM, 1)
    return out

def s06():  # x1,000,000 behind Wang
    cap = cv2.VideoCapture('/home/claude/work/arch_v2.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES, 117)
    ok, fr = cap.read(); img = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    img = img * .85
    img = look(img, .5, .1, 6)
    f = inter(170, 800, 32)
    while tlen('×1,000,000', f) > 930: f = inter(f.size - 6, 800, 32)
    mk = text_mask('×1,000,000', f, (540, 1150), 'ms')
    img = img * (1 - (blur(np.roll(mk, 10, 0), 20) * .6)[..., None]); img = add(img, blur(mk, 30), WARM, .2); img = comp(img, mk, WARM, 1)
    return wcap(img, ['a', 'million', 'times', 'more', 'data'], 1270, 50)

def s07():  # tile reveal: one night
    base = canvas((0.03, 0.03, 0.035))
    base = blob(base, 540, 820, 420, COOL, .08)
    base = comp(base, rect_mask(110, 860, 970, 980, 60), (0.11, 0.11, 0.12), 1)
    base = comp(base, text_mask('scaleapi.com', font(MONO, 50), (190, 936)), WARM, 1)
    base = comp(base, text_mask('2:47', inter(230, 300), (540, 760), 'ms'), WARM, .95)
    base = comp(base, text_mask('AM', inter(60, 500), (540 + tlen('2:47', inter(230, 300)) / 2 + 18, 760)), WARM, .6)
    dark = canvas((0.10, 0.11, 0.13))
    yy, xx = np.mgrid[0:H, 0:W]
    dark = comp(dark, (((xx % 60) < 2) | ((yy % 60) < 2)).astype(np.float32), (.25, .27, .3), .5)
    T = 180; rng = np.random.default_rng(4)
    img = dark.copy()
    for ty in range(0, H, T):
        for tx in range(0, W, T):
            r = rng.random()
            sl = (slice(ty, ty + T), slice(tx, tx + T))
            inside = 560 < ty + T / 2 < 1100
            if r < (.97 if inside else .45) and not (inside and tx == 720 and ty == 900): img[sl] = base[sl]
            elif (inside and tx == 720 and ty == 900) or (not inside and r < .6): img[sl] = 0.96
    img = look(img, .55, .12, 7)
    return wcap(img, ['one', 'night'], 330, 50)

def s08():  # Product Hunt backdrop + italic
    img = article(canvas(), 'REAL SCREENSHOT GOES HERE · SCALE API ON PRODUCT HUNT, 2016', 8)
    hl = rect_mask(80, 450, 820, 486, 4); img = img * (1 - hl[..., None] * .55) + hl[..., None] * .55 * np.array([0.98, 0.86, 0.55])
    cal = canvas((0.10, 0.10, 0.11))
    cal = comp(cal, text_mask('+7', inter(420, 700), (540, 1100), 'ms'), WARM, 1)
    cal = comp(cal, text_mask('DAYS', inter(70, 500), (540, 1220), 'ms'), WARM, .6)
    img = inset(img, cal[700:1320], 110, 640, 970, 1200, 'a week later')
    img = look(img, .55, .05, 8)
    return wcap(img, ['launched', 'on', 'Product', 'Hunt'], 1330, 46, color=(0.12, 0.12, 0.13))

def s09():  # perspective grid, engineers pop in
    img = canvas((0.05, 0.05, 0.06)); img = blob(img, 540, 900, 600, (.6, .65, .8), .08)
    img, M = persp_grid(img)
    rng = np.random.default_rng(11)
    cols = [(.95, .45, .2), (.3, .55, .95), (.55, .4, .9), (.25, .75, .55), (.9, .8, .3), (.85, .85, .85)]
    for k in range(13):
        p = cv2.perspectiveTransform(np.float32([[[rng.uniform(.05, .95), rng.uniform(.05, .95)]]]), M)[0, 0]
        s = 30 + (p[1] - 470) / 1400 * 70
        c = cols[k % len(cols)]
        img = comp(img, blur(rect_mask(p[0] - s, p[1] - s, p[0] + s, p[1] + s, s * .3), 4), (0, 0, 0), .5)
        img = comp(img, rect_mask(p[0] - s, p[1] - s, p[0] + s, p[1] + s, s * .3), c, .95)
        img = comp(img, rect_mask(p[0] - s * .25, p[1] - s * .62, p[0] + s * .25, p[1] - s * .12, s * .25), (1, 1, 1), .9)
        img = comp(img, rect_mask(p[0] - s * .5, p[1] - s * .02, p[0] + s * .5, p[1] + s * .6, s * .3), (1, 1, 1), .9)
    big = rect_mask(700, 1320, 940, 1560, 50)
    img = comp(img, blur(big, 14), (.3, .55, .95), .85)
    img = look(img, .55, .15, 9)
    return wcap(img, ['random', 'engineers', 'showed', 'up'], 1250, 52)

def s10():  # CRUISE wordmark behind the car cutout
    img = canvas((0.95, 0.95, 0.94)); img = vignette(img, .5)
    f = inter(250, 820, 32)
    img = comp(img, text_mask('CRUISE', f, (540, 760), 'ms', tracking=8), (0.98, 0.42, 0.15), 1)
    _, mk = car_silhouette(img.copy(), 540, 900, 1.45)
    img = placeholder_fill(img, mk, '')
    img = comp(img, text_mask('YOUR ROBOTAXI CUTOUT', font(MONO, 22), (540, 960), 'ms', tracking=3), (.92, .92, .92), .9)
    img = look(img, .45, .02, 10)
    return wcap(img, ['then', 'Cruise', 'reached', 'out'], 380, 52, color=(0.1, 0.1, 0.11))

def s11():  # labelling, reference style
    old_cap, old_tag = F1.caption, F1.tag
    F1.caption = lambda img, line: img
    def tag(img, x, y, txt, color=WARM, ink=INK, size=30):
        f = inter(size, 560); w = tlen(txt, f)
        img = comp(img, rect_mask(x, y - size - 14, x + w + 24, y + 6, 6), color, .95)
        return comp(img, text_mask(txt, f, (x + 12, y - 6)), ink, 1)
    F1.tag = tag
    img = F1.f08(); F1.caption, F1.tag = old_cap, old_tag
    img = handles(img, 585, 1210, 715, 1325, None, RED)
    img = look(img, .4, .1, 11)
    return wcap(img, ['all', 'in', 'on', 'self-driving'], 1440, 50)

def s12():  # expo + Wang cutout, yellow silhouette flash state
    img = canvas((0.06, 0.055, 0.05))
    rng = np.random.default_rng(12)
    for k in range(7):
        x = 60 + k * 150
        img = add(img, blur(rect_mask(x, 300, x + 120, 330), 8), (1, .95, .85), .5)
        img = comp(img, rect_mask(x, 700 + (k % 2) * 40, x + 130, 1500), (0.10 + .03 * (k % 3), 0.10, 0.11), 1)
        img = comp(img, rect_mask(x + 10, 720 + (k % 2) * 40, x + 120, 800 + (k % 2) * 40, 6), (.85, .85, .8), .25)
    img = blob(img, 540, 900, 500, (1, .9, .7), .12)
    img = blur(img, 3) * .8
    sil = person_silhouette(560, 600, 1.0)
    img = comp(img, sil, (1.0, 0.86, 0.10), 1)
    img = add(img, blur(sil, 40), (1.0, 0.86, 0.10), .35)
    img = comp(img, text_mask('YOUR WANG CUTOUT · FLASH FRAME', font(MONO, 22), (540, 1490), 'ms', tracking=3), WARM, .5)
    img = look(img, .55, .1, 12)
    return wcap(img, ['booth', 'to', 'booth'], 420, 54)

def s13():  # the formula as type
    img = canvas((0.05, 0.048, 0.045)); img = blob(img, 540, 800, 600, (1, .9, .8), .05)
    y = 560
    img = comp(img, text_mask('Launch broad.', inter(120, 780), (100, y)), WARM, 1); y += 150
    img = comp(img, text_mask("Find who's", inter(120, 300), (100, y)), WARM, 1); y += 135
    img = comp(img, text_mask('desperate.', inter(120, 300), (100, y)), WARM, 1); y += 165
    img = comp(img, text_mask('Go in,', inter(120, 780), (100, y)), WARM, 1); y += 130
    img = glow_text(img, text_mask('even if it looks small', ImageFont.truetype(SERIF_I, 96), (104, y)), WARM, .6, .3)
    return look(img, .6, .12, 13)

def s14():  # AI plate mock: huge budgets
    img = vgrad((0.52, 0.80, 0.80), (0.35, 0.62, 0.64))
    for cx, cy, r in ((260, 520, 120), (820, 430, 150), (600, 1650, 260)):
        img = blob(img, cx, cy, r, (1, 1, 1), .55)
    def cube(img, x, y, s, top=(.62, .74, .52), left=(.38, .5, .32), right=(.28, .38, .24)):
        m = Image.new('RGB', (W, H), 0); d = ImageDraw.Draw(m)
        h = s * .5
        d.polygon([(x, y), (x + s, y - h), (x + 2 * s, y), (x + s, y + h)], fill=tuple(int(v * 255) for v in top))
        d.polygon([(x, y), (x + s, y + h), (x + s, y + h + s * 1.1), (x, y + s * 1.1)], fill=tuple(int(v * 255) for v in left))
        d.polygon([(x + s, y + h), (x + 2 * s, y), (x + 2 * s, y + s * 1.1), (x + s, y + h + s * 1.1)], fill=tuple(int(v * 255) for v in right))
        a = np.asarray(m, np.float32) / 255; mk = (a.sum(2) > 0).astype(np.float32)
        img = img * (1 - (blur(np.roll(mk, 40, 0), 30) * .35)[..., None])
        return img * (1 - mk[..., None]) + a * mk[..., None]
    img = cube(img, 140, 980, 190); img = cube(img, 560, 1040, 170); img = cube(img, 330, 760, 180)
    for k in range(9): img = cube(img, 120 + k * 92, 1560, 28, (.7, .7, .7), (.45, .45, .45), (.35, .35, .35))
    f = inter(92, 900, 32)
    for i, (t, yy) in enumerate((('FEW CUSTOMERS', 420), ('HUGE BUDGETS', 530))):
        mk = text_mask(t, f, (540, yy), 'ms')
        img = comp(img, np.roll(mk, 8, 0), (.6, .45, .05), 1); img = comp(img, mk, (1.0, .82, .15), 1)
    img = comp(img, text_mask('AI PLATE · YOU GENERATE FROM MY PROMPT', font(MONO_M, 22), (540, 300), 'ms', tracking=3), (.1, .2, .2), .8)
    return look(img, .5, .05, 14)

def s15():  # META wordmark behind Wang cutout
    img = canvas((0.95, 0.95, 0.94)); img = vignette(img, .5)
    img = comp(img, text_mask('META', inter(330, 820), (540, 760), 'ms', tracking=10), (0.10, 0.40, 0.98), 1)
    sil = person_silhouette(540, 600, 1.0)
    img = placeholder_fill(img, sil, '')
    img = comp(img, text_mask('YOUR RECENT WANG CUTOUT', font(MONO, 22), (540, 1050), 'ms', tracking=3), (.9, .9, .9), .8)
    img = look(img, .45, .02, 15)
    return wcap(img, ['now', 'running', 'AI', 'at', 'Meta'], 380, 52, color=(0.1, 0.1, 0.11))

def s16():  # post backdrop + italic
    img = canvas((0.06, 0.06, 0.065))
    img = comp(img, rect_mask(80, 280, 140, 340, 30), (.35, .35, .36), 1)
    img = comp(img, rect_mask(160, 290, 460, 312), (.55, .55, .56), 1); img = comp(img, rect_mask(160, 322, 360, 338), (.35, .35, .36), 1)
    for i, y in enumerate((400, 450, 500)): img = comp(img, rect_mask(80, y, 1000 - i * 120, y + 22), (.32, .32, .33), 1)
    img = comp(img, text_mask('REAL POST SCREENSHOT GOES HERE · WANG, JULY 2026', inter(24, 500), (80, 590)), (.55, .55, .56), 1)
    fr = F1.fridge_plate(1.0, 1.0)
    img = inset(img, fr[300:900], 110, 660, 970, 1220, 'refill your fridge')
    img = look(img, .55, .1, 16)
    return wcap(img, ['he', 'posted', 'that', 'its', 'AI'], 1340, 48)

def s17():  # face, fridge behind head
    img = load(SB + 'face_49.30.jpg'); a = matte(img)
    img = behind(img, a, 'fridge.', ImageFont.truetype(SERIF_I, 300), (540, 470))
    img = look(img, .45, .12, 17)
    return wcap(img, ['refill', 'your', 'fridge'], 1230, 52, live=0)

def s18():  # cream end card
    img = canvas((0.97, 0.95, 0.90)); img = vignette(img, .45)
    f = ImageFont.truetype(SERIF_I, 64)
    img = comp(img, text_mask('This problem was actually', f, (540, 640), 'ms'), (0.15, 0.14, 0.13), 1)
    img = comp(img, text_mask('the inspiration for Scale AI', f, (540, 720), 'ms'), (0.15, 0.14, 0.13), .55)
    fr = cv2.resize(F1.fridge_plate(1.0, .55)[500:1400, 100:980], (400, 410))
    img = polaroid(img, 340, 1000, 400, fr, -3, 41, 'full circle')
    return grain(img, .015, 18)

FR = {k: v for k, v in globals().items() if k.startswith('s') and k[1:].isdigit()}
if __name__ == '__main__':
    for n in (sys.argv[1:] or sorted(FR)):
        save(FR[n](), OUT + n + '.png'); print('ok', n, flush=True)
