"""Animated phone preview of storyboard v3 over the locked v2 cut (720x1280, timecode)."""
import sys, json, subprocess, numpy as np, cv2
sys.path.insert(0, '/home/claude/sb'); sys.path.insert(0, '/home/claude/sb2'); sys.path.insert(0, '/home/claude/sb3')
from kit import *
from seg import matte as human_matte
from frames3 import (inter, serif_i, load, A, cover, object_matte, place, studio, look as look3)
from PIL import ImageFont
import caps_block
FPS = 24000 / 1001
SRC = '/mnt/user-data/uploads/Video editor/14th nov/Fridge_zoom_v2_tight.mp4'
OUTF = '/home/claude/sb3/Fridge_storyboard_v3_blockcaps_preview.mp4'
PW, PH = 720, 1280
LEAD = 0.12  # captions/type lead the spoken word

def cl(x): return float(np.clip(x, 0, 1))
def eo(u): u = cl(u); return 1 - (1 - u) ** 3
def eb(u):  # ease-out-back
    u = cl(u); c = 1.9; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def eio(u): u = cl(u); return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2

def M_about(s, cx, cy, tx=0, ty=0, rot=0):
    M = cv2.getRotationMatrix2D((cx, cy), rot, s); M[0, 2] += tx; M[1, 2] += ty; return M
def warp(img, M, border=cv2.BORDER_REFLECT):
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=border)
def warp0(img, M):
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
def over(base, rgb_pm, a, op=1.0):
    a = a * op; return base * (1 - a[..., None]) + rgb_pm * op
def layer_of(sub, al, cx, bottom, height):
    rgb, a = place(np.zeros((H, W, 3), np.float32), sub, al, cx, bottom, height, shadow=0)
    return rgb, a  # rgb is premultiplied

# ---------------- captions built word by word, in place
def cap(img, words, t, y, size=50, color=WARM):
    return img

def _old_cap(img, words, t, y, size=50, color=WARM):
    f = inter(size, 520); gap = size * .55
    ws = [tlen(w, f) for w, _ in words]
    x = 478.5 - (sum(ws) + gap * (len(words) - 1)) / 2
    for (w, wt), wd in zip(words, ws):
        k = (t - (wt - LEAD)) / .12
        if k > 0:
            a = .45 + .55 * cl(k)
            mk = text_mask(w, f, (x, y))
            img = img * (1 - (blur(np.roll(mk, 3, 0), 6) * .5 * a)[..., None]); img = comp(img, mk, color, a)
        x += wd + gap
    return img

def finish(img, i, vig=.6, bloom=.14):
    b = blur(np.clip(img - .55, 0, 1), 26); img = img + b * bloom
    return grain(vignette(img, vig), .022, i)

def glitch(img, i, amt=1.0):
    out = img.copy(); s = int(18 * amt)
    out[..., 0] = np.roll(img[..., 0], s, 1); out[..., 2] = np.roll(img[..., 2], -s, 1)
    rng = np.random.default_rng(i)
    for _ in range(8):
        y = rng.integers(200, 1700); h = rng.integers(20, 110); dx = rng.integers(-140, 140)
        out[y:y + h] = np.roll(out[y:y + h], int(dx * amt), 1)
    y = rng.integers(500, 1300); out[y:y + 160] = 1 - out[y:y + 160] * np.array([.3, 1, 1])
    return out

# ---------------- video readers
_caps = {}
def vframe(path, sec):
    c = _caps.setdefault(path, cv2.VideoCapture(path)); c.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    ok, f = c.read()
    if not ok:
        c.set(cv2.CAP_PROP_POS_FRAMES, max(0, c.get(7) - 2)); ok, f = c.read()
    return cv2.cvtColor(f, cv2.COLOR_BGR2RGB).astype(np.float32) / 255

# ---------------- precompute assets
print('prep', flush=True)
P = {}
dome = load(A + 'B01_mit_dome_c_night.jpg')
P['mit_bg'] = blur(cover(dome, .5, .42, 1.0) * np.array([.86, .92, 1.05]), 1.0) * .9
P['mit_txt'] = text_mask('MIT', inter(400, 860), (640, 1080), 'ms', tracking=-6)
ya = load(A + 'B01_wang_young_a.jpg'); fm = human_matte(ya)
cr = ya[110:830, 1060:1420] * np.array([.95, .97, 1.03]); al = fm[110:830, 1060:1420].copy(); al[:, :70] = 0
P['mit_w'] = layer_of(cr, al, 300, 1960, 1180)

