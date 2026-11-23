import sys, numpy as np, cv2
from kit import *
OUT = '/home/claude/sb/out/'
import os; os.makedirs(OUT, exist_ok=True)
PAPER = (0.925, 0.905, 0.855)
PINK = np.array([0.20, 0.19, 0.18])  # ink on paper

# ---------------------------------------------------------------- shared plates
def fridge_plate(light=1.0, door=1.0):
    """inside the fridge, looking out. cold lamp from top, glass shelves, a few silhouettes."""
    img = vgrad((0.50, 0.58, 0.66), (0.10, 0.12, 0.15), 0.8) * light
    img = blob(img, 540, 210, 360, COOL, .55 * light)
    # back-wall panel lines
    for x in (150, 930):
        img = comp(img, blur(line_mask([(x, 0), (x, H)], 3), 2), (0.30, 0.34, 0.40), .5 * light)
    for y, sh in ((640, 1), (1130, 1), (1600, 1)):
        img = comp(img, rect_mask(0, y, W, y + 26, 0, 3), (0.80, 0.88, 0.96), .55 * light)   # glass edge
        img = comp(img, blur(rect_mask(0, y + 26, W, y + 120), 30), (0.0, 0.0, 0.0), .45)      # shadow under
    def item(x0, y0, x1, y1, r, c=(0.12, 0.13, 0.15)):
        nonlocal img
        img = comp(img, rect_mask(x0, y0, x1, y1, r, 1.2), c, .96)
        img = comp(img, rect_mask(x0 + 6, y0 + 4, x0 + 16, y1 - 10, 4, 3), COOL, .35 * light)  # rim light
    # top shelf: jars
    item(210, 470, 330, 640, 26); item(360, 420, 470, 640, 30); item(760, 500, 880, 640, 18)
    # milk carton
    item(560, 380, 690, 640, 6, (0.80, 0.82, 0.84))
    img = comp(img, rect_mask(560, 470, 690, 560, 0, 1), (0.30, 0.36, 0.45), .8)
    # middle shelf: his takeout box with the note
    item(300, 930, 640, 1130, 16, (0.17, 0.15, 0.13))
    item(700, 980, 830, 1130, 40)
    img = paper(img, 360, 965, 590, 1080, -3, (0.94, 0.93, 0.88), seed=7, shadow=.4,
                content=lambda c: local_text(local_text(c, "DON'T.", font(MONO_M, 40), (18, 58), RED * .85),
                                             '— A.W.', font(MONO, 28), (20, 96), PINK))
    # bottom shelf
    item(180, 1430, 420, 1600, 20); item(470, 1470, 600, 1600, 12); item(660, 1400, 900, 1600, 24)
    # door edge / room beyond on the right
    if door < 1:
        dark = np.zeros((H, W), np.float32); x = int(W * door)
        dark[:, x:] = 1; dark = blur(dark, 8)
        img = img * (1 - dark[..., None] * .96)
    img = vignette(img, .5)
    return img

def cctv(img, ts='02:14:07', rec=True):
    f = font(MONO_M, 34)
    img = comp(img, box_mask(80, 260, 1000, 1290, 4, 60), WARM, .85)
    if rec:
        img = comp(img, blur(rect_mask(110, 296, 140, 326, 15), .8), RED, 1)
        img = comp(img, text_mask('REC', f, (156, 324)), WARM, .95)
    img = comp(img, text_mask('CAM 01 · FRIDGE', font(MONO, 30), (970, 324), 'rs'), WARM, .85)
    img = comp(img, text_mask(ts, font(MONO, 30), (970, 1260), 'rs'), WARM, .85)
    img = comp(img, text_mask('MIT · EAST CAMPUS', font(MONO, 26), (112, 1260)), WARM, .6)
    return img

def tag(img, x, y, txt, color=WARM, ink=INK, size=30):
    f = font(MONO_M, size); w = tlen(txt, f)
    img = comp(img, rect_mask(x, y - size - 14, x + w + 24, y + 6), color, .95)
    return comp(img, text_mask(txt, f, (x + 12, y - 4)), ink, 1)

