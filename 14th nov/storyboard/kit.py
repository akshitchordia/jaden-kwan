import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
F = '/home/claude/sb/fonts/'
SERIF, SERIF_I = F + 'InstrumentSerif-Regular.ttf', F + 'InstrumentSerif-Italic.ttf'
MONO, MONO_M = F + 'IBMPlexMono-Regular.ttf', F + 'IBMPlexMono-Medium.ttf'
WARM = np.array([1.0, 0.976, 0.941])      # #FFF9F0
RED = np.array([0.90, 0.20, 0.18])
COOL = np.array([0.86, 0.92, 1.0])
INK = np.array([0.043, 0.040, 0.036])

def canvas(c=INK):
    return np.ones((H, W, 3), np.float32) * np.array(c, np.float32)

def font(p, s): return ImageFont.truetype(p, s)

def text_mask(txt, fnt, xy, anchor='ls', spacing=0, tracking=0):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if tracking:
        x, y = xy
        if anchor[0] == 'm':
            tw = sum(d.textlength(ch, font=fnt) + tracking for ch in txt) - tracking; x -= tw / 2
        for ch in txt:
            d.text((x, y), ch, font=fnt, fill=255, anchor='l' + anchor[1]); x += d.textlength(ch, font=fnt) + tracking
    else:
        d.text(xy, txt, font=fnt, fill=255, anchor=anchor)
    return np.asarray(m, np.float32) / 255

def tlen(txt, fnt):
    return ImageDraw.Draw(Image.new('L', (1, 1))).textlength(txt, font=fnt)

def blur(m, s): return cv2.GaussianBlur(m, (0, 0), s)

def comp(img, mask, color, a=1.0):
    m = (mask * a)[..., None]
    return img * (1 - m) + np.array(color, np.float32) * m

def add(img, mask, color, a=1.0):
    return img + (mask * a)[..., None] * np.array(color, np.float32)

def glow_text(img, mask, color=WARM, glow=1.0, shadow=0.55):
    if shadow:
        sh = blur(np.roll(mask, 6, 0), 16); img = img * (1 - (sh * shadow)[..., None])
    img = add(img, blur(mask, 38), color * np.array([1, .86, .68]), .30 * glow)
    img = add(img, blur(mask, 10), color, .55 * glow)
    img = add(img, blur(mask, 2.5), color, .45 * glow)
    return comp(img, mask, color)

def caption(img, line, size=112):
    """locked Supercell serif-glow body caption, safe zone, centre x 478.5, baseline 1415"""
    f = font(SERIF, size)
    while tlen(line, f) > 797: size -= 4; f = font(SERIF, size)
    return glow_text(img, text_mask(line, f, (478.5, 1415), 'ms'), WARM, 0.85, 0.6)

def vgrad(top, bot, p=1.0):
    t = (np.linspace(0, 1, H) ** p)[:, None, None]
    return (np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t) * np.ones((H, W, 3), np.float32)

def blob(img, cx, cy, r, color, a):
    yy, xx = np.mgrid[0:H, 0:W]
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))).astype(np.float32)
    return add(img, g, color, a)

def vignette(img, k=0.55):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    return img * (1 - k * np.clip(d, 0, 1) ** 2.2)[..., None]

def halftone(img, cell=7.0, strength=0.38, angle=45):
    L = np.clip(img.mean(2), 0, 1)
    Ls = blur(L, cell * .45)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.deg2rad(angle)
    u = (xx * np.cos(a) + yy * np.sin(a)) / cell; v = (-xx * np.sin(a) + yy * np.cos(a)) / cell
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du * du + dv * dv)
    r = np.sqrt(Ls) * 0.62
    dots = np.clip((r - d) * cell * 1.2 + .5, 0, 1)
    tone = img / (Ls[..., None] + 1e-3)
    ht = np.clip(tone * dots[..., None], 0, 1.4) * np.clip(Ls[..., None] * 1.6, 0, 1)
    return img * (1 - strength) + ht * strength

def grain(img, a=0.025, seed=1):
    rng = np.random.default_rng(seed)
    n = blur(rng.standard_normal((H, W)).astype(np.float32), .7)
    return img + (n * a)[..., None]

def rect_mask(x0, y0, x1, y1, r=0, soft=0):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=255)
    a = np.asarray(m, np.float32) / 255
    return blur(a, soft) if soft else a

def line_mask(pts, w=2, dash=None):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if dash:
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            L = np.hypot(x1 - x0, y1 - y0); n = int(L / sum(dash))
            for k in range(n + 1):
                a = k * sum(dash) / L; b = min(1, a + dash[0] / L)
                if a < 1: d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=255, width=w)
    else:
        d.line(pts, fill=255, width=w, joint='curve')
    return np.asarray(m, np.float32) / 255

def box_mask(x0, y0, x1, y1, w=3, corner=None):
    """full box or corner brackets (corner = bracket length)"""
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if corner:
        c = corner
        for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(x, y + sy * c), (x, y), (x + sx * c, y)], fill=255, width=w)
    else:
        d.rectangle([x0, y0, x1, y1], outline=255, width=w)
    return np.asarray(m, np.float32) / 255

def paper(img, x0, y0, x1, y1, angle=0, color=(0.93, 0.91, 0.86), seed=3, shadow=0.6, content=None):
    """paper card with grain + drop shadow, rotated about its centre. content(card_img) draws on a local RGBA."""
    cw, ch = int(x1 - x0), int(y1 - y0)
    rng = np.random.default_rng(seed)
    card = np.ones((ch, cw, 3), np.float32) * np.array(color, np.float32)
    fib = blur(rng.standard_normal((ch, cw)).astype(np.float32), 1.2) * .03 + blur(rng.standard_normal((ch, cw)).astype(np.float32), 9) * .05
    card += fib[..., None]
    alpha = np.ones((ch, cw), np.float32)
    if content: card = content(card)
    M = cv2.getRotationMatrix2D((cw / 2, ch / 2), angle, 1.0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    M[0, 2] += cx - cw / 2; M[1, 2] += cy - ch / 2
    cr = cv2.warpAffine(card, M, (W, H), flags=cv2.INTER_CUBIC)
    al = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR)
    if shadow:
        sh = blur(np.roll(np.roll(al, 22, 0), 10, 1), 26)
        img = img * (1 - (sh * shadow)[..., None])
    return img * (1 - al[..., None]) + cr * al[..., None]

def local_text(card, txt, fnt, xy, color, anchor='ls', tracking=0):
    h, w = card.shape[:2]
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    if tracking:
        x, y = xy
        for ch_ in txt:
            d.text((x, y), ch_, font=fnt, fill=255, anchor='l' + anchor[1]); x += d.textlength(ch_, font=fnt) + tracking
    else:
        d.text(xy, txt, font=fnt, fill=255, anchor=anchor)
    a = (np.asarray(m, np.float32) / 255)[..., None]
    return card * (1 - a) + np.array(color, np.float32) * a

def save(img, path):
    out = np.clip(img, 0, 1) ** (1 / 1.0)
    cv2.imwrite(path, cv2.cvtColor((out * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))