page = load(A + 'B04_scaleapi_2016_a_jun24.png')[0:1100]; P['sc_page'] = page
pp = load(A + 'B05_producthunt_2016_a.png')[0:1500]; P['ph_page'] = pp
post = load(A + 'B13_july_post_a.png')[0:1500]; P['post'] = post

car = load(A + 'B07_cruise_car_b.jpg')[1100:4100, 900:7000]
P['car'] = layer_of(car, object_matte(car), 540, 1390, 470)
f_cr = inter(320, 860)
letters, x = [], 540 - (sum(tlen(ch, f_cr) for ch in 'Cruise') - 8 * 5) / 2
for ch in 'Cruise':
    letters.append(text_mask(ch, f_cr, (x, 980), 'ls')); x += tlen(ch, f_cr) - 8
P['cr_letters'] = letters
P['studio'] = studio((0.95, 0.95, 0.94), (0.78, 0.78, 0.79))

pr = load(A + 'B12_wang_recent_a.jpg')[400:7200, 200:5560]
small = cv2.resize(pr, (1072, 1360), interpolation=cv2.INTER_AREA)
P['meta'] = layer_of(small, human_matte(small), 540, 1930, 1300)
f_me = inter(360, 860); letters, x = [], 540 - (sum(tlen(ch, f_me) for ch in 'Meta') - 8 * 3) / 2
for ch in 'Meta':
    letters.append(text_mask(ch, f_me, (x, 820), 'ls')); x += tlen(ch, f_me) - 8
P['me_letters'] = letters
P['studio2'] = studio((0.94, 0.94, 0.95), (0.80, 0.81, 0.84))

yb = load(A + 'B01_wang_young_b.jpg'); fm2 = object_matte(yb)
ys, xs = np.where(fm2 > .5)
y0, y1, x0, x1 = max(0, ys.min() - 20), ys.max(), max(0, xs.min() - 20), min(yb.shape[1], xs.max() + 20)
crop = yb[y0:y1, x0:x1]; a2 = fm2[y0:y1, x0:x1].copy(); a2[-14:] = 0
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)); border = np.clip(cv2.dilate(a2, k) - a2, 0, 1)
stick = crop * a2[..., None] + .97 * border[..., None]; sa = np.clip(a2 + border, 0, 1)
P['sticker'] = layer_of(stick, sa, 540, 1300, 640)

P['plate'] = cover(load(A + 'B11_ai_huge_budgets_b.png'), .5, .55, 1.0)
P['tyler'] = cover(load('/home/claude/sb3/tyler_order.jpg'), .36, .5, 1.35) * .92
P['fridge_txt'] = text_mask('fridge.', ImageFont.truetype(SERIF_I, 300), (540, 470), 'ms')
f_cnt = inter(170, 800, 32)
while tlen('×1,000,000', f_cnt) > 930: f_cnt = inter(f_cnt.size - 6, 800, 32)
P['f_cnt'] = f_cnt
DASH = A + 'B08_dashcam_night_a.mp4'; EXPO = A + 'B09_expo_floor_a.mp4'; CV19 = A + 'B09_expo_floor_c_cvpr2019.mp4'; CRN = A + 'B07_cruise_night_a.mp4'
print('prep done', flush=True)