def arm(img, tip_x, tip_y, a=1.0):
    """forearm + hand reaching in from the right, lit by the fridge lamp"""
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    wx = tip_x + 150                                    # wrist x
    d.polygon([(W + 60, tip_y - 95), (wx, tip_y - 38), (wx, tip_y + 42), (W + 60, tip_y + 120)], fill=255)  # forearm
    d.ellipse([tip_x + 55, tip_y - 50, wx + 25, tip_y + 52], fill=255)                                      # palm
    for i, (dy, ln) in enumerate(((-34, 92), (-11, 104), (12, 98), (33, 80))):                               # fingers
        y = tip_y + dy
        d.rounded_rectangle([tip_x + 85 - ln, y - 11, tip_x + 95, y + 11], 11, fill=255)
    d.polygon([(tip_x + 120, tip_y + 30), (tip_x + 60, tip_y + 78), (tip_x + 48, tip_y + 64), (tip_x + 100, tip_y + 18)], fill=255)  # thumb
    mk = blur(np.asarray(m, np.float32) / 255, 1.6)
    img = comp(img, mk, (0.23, 0.16, 0.13), .98 * a)
    shade = blur(np.clip(mk - np.roll(mk, -14, 0), 0, 1), 6)              # darker underside
    img = img * (1 - (shade * .45 * a)[..., None])
    rim = np.clip(mk - np.roll(mk, 4, 0), 0, 1)
    return add(img, blur(rim, 1.2), COOL, .75 * a)

def dossier(img, title, lines, photo_label, angle=-2.5, seed=11, stamp=None):
    def content(c):
        h, w = c.shape[:2]
        c = local_text(c, 'FILE 01', font(MONO_M, 26), (44, 70), PINK * 1.6, tracking=4)
        c = local_text(c, 'SUBJECT', font(MONO, 22), (44, 700), PINK * 1.8, tracking=3)
        c = local_text(c, title, font(SERIF, 92), (44, 790), PINK)
        y = 860
        for l in lines:
            c = local_text(c, l, font(MONO, 27), (46, y), PINK * 1.3); y += 44
        # photo slot (halftone grey placeholder silhouette)
        ph = np.ones((520, w - 88, 3), np.float32) * .55
        yy, xx = np.mgrid[0:520, 0:w - 88]
        cx = (w - 88) / 2
        head = ((xx - cx) ** 2 / 95 ** 2 + (yy - 210) ** 2 / 120 ** 2) < 1
        body = ((xx - cx) ** 2 / 260 ** 2 + (yy - 600) ** 2 / 230 ** 2) < 1
        ph[head | body] = .24
        ph = cv2.GaussianBlur(ph, (0, 0), 2)
        # tiny halftone on the photo
        a = np.deg2rad(45); u = (xx * np.cos(a) + yy * np.sin(a)) / 6; v = (-xx * np.sin(a) + yy * np.cos(a)) / 6
        dd = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2)
        dots = (dd < np.sqrt(ph.mean(2)) * .6).astype(np.float32)
        ph = ph * .4 + dots[..., None] * .55
        c[110:630, 44:w - 44] = ph
        c = local_text(c, photo_label, font(MONO, 20), (60, 612), (0.95, 0.94, 0.9), tracking=2)
        return c
    img = paper(img, 170, 300, 910, 1260, angle, PAPER, seed=seed, shadow=.65, content=content)
    if stamp:
        f = font(MONO_M, 40)
        mk = text_mask(stamp, f, (660, 1170), 'ms', tracking=6)
        mk = cv2.warpAffine(mk, cv2.getRotationMatrix2D((660, 1155), 8, 1), (W, H))
        bx = cv2.warpAffine(box_mask(660 - tlen(stamp, f) / 2 - 60, 1115, 660 + tlen(stamp, f) / 2 + 60, 1188, 5),
                            cv2.getRotationMatrix2D((660, 1155), 8, 1), (W, H))
        img = comp(img, np.clip(mk + bx, 0, 1), RED * .9, .85)
    return img

def desk():
    img = vgrad((0.075, 0.068, 0.060), (0.030, 0.027, 0.024))
    img = blob(img, 520, 780, 520, (1.0, .9, .75), .10)
    return vignette(img, .6)

def finish(img, ht=True, seed=1):
    if ht: img = halftone(img, 7, .30)
    return grain(img, .02, seed)

# ---------------------------------------------------------------- frames
def f01():  # At MIT, Alexandr Wang
    img = desk()
    img = dossier(img, 'Alexandr Wang', ['MIT · EAST CAMPUS', 'FRESHMAN, 2015'], 'PHOTO · WANG, 2015 · YOUR PICK')
    img = finish(img)
    return caption(img, 'At MIT Alexandr Wang')