def plane_img(bg, page, quad, dim=0.0):
    h, w = page.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    warped = cv2.warpPerspective(page, M, (W, H), flags=cv2.INTER_LINEAR)
    al = cv2.warpPerspective(np.ones((h, w), np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
    sh = blur(np.roll(al, 40, 0), 40) * .6; img = bg * (1 - sh[..., None])
    img = img * (1 - al[..., None]) + warped * al[..., None]
    if dim: img = img * (1 - dim * al[..., None])
    return img, al, M

def lerpq(q0, q1, u): return [[a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u] for a, b in zip(q0, q1)]

# ---------------- beats: f(t, t0, u, i, base) -> 1080 image
def b_mit(t, t0, u, i, base):
    img = warp(P['mit_bg'], M_about(1 + .06 * u, 540, 900))
    e = eo(t0 / .35)
    mk = warp0(P['mit_txt'], M_about(1 + .03 * u, 640, 1000, 0, 90 * (1 - e)))
    img = img * (1 - (blur(np.roll(mk, 10, 0), 20) * .35 * e)[..., None]); img = add(img, blur(mk, 30), WARM, .2 * e); img = comp(img, mk, WARM, e)
    rgb, a = P['mit_w']; e2 = eo((t0 - .08) / .4)
    M = M_about((1.04 - .04 * e2) * (1 + .04 * u), 300, 1700, -150 * (1 - e2), 0)
    a_w = warp0(a, M); img = img * (1 - (blur(np.roll(a_w, 24, 0), 30) * .5)[..., None]); img = over(img, warp0(rgb, M), a_w)
    img = finish(img, i)
    img = cap(img, [('At', 4.96), ('MIT', 5.12), ('Alexandr', 5.68), ('Wang', 6.08)], t, 330)
    return 1 - img if t0 < 2 / FPS else img

def b_counter(t, t0, u, i, base):
    ur = eo(t0 / .7); val = int(round(10 ** (6 * ur)))
    txt = f'×{val:,}'
    k = cl(t0 / .1)
    mk = text_mask(txt, P['f_cnt'], (540, 1150), 'ms')
    img = base * (1 - (blur(np.roll(mk, 10, 0), 20) * .6 * k)[..., None])
    pulse = .5 * np.exp(-max(0, t0 - .7) / .15) if t0 >= .7 else 0
    img = add(img, blur(mk, 30), WARM, (.2 + pulse) * k); img = comp(img, mk, WARM, k)
    return cap(img, [('a', 15.68), ('million', 15.92), ('times', 16.24), ('more', 16.56), ('data', 16.80)], t, 1270)

def b_scale(t, t0, u, i, base):
    bg = blob(canvas((0.02, 0.025, 0.04)), 540, 900, 600, (.35, .45, .7), .25)
    q = lerpq([[120, 600], [990, 520], [1020, 1300], [90, 1260]], [[70, 540], [1020, 450], [1060, 1350], [40, 1310]], eio(u))
    img, al, _ = plane_img(bg, P['sc_page'], q)
    img = img * (1 - np.linspace(.15, .55, W)[None, :, None] * al[..., None]); img = add(img, blur(al, 60), (.45, .6, 1.0), .12)
    img = finish(img, i, .65, .2)
    img = cap(img, [('one', 20.43), ('night', 20.59)], t, 360, 52)
    # tile reveal in
    if t0 < .4:
        rng = np.random.default_rng(7); T = 180
        dark = canvas((0.10, 0.11, 0.13)); out = img.copy()
        for ty in range(0, H, T):
            for tx in range(0, W, T):
                r = rng.uniform(0, .3); sl = (slice(ty, ty + T), slice(tx, tx + T))
                if t0 < r: out[sl] = dark[sl]
                elif t0 < r + 2 / FPS: out[sl] = .96
        img = out
    return img

def b_ph(t, t0, u, i, base):
    bg = blob(canvas((0.05, 0.045, 0.045)), 540, 900, 600, (1, .7, .5), .12)
    q = lerpq([[70, 440], [990, 520], [1010, 1430], [50, 1370]], [[40, 400], [1020, 470], [1040, 1460], [20, 1400]], eio(u))
    img, al, M = plane_img(bg, P['ph_page'], q, .35)
    band = np.zeros((1500, 1440), np.float32); band[150:330, 30:1000] = 1
    band = cv2.warpPerspective(cv2.GaussianBlur(band, (0, 0), 25), M, (W, H))
    img = img * (1 + .55 * eo((t0 - .15) / .4) * band[..., None])
    e = eo((t - (21.95 - LEAD)) / .3)
    if e > 0:
        mk = text_mask('a week later.', serif_i(150), (540, 1620 + 30 * (1 - e)), 'ms')
        img = img * (1 - (blur(np.roll(mk, 10, 0), 20) * .5 * e)[..., None]); img = comp(img, mk, WARM, e)
    img = finish(img, i)
    if t0 < .25:  # rotating panel wipe
        v = t0 / .25; m = np.zeros((H, W), np.float32)
        cx = -500 + 2100 * v
        pts = np.array([[cx - 260, -200], [cx + 260, -200], [cx - 140, H + 200], [cx - 660, H + 200]], np.int32)
        cv2.fillPoly(m, [pts], 1.0); img = img * (1 - blur(m, 3)[..., None] * .95)
    return img

def b_eng(t, t0, u, i, base):
    cuts = [(0, .55, CV19, .3), (.55, 1.05, EXPO, 1.2), (1.05, 9, CV19, 2.4)]
    for a, b, p, s0 in cuts:
        if a <= t0 < b:
            fr = vframe(p, s0 + (t0 - a)); uu = (t0 - a) / max(.3, min(b, 1.6) - a)
            img = warp(cover(fr, .5, .5, 1.05) * np.array([.92, .95, 1.02]), M_about(1 + .08 * uu, 540, 960)); break
    img = finish(img, i)
    return cap(img, [('random', 24.27), ('engineers', 24.67), ('showed', 25.31), ('up', 25.47)], t, 1250, 52)

def b_cruise(t, t0, u, i, base):
    if t0 < .9:
        seg = 0 if t0 < .45 else 1; s0 = [0.5, 2.5][seg]; uu = (t0 - .45 * seg) / .45
        img = warp(cover(vframe(CRN, s0 + t0 - .45 * seg), .5, .5, 1.0), M_about(1 + .07 * uu, 540, 960))
        img = finish(img, i)
        return cap(img, [('then', 25.87), ('Cruise', 26.11), ('reached', 26.59), ('out', 26.83)], t, 420, 52)
    h0 = t0 - .9; uh = h0 / (3.3 - .9)
    img = P['studio'].copy()
    for k_, mk in enumerate(P['cr_letters']):
        e = eb((h0 - .08 - .05 * k_) / .3)
        if e > 0:
            m2 = warp0(mk, M_about(1, 540, 900, 0, -80 * (1 - e)))
            img = comp(img, m2, (1.0, 0.36, 0.20), cl(e))
    rgb, a = P['car']; M = M_about(1 + .05 * uh, 540, 1300, -20 * (1 - eo(uh * 2)), 0)
    a_w = warp0(a, M); img = img * (1 - (blur(np.roll(a_w, 24, 0), 30) * .55)[..., None])
    if h0 < 2 / FPS: img = comp(img, a_w, (1.0, 0.36, 0.20), 1)
    else: img = over(img, warp0(rgb, M), a_w)
    img = finish(img, i, .45, .04)
    return cap(img, [('then', 25.87), ('Cruise', 26.11), ('reached', 26.59), ('out', 26.83)], t, 420, 52, (0.1, 0.1, 0.11))

def b_dash(t, t0, u, i, base):
    img = cover(vframe(DASH, 1.6 + t0), .5, .5, 1.0) * .95
    img = warp(img, M_about(1 + .04 * u, 540, 1100))
    img = finish(img, i, .45, .2)
    boxes = [(110, 1036, 390, 1230), (610, 1024, 718, 1158), (448, 1070, 506, 1176), (875, 1086, 1000, 1170)]
    for k_, (x0, y0, x1, y1) in enumerate(boxes):
        e = eo((t0 - .2 - .28 * k_) / .18)
        if e > 0:
            img = comp(img, box_mask(x0, y0, x1, y1, 3, max(2, int(22 * e))), WARM, 1)
            img = comp(img, box_mask(x0, y0, x1, y1, 1), WARM, .3 * e)
    return cap(img, [('all', 31.15), ('in', 31.31), ('on', 31.47), ('self-driving', 31.55)], t, 420, 52)

def b_booth(t, t0, u, i, base):
    img = blur(cover(vframe(EXPO, .5 + t0), .5, .5, 1.0), 6) * .7
    pts = [(300, 1330), (560, 1270), (800, 1330)]; hops = [33.2, 34.1, 34.85]
    pos = pts[0]; lift = 0; sq = 1.0
    for k_, ht in enumerate(hops[:2]):
        if t >= ht:
            v = cl((t - ht) / .35); a_, b_ = pts[k_], pts[k_ + 1]
            pos = (a_[0] + (b_[0] - a_[0]) * eio(v), a_[1] + (b_[1] - a_[1]) * eio(v)); lift = 160 * 4 * v * (1 - v)
            if v >= 1: pos = b_
    pop = eb((t0 - .05) / .3)
    rot = 2.5 if (i // 3) % 2 else -2.5
    rgb, a = P['sticker']
    M = M_about(max(.01, pop), 540, 1300, pos[0] - 540, pos[1] - 1300 - lift, rot)
    a_w = warp0(a, M); img = img * (1 - (blur(np.roll(a_w, 30, 0), 26) * .6)[..., None]); img = over(img, warp0(rgb, M), a_w)
    img = finish(img, i, .55, .12)
    return cap(img, [('booth', 34.59), ('to', 34.83), ('booth', 34.99)], t, 380, 54)

def b_formula(t, t0, u, i, base):
    img = blob(canvas((0.05, 0.048, 0.045)), 540, 800, 600, (1, .9, .8), .05)
    lines = [('Launch broad.', inter(120, 780), 560, 36.04, False), ("Find who's", inter(120, 300), 710, 36.92, False),
             ('desperate.', inter(120, 300), 845, 37.40, False), ('Go in,', inter(120, 780), 1010, 38.04, False),
             ('even if it looks small', serif_i(96), 1140, 38.44, True)]
    for txt, f, y, wt, it in lines:
        e = eo((t - (wt - LEAD)) / .25)
        if e > 0:
            mk = text_mask(txt, f, (104 if it else 100, y + 40 * (1 - e)))
            img = glow_text(img, mk, WARM, .6 * e, .3 * e) if it else comp(img, mk, WARM, e)
    img = warp(img, M_about(1 + .03 * u, 540, 900))
    img = finish(img, i, .6, .12)
    if t0 < 4 / FPS: img = img + (1 - img) * (1 - t0 / (4 / FPS))
    return img

def b_budget(t, t0, u, i, base):
    img = warp(P['plate'], M_about(1 + .05 * u, 540, 1300))
    e1 = eo((t - (41.64 - LEAD)) / .3)
    if e1 > 0: img = comp(img, text_mask('a few customers,', inter(84, 320), (540, 470 + 20 * (1 - e1)), 'ms'), (0.12, 0.2, 0.2), e1)
    e2 = eb((t - (42.84 - LEAD)) / .3)
    if e2 > 0:
        mk = warp0(text_mask('huge budgets.', inter(120, 820), (540, 600), 'ms'), M_about(.85 + .15 * e2, 540, 560))
        img = comp(img, mk, (0.12, 0.2, 0.2), cl(e2))
    return finish(img, i, .45, .05)

def b_meta(t, t0, u, i, base):
    img = P['studio2'].copy()
    for k_, mk in enumerate(P['me_letters']):
        e = eo((t0 - .1 - .05 * k_) / .3)
        if e > 0: img = comp(img, warp0(mk, M_about(1, 540, 700, 0, 90 * (1 - e))), (0.06, 0.40, 0.98), e)
    rgb, a = P['meta']; M = M_about(1 + .04 * u, 540, 1800)
    a_w = warp0(a, M); img = img * (1 - (blur(np.roll(a_w, 24, 0), 30) * .4)[..., None])
    img = comp(img, a_w, (0.06, 0.40, 0.98), 1) if t0 < 2 / FPS else over(img, warp0(rgb, M), a_w)
    img = finish(img, i, .45, .04)
    return cap(img, [('now', 45.32), ('running', 45.56), ('AI', 45.80), ('at', 46.20), ('Meta', 46.28)], t, 420, 52, (0.1, 0.1, 0.11))

def b_post(t, t0, u, i, base):
    bg = blob(canvas((0.035, 0.035, 0.04)), 540, 900, 650, (.6, .7, 1), .12)
    q = lerpq([[130, 450], [980, 490], [990, 1370], [110, 1330]], [[90, 410], [1010, 440], [1020, 1400], [70, 1360]], eio(u))
    img, al, M = plane_img(bg, P['post'], q, .3)
    cxb = -300 + 2200 * eio(t0 / .9)
    band = np.zeros((1500, 1650), np.float32); band[150:420, :] = 1
    xx = np.arange(1650)[None, :]; band = band * np.exp(-((xx - cxb) / 380) ** 2)
    band = cv2.warpPerspective(cv2.GaussianBlur(band, (0, 0), 20), M, (W, H))
    img = img * (1 + .6 * band[..., None])
    img = finish(img, i)
    return glitch(img, i, 1 - t0 / (3 / FPS)) if t0 < 3 / FPS else img

def b_tyler(t, t0, u, i, base):
    img = warp(P['tyler'], M_about(1 + .08 * u, 540, 700))
    e = eo((t - (48.68 - LEAD)) / .3)
    if e > 0: img = comp(img, text_mask('refill your fridge', serif_i(120), (540, 1500 + 25 * (1 - e)), 'ms'), (0.10, 0.10, 0.11), e)
    return finish(img, i, .55, .05)

def b_fridge(t, t0, u, i, base):
    e = eb((t - (49.24 - LEAD)) / .3)
    if e <= 0: return base
    al = human_matte(base)
    mk = warp0(P['fridge_txt'], M_about(1, 540, 400, 0, -120 * (1 - e)))
    lay = base * (1 - (blur(np.roll(mk, 10, 0), 18) * .35)[..., None]); lay = add(lay, blur(mk, 30), WARM, .12); lay = comp(lay, mk, WARM, cl(e))
    return base * al[..., None] + lay * (1 - al[..., None])

def b_end(t, t0, u, i, base):
    cream = vignette(canvas((0.97, 0.95, 0.90)), .45)
    txt = 'full circle.'; n = int(cl((t0 - .2) / (.06 * len(txt))) * len(txt))
    if n: cream = comp(cream, text_mask(txt[:n], serif_i(150), (540 - tlen(txt, serif_i(150)) / 2, 980), 'ls'), (0.13, 0.12, 0.11), 1)
    cream = grain(cream, .015, i)
    if t0 < .25:
        v = t0 / .25
        return base + (1 - base) * (v / .5) if v < .5 else np.ones_like(base) + (cream - 1) * ((v - .5) / .5)
    return cream

SEG = [(5.1, 6.6, b_mit), (15.6, 18.7, b_counter), (19.6, 20.8, b_scale), (20.8, 22.5, b_ph), (24.3, 25.9, b_eng),
       (25.9, 29.2, b_cruise), (30.5, 32.4, b_dash), (32.4, 35.4, b_booth), (36.1, 39.6, b_formula), (41.6, 43.6, b_budget),
       (44.4, 46.8, b_meta), (46.8, 48.0, b_post), (48.0, 49.0, b_tyler), (49.0, 51.2, b_fridge), (51.2, 52.8, b_end)]

if __name__ == '__main__':
    a_, b_ = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    cap_src = cv2.VideoCapture(SRC)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{PW}x{PH}', '-r', '24000/1001', '-i', '-',
                            '-i', SRC, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUTF], stdin=subprocess.PIPE)
    i = 0
    while True:
        ok, fr = cap_src.read()
        if not ok: break
        t = i / FPS
        base = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        seg = next((s for s in SEG if s[0] <= t < s[1]), None)
        if seg:
            a, b, fn = seg; img = fn(t, t - a, (t - a) / (b - a), i, base)
        elif 10.33 <= t < 10.50:   # glitch on "couldn't" (fridge beat still waiting on footage)
            img = glitch(base, i, 1 - (t - 10.33) / .17)
        else:
            img = base
        img = caps_block.draw(img, t)
        out = cv2.resize(np.clip(img, 0, 1), (PW, PH), interpolation=cv2.INTER_AREA)
        o8 = (out * 255 + .5).astype(np.uint8)
        tc = f'{int(t // 60)}:{t % 60:05.2f}'
        cv2.rectangle(o8, (10, 10), (150, 42), (0, 0, 0), -1)
        cv2.putText(o8, tc, (18, 34), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 230, 120), 2, cv2.LINE_AA)
        enc.stdin.write(o8.tobytes()); i += 1
        if i % 100 == 0: print('frame', i, flush=True)
    enc.stdin.close(); enc.wait(); print('done', i)