def f02():  # build a camera to catch them
    img = fridge_plate(1.0, 1.0)
    img = arm(img, 660, 1035)
    img = finish(img, True, 2)
    img = cctv(img)
    img = comp(img, box_mask(560, 960, 1000, 1130, 4), WARM, 1)
    img = tag(img, 560, 948, 'PERSON  0.41')
    return caption(img, 'so he tried to build a camera')

def f03():  # It couldn't work
    img = fridge_plate(1.0, 1.0)
    img = arm(img, 660, 1035)
    img = finish(img, True, 3)
    img = cctv(img, '02:14:09')
    img = comp(img, line_mask([(600, 940), (1000, 940), (1000, 1150), (600, 1150), (600, 940)], 4, (22, 14)), RED, 1)
    img = tag(img, 600, 928, 'MILK  0.38', RED, WARM)
    img = comp(img, line_mask([(195, 455), (345, 455), (345, 655), (195, 655), (195, 455)], 4, (22, 14)), RED, .9)
    img = tag(img, 195, 443, 'PERSON  0.12', RED, WARM)
    img = comp(img, text_mask('NO MATCH', font(MONO_M, 30), (540, 1262), 'ms', tracking=8), RED, 1)
    return caption(img, "It couldn't work")

def f04():  # archival overlay x1,000,000
    cap = cv2.VideoCapture('/home/claude/work/arch_v2.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, 130)
    ok, fr = cap.read()
    img = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    img = img * .78
    img = halftone(img, 7, .22)
    f = font(SERIF, 178)
    mk = text_mask('×1,000,000', f, (478, 1170), 'ms')
    img = glow_text(img, mk, WARM, 1.1, .7)
    img = comp(img, text_mask('MORE DATA', font(MONO_M, 30), (478, 1250), 'ms', tracking=10), WARM, .9)
    img = grain(img, .02, 4)
    return caption(img, 'than I have now')

def f05():  # scaleapi.com one night
    img = vgrad((0.05, 0.05, 0.055), (0.02, 0.02, 0.022))
    img = blob(img, 540, 820, 420, COOL, .07)
    img = comp(img, rect_mask(110, 760, 970, 880, 60), (0.11, 0.11, 0.12), 1)
    img = comp(img, np.clip(rect_mask(110, 760, 970, 880, 60) - rect_mask(113, 763, 967, 877, 57), 0, 1), WARM, .35)
    f = font(MONO, 50)
    img = comp(img, text_mask('scaleapi.com', f, (190, 836)), WARM, 1)
    x = 190 + tlen('scaleapi.com', f) + 8
    img = comp(img, rect_mask(x, 790, x + 5, 850), WARM, 1)
    img = comp(img, text_mask('●', font(MONO, 30), (150, 832), 'ms'), (0.4, 0.4, 0.42), 1)
    img = comp(img, text_mask('2:47 AM', font(SERIF, 120), (540, 640), 'ms'), WARM, .9)
    img = comp(img, text_mask('ONE NIGHT · 2016', font(MONO, 26), (540, 1000), 'ms', tracking=8), WARM, .45)
    img = finish(img, True, 5)
    return caption(img, 'So he bought scaleapi.com')

def f06():  # Product Hunt (real screenshot placeholder)
    img = desk()
    def content(c):
        h, w = c.shape[:2]
        c[:] = (0.97, 0.97, 0.96)
        for i, (y, ww) in enumerate([(70, .35), (150, .7), (205, .55)]):
            c[y:y + (34 if i else 26), 40:40 + int(w * ww)] = (0.80, 0.80, 0.80)
        c[300:380, 40:w - 40] = (0.86, 0.86, 0.85)
        for y in range(440, 820, 70): c[y:y + 22, 40:w - 40 - (y % 3) * 60] = (0.88, 0.88, 0.88)
        c = local_text(c, 'REAL SCREENSHOT GOES HERE', font(MONO_M, 24), (40, 900), (0.55, 0.55, 0.55), tracking=3)
        c = local_text(c, 'Scale API · Product Hunt, 2016', font(MONO, 24), (40, 940), (0.55, 0.55, 0.55))
        return c
    img = paper(img, 170, 330, 910, 1250, 2, (0.97, 0.97, 0.96), seed=12, shadow=.7, content=content)
    # highlighter swipe on the tagline line
    hl = rect_mask(205, 625, 875, 715, 6, 2)
    hl = cv2.warpAffine(hl, cv2.getRotationMatrix2D((540, 670), 2, 1), (W, H))
    img = img * (1 - hl[..., None] * .55) + hl[..., None] * .55 * np.array([0.98, 0.86, 0.55])
    img = comp(img, text_mask('tagline  →  highlight', font(MONO, 22), (540, 770), 'ms'), PINK, .7)
    img = finish(img, True, 6)
    return caption(img, 'launched on Product Hunt')

def street_plate(seed=8):
    rng = np.random.default_rng(seed)
    img = vgrad((0.04, 0.045, 0.06), (0.10, 0.08, 0.06), 1.2)
    for _ in range(26):
        x, y = rng.uniform(60, 1020), rng.uniform(250, 900)
        c = [(1, .75, .45), (.9, .95, 1), (1, .45, .35)][rng.integers(3)]
        img = blob(img, x, y, rng.uniform(14, 46), c, rng.uniform(.10, .35))
    # wet road reflections
    for _ in range(14):
        x = rng.uniform(80, 1000)
        m = blur(rect_mask(x - 6, 1050, x + 6, 1700), 10)
        img = add(img, m, (1, .7, .45), rng.uniform(.05, .18))
    return vignette(img, .5)

def f07():  # Cruise reached out through their website
    img = street_plate()
    img = comp(img, text_mask('YOUR FOOTAGE · CRUISE ROBOTAXI, SF NIGHT', font(MONO, 22), (540, 290), 'ms', tracking=3), WARM, .45)
    img = finish(img, True, 7)
    def content(c):
        c = local_text(c, 'WEBSITE INQUIRY', font(MONO_M, 24), (40, 62), PINK * 1.6, tracking=4)
        c = local_text(c, 'From: Cruise', font(SERIF, 86), (40, 160), PINK)
        c = local_text(c, 'via scaleapi.com', font(MONO, 26), (42, 212), PINK * 1.4)
        return c
    img = paper(img, 170, 900, 910, 1150, -2, PAPER, seed=14, shadow=.7, content=content)
    img = comp(img, blur(rect_mask(850, 905, 880, 935, 15), .6), RED, 1)
    return caption(img, 'then Cruise reached out')

def f08():  # self-driving labelling
    img = vgrad((0.05, 0.05, 0.065), (0.09, 0.075, 0.06), 1.0)
    hz = 760
    for x in (180, 900): img = blob(img, x, hz - 120, 60, (1, .8, .5), .4)
    road = Image.new('L', (W, H), 0); d = ImageDraw.Draw(road)
    d.polygon([(500, hz), (580, hz), (1300, H), (-220, H)], fill=255)
    img = comp(img, blur(np.asarray(road, np.float32) / 255, 2), (0.11, 0.10, 0.10), 1)
    for k in range(7):
        t0, t1 = (k / 7) ** 1.8, ((k + .45) / 7) ** 1.8
        y0, y1 = hz + (H - hz) * t0, hz + (H - hz) * t1
        w0, w1 = 3 + 14 * t0, 3 + 14 * t1
        lm = Image.new('L', (W, H), 0); ImageDraw.Draw(lm).polygon([(540 - w0, y0), (540 + w0, y0), (540 + w1, y1), (540 - w1, y1)], fill=255)
        img = comp(img, np.asarray(lm, np.float32) / 255, WARM, .55)
    # car ahead
    img = comp(img, rect_mask(400, 840, 650, 1010, 30, 1.5), (0.05, 0.05, 0.06), 1)
    for x in (420, 595): img = add(blur(rect_mask(x, 930, x + 35, 950, 6), 3), 0, RED, 0) if False else blob(img, x + 17, 940, 18, RED, .9)
    # pedestrian
    p = Image.new('L', (W, H), 0); d = ImageDraw.Draw(p)
    d.ellipse([796, 770, 846, 822], fill=255); d.rounded_rectangle([782, 826, 860, 1000], 30, fill=255)
    d.polygon([(790, 990), (812, 990), (800, 1130), (778, 1130)], fill=255); d.polygon([(832, 990), (854, 990), (880, 1125), (858, 1128)], fill=255)
    img = comp(img, blur(np.asarray(p, np.float32) / 255, 1.2), (0.03, 0.03, 0.035), 1)
    # cyclist
    c = Image.new('L', (W, H), 0); d = ImageDraw.Draw(c)
    for cx in (175, 285): d.ellipse([cx - 45, 1010, cx + 45, 1100], outline=255, width=6)
    d.line([(175, 1055), (225, 990), (285, 1055)], fill=255, width=6); d.ellipse([212, 900, 246, 934], fill=255)
    d.line([(229, 934), (222, 990)], fill=255, width=14)
    img = comp(img, blur(np.asarray(c, np.float32) / 255, 1.2), (0.03, 0.03, 0.035), 1)
    # plastic bag
    b = Image.new('L', (W, H), 0); ImageDraw.Draw(b).polygon([(600, 1250), (650, 1222), (700, 1245), (690, 1300), (640, 1312), (598, 1290)], fill=255)
    img = comp(img, blur(np.asarray(b, np.float32) / 255, 2), (0.75, 0.75, 0.72), .85)
    img = finish(img, True, 8)
    for (x0, y0, x1, y1, t, col) in [(390, 830, 660, 1020, 'car  0.98', WARM), (760, 755, 895, 1145, 'pedestrian  0.97', WARM),
                                      (120, 890, 340, 1110, 'cyclist  0.91', WARM), (585, 1210, 715, 1325, 'plastic bag  0.64', RED)]:
        img = comp(img, box_mask(x0, y0, x1, y1, 4, 26), col, 1)
        img = comp(img, box_mask(x0, y0, x1, y1, 1), col, .35)
        img = tag(img, x0, y0 - 6, t, col, INK if col is WARM else WARM, 24)
    img = comp(img, text_mask('YOUR FOOTAGE · NIGHT DASHCAM  /  MY BOXES ON TOP', font(MONO, 22), (540, 290), 'ms', tracking=2), WARM, .45)
    return caption(img, 'all in on self-driving')

def f09():  # booth to booth
    img = vgrad((0.06, 0.055, 0.05), (0.03, 0.028, 0.025))
    img = blob(img, 540, 800, 500, (1, .9, .75), .06)
    cols, rows = 3, 5
    bw, bh, gx, gy = 220, 150, 70, 56
    x0, y0 = 540 - (cols * bw + (cols - 1) * gx) / 2, 380
    centers = []
    k = 0
    for r in range(rows):
        for cc in range(cols):
            x, y = x0 + cc * (bw + gx), y0 + r * (bh + gy)
            img = comp(img, np.clip(rect_mask(x, y, x + bw, y + bh, 4) - rect_mask(x + 2, y + 2, x + bw - 2, y + bh - 2, 3), 0, 1), WARM, .45)
            img = comp(img, text_mask(f'B-{11 + k:02d}', font(MONO, 22), (x + 14, y + 34)), WARM, .45)
            centers.append((x + bw / 2, y + bh + gy / 2)); k += 1
    path = [(x0 - 30, 1430), centers[12], centers[13], centers[10], centers[7], centers[8], centers[5], centers[2]]
    img = comp(img, line_mask([(p[0], p[1]) for p in path], 4, (16, 14)), RED, 1)
    for p in path[1:]:
        img = comp(img, blur(rect_mask(p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9, 9), .6), RED, 1)
    img = finish(img, True, 9)
    # the sticker cutout (placeholder for his photo of Wang)
    sx, sy = centers[8]
    img = comp(img, blur(rect_mask(sx - 74, sy - 180, sx + 74, sy + 6, 60), 12), (0, 0, 0), .55)
    img = comp(img, rect_mask(sx - 70, sy - 190, sx + 70, sy - 2, 56), (0.96, 0.95, 0.92), 1)
    img = comp(img, rect_mask(sx - 56, sy - 176, sx + 56, sy - 16, 46), (0.32, 0.32, 0.33), 1)
    img = comp(img, text_mask('WANG', font(MONO_M, 20), (sx, sy - 90), 'ms', tracking=3), (0.9, 0.9, 0.88), 1)
    img = comp(img, text_mask('CUTOUT', font(MONO, 18), (sx, sy - 64), 'ms', tracking=3), (0.9, 0.9, 0.88), .8)
    img = comp(img, text_mask('Expo floor', font(SERIF, 64), (110, 330)), WARM, .95)
    img = comp(img, text_mask('COMPUTER VISION CONFERENCE', font(MONO, 22), (970, 322), 'rs', tracking=3), WARM, .5)
    return caption(img, 'booth to booth with a laptop')

def f10():  # playbook (no caption: the graphic says the words)
    img = vgrad((0.055, 0.05, 0.045), (0.025, 0.023, 0.02))
    img = blob(img, 540, 760, 520, (1, .9, .75), .07)
    img = comp(img, text_mask('The', font(SERIF, 120), (120, 520)), WARM, .9)
    img = glow_text(img, text_mask('Playbook', font(SERIF_I, 170), (120, 670)), WARM, .9, .5)
    img = comp(img, line_mask([(120, 740), (960, 740)], 2), WARM, .35)
    items = [('01', 'Launch broad', 1.0), ('02', "Find who's desperate", 1.0), ('03', 'Go in, even if it looks small', .28)]
    y = 900
    for n, t, a in items:
        img = comp(img, text_mask(n, font(MONO, 30), (124, y - 14)), RED if a == 1 else WARM, .9 * a + .1)
        f = font(SERIF, 84)
        while tlen(t, f) > 760: f = font(SERIF, f.size - 4)
        mk = text_mask(t, f, (210, y))
        img = glow_text(img, mk, WARM, .7 * a, .4 * a) if a == 1 else comp(img, mk, WARM, a)
        img = comp(img, line_mask([(124, y + 50), (960, y + 50)], 1), WARM, .14)
        y += 170
    img = finish(img, True, 10)
    return img

def f11():  # now running AI at Meta
    img = desk()
    img = paper(img, 210, 340, 950, 1300, 4, PAPER, seed=19, shadow=.5)  # the old card underneath
    img = dossier(img, 'Alexandr Wang', ['NOW · META', 'RUNS AI · 2026'], 'PHOTO · WANG, 2025–26 · YOUR PICK', -2, 21, stamp='META')
    img = finish(img, True, 11)
    return caption(img, 'now running AI at Meta')

def f12():  # the July post (real screenshot placeholder)
    img = vgrad((0.05, 0.05, 0.055), (0.02, 0.02, 0.022))
    def content(c):
        h, w = c.shape[:2]
        c[:] = (0.07, 0.07, 0.075)
        yy, xx = np.mgrid[0:h, 0:w]
        c[((xx - 80) ** 2 + (yy - 90) ** 2) < 44 ** 2] = (0.35, 0.35, 0.36)
        c[70:96, 150:420] = (0.45, 0.45, 0.46); c[110:130, 150:330] = (0.28, 0.28, 0.29)
        for i, y in enumerate((200, 260, 320, 380)): c[y:y + 30, 40:w - 40 - i * 90] = (0.30, 0.30, 0.31)
        c = local_text(c, 'REAL POST SCREENSHOT GOES HERE', font(MONO_M, 24), (40, 500), (0.55, 0.55, 0.56), tracking=3)
        c = local_text(c, 'Wang · July 2026', font(MONO, 24), (40, 540), (0.55, 0.55, 0.56))
        return c
    img = paper(img, 120, 640, 960, 1240, 0, (0.07, 0.07, 0.075), seed=22, shadow=.8, content=content)
    img = comp(img, np.clip(rect_mask(120, 640, 960, 1240, 0) - rect_mask(122, 642, 958, 1238, 0), 0, 1), WARM, .25)
    hl = rect_mask(150, 893, 860, 935, 4)
    img = img * (1 - hl[..., None] * .5) + hl[..., None] * .5 * np.array([0.98, 0.86, 0.55])
    img = comp(img, text_mask('“…refill your fridge”  →  highlight', font(MONO, 22), (540, 1300), 'ms'), WARM, .55)
    img = finish(img, True, 12)
    return caption(img, 'refill your fridge')

def f13():  # full circle: the fridge door closes
    img = fridge_plate(0.9, 0.34)
    img = finish(img, True, 13)
    img = comp(img, text_mask('CAM 01 · OFF', font(MONO, 30), (970, 324), 'rs'), WARM, .5)
    return caption(img, 'the inspiration for Scale AI')

FR = {k: v for k, v in globals().items() if k.startswith('f') and k[1:].isdigit()}
if __name__ == '__main__':
    names = sys.argv[1:] or sorted(FR)
    for n in names:
        save(FR[n](), OUT + n + '.png'); print('ok', n)
