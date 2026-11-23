"""'I'll check in with you at the end of the week' — full-screen calendar B-roll (dark-mode month view, hop to Friday, check-in lands)."""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
W, H = 1080, 1920; FPS = 24000 / 1001; K = 2                          # draw at 2x, warp down
T0, T1 = 22.18, 24.30
N0, N1 = 533, 583
def F(p, s): return ImageFont.truetype(S + 'fd/' + p, int(s * K))
FI6, FI5, FN, FM = 'inter-600.ttf', 'inter-500.ttf', 'newsreader-600.ttf', 'plexmono-500.ttf'
def cl(x): return min(1.0, max(0.0, x))
def eoq(x): x = cl(x); return 1 - (1 - x) ** 5
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eic(x): x = cl(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x, s=1.6): x = cl(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
ORANGE = (250, 120, 51); PAPER = (255, 246, 233)
# ---- layout (1x coordinates)
GX0, GX1 = 36, 1044; COLW = (GX1 - GX0) / 7; GAP = 10
GY0, ROWH = 606, 256
DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
# October 2026 starts on a Thursday
CELLS = []
for r in range(5):
    for c in range(7):
        k = r * 7 + c - 3 + 1
        if k < 1: num, inm = 30 + k - 1 + 1 - 1 + 0, False; num = [28, 29, 30][c]
        elif k > 31: num, inm = k - 31, False
        else: num, inm = k, True
        CELLS.append(dict(r=r, c=c, num=num, inm=inm))
EVENTS = {5: [('Standup', 0)], 7: [('1:1 · Priya', 0)], 9: [('Board prep', 0), ('Gym', 1)], 12: [('Ship v2', 0)], 14: [('Review', 0)],
          15: [('Investor call', 0)], 19: [('Standup', 0)], 20: [('Hiring loop', 0), ('Gym', 1)], 22: [('Roadmap', 0)],
          23: [('1:1 · Sam', 0)], 26: [('Offsite', 0)], 28: [('Standup', 0)], 30: [('Demo', 0)], 33: [('Retro', 0)]}
WEEK_ROW = 3; FRI = WEEK_ROW * 7 + 4
HOPS = [22.52, 22.74, 22.95, 23.16, 23.38]                            # pill lands Mon..Fri
T_FRI = 23.40; T_CHIP = 23.47; T_RING = 23.52
def cell_rect(i, s=1.0):
    c = CELLS[i]; x0 = GX0 + c['c'] * COLW + GAP / 2; y0 = GY0 + c['r'] * ROWH + GAP / 2
    w, h = COLW - GAP, ROWH - GAP; cx, cy = x0 + w / 2, y0 + h / 2
    return (cx - w * s / 2, cy - h * s / 2, cx + w * s / 2, cy + h * s / 2)
def R(b): return [v * K for v in b]

def scene(t):
    im = Image.new('RGBA', (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    gl = Image.new('L', (W * K, H * K), 0); g = ImageDraw.Draw(gl)
    # header
    a = eoq((t - T0) / 0.3)
    d.text((56 * K, 360 * K), 'October', font=F(FN, 176), fill=PAPER + (int(255 * a),), anchor='ls')
    d.text((1024 * K, 352 * K), '2026', font=F(FM, 40), fill=(200, 190, 178, int(200 * a)), anchor='rs')
    d.text((60 * K, 428 * K), 'WEEK 43  ·  5 EVENTS', font=F(FM, 26), fill=(160, 150, 140, int(200 * eoq((t - T0 - 0.1) / 0.3))), anchor='ls')
    for c, dn in enumerate(DAYS):
        x = GX0 + (c + 0.5) * COLW; aa = eoq((t - T0 - 0.05 - c * 0.02) / 0.25)
        col = ORANGE if (c == 4 and t > T_FRI) else (215, 205, 192)
        d.text((x * K, 580 * K), dn, font=F(FI6, 24), fill=col + (int(230 * aa),), anchor='ms')
    # week band
    wb = eoq((t - HOPS[0] + 0.1) / 0.3)
    if wb > 0:
        y0 = GY0 + WEEK_ROW * ROWH; d.rounded_rectangle(R((GX0 - 6, y0 - 2, GX1 + 6, y0 + ROWH + 2)), radius=28 * K, fill=(255, 240, 220, int(14 * wb)))
    # cells
    for i, c in enumerate(CELLS):
        ti = T0 + 0.02 + (c['r'] * 7 + c['c']) * 0.007; p = eoq((t - ti) / 0.32)
        if p <= 0: continue
        s = 0.9 + 0.1 * p; b = cell_rect(i, s); A = p
        past = c['r'] == WEEK_ROW and c['c'] < 4 and t > HOPS[c['c'] + 1] - 0.02
        fri = i == FRI and t >= T_FRI
        base = 22 if c['inm'] else 14
        if c['r'] == WEEK_ROW: base += 6
        if past: base -= 6
        fill = (base + 4, base + 2, base, int(255 * A))
        d.rounded_rectangle(R(b), radius=22 * K, fill=fill, outline=(255, 245, 230, int(18 * A)), width=K)
        # date number (today = Monday 19 gets the white dot until the pill leaves)
        nx, ny = b[0] + 18, b[1] + 50
        ncol = (235, 228, 218) if c['inm'] else (95, 90, 85)
        if past: ncol = (110, 104, 98)
        if i == WEEK_ROW * 7 and t < HOPS[1]:
            d.ellipse(R((nx - 10, ny - 40, nx + 46, ny + 14)), fill=(245, 238, 228, int(255 * A))); ncol = (18, 16, 14)
        if fri:
            fa = eoq((t - T_FRI) / 0.12)
            d.rounded_rectangle(R(b), radius=22 * K, fill=(int(lerp3(base + 4, 70, fa)), int(lerp3(base + 2, 34, fa)), int(lerp3(base, 18, fa)), 255),
                                outline=ORANGE + (int(255 * fa),), width=2 * K)
            ncol = ORANGE; g.text((nx * K, ny * K), str(c['num']), font=F(FI6, 44), fill=int(255 * (0.5 + 2.5 * math.exp(-(t - T_FRI) / 0.12))), anchor='ls')
        d.text((nx * K, ny * K), str(c['num']), font=F(FI6, 44), fill=ncol + (int(255 * A),), anchor='ls')
        if past:                                                       # done: small tick in the corner
            u = eoc((t - HOPS[c['c'] + 1] + 0.02) / 0.18); cx, cy = b[2] - 34, b[1] + 34
            pts = [(cx - 11, cy), (cx - 3, cy + 8), (cx + 12, cy - 9)]
            seg = pts[:2] if u < 0.4 else pts
            if u < 0.4: seg = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * u / 0.4, pts[0][1] + (pts[1][1] - pts[0][1]) * u / 0.4)]
            elif u < 1: f = (u - 0.4) / 0.6; seg = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * f, pts[1][1] + (pts[2][1] - pts[1][1]) * f)]
            d.line([(x * K, y * K) for x, y in seg], fill=(150, 142, 132, 255), width=3 * K, joint='curve')
        # existing events: grey chips
        for j, (ev, slot) in enumerate(EVENTS.get(i, [])):
            ea = eoq((t - ti - 0.12 - j * 0.04) / 0.3) * (0.55 if past else 1.0)
            if ea <= 0: continue
            ey = b[1] + 78 + slot * 46
            d.rounded_rectangle(R((b[0] + 10, ey, b[2] - 10, ey + 38)), radius=9 * K, fill=(56, 52, 48, int(255 * ea)))
            d.rectangle(R((b[0] + 10, ey + 6, b[0] + 14, ey + 32)), fill=(140, 132, 122, int(255 * ea)))
            txt = ev; f = F(FI5, 19)
            while f.getlength(txt) > (b[2] - b[0] - 40) * K and len(txt) > 3: txt = txt[:-2] + '…'
            d.text(((b[0] + 22) * K, (ey + 26) * K), txt, font=f, fill=(205, 196, 184, int(255 * ea)), anchor='ls')
    # Friday check-in chip
    if t >= T_CHIP:
        b = cell_rect(FRI); u = back((t - T_CHIP) / 0.32); ey = b[1] + 78 + (1 - u) * 40; ca = eoq((t - T_CHIP) / 0.15)
        box = (b[0] + 10, ey, b[2] - 10, ey + 92)
        d.rounded_rectangle(R(box), radius=12 * K, fill=ORANGE + (int(255 * ca),))
        d.text(((b[0] + 22) * K, (ey + 36) * K), 'Check-in', font=F(FI6, 23), fill=(28, 16, 8, int(255 * ca)), anchor='ls')
        d.text(((b[0] + 22) * K, (ey + 70) * K), '4:00 PM', font=F(FI5, 19), fill=(60, 30, 12, int(255 * ca)), anchor='ls')
        g.rounded_rectangle(R(box), radius=12 * K, fill=int(255 * min(1, 0.35 + 1.6 * math.exp(-(t - T_CHIP) / 0.14)) * ca))
    # hopping selection pill
    if HOPS[0] - 0.12 <= t:
        k = max(i for i in range(5) if t >= HOPS[i] - 0.18) if t >= HOPS[0] - 0.18 else 0
        if t < HOPS[0]: u = 1.0; ca, cb = 0, 0; app = eoq((t - HOPS[0] + 0.12) / 0.12)
        else:
            app = 1.0; nk = min(4, k)
            prev = max(0, nk - 1) if t < HOPS[nk] else nk
            u = eic((t - (HOPS[nk] - 0.18)) / 0.18) if t < HOPS[nk] else 1.0
            ca, cb = prev, nk
        if t < HOPS[0]: ca = cb = 0
        ra, rb = cell_rect(WEEK_ROW * 7 + ca), cell_rect(WEEK_ROW * 7 + cb)
        rc = [ra[j] + (rb[j] - ra[j]) * u for j in range(4)]
        stretch = math.sin(math.pi * u) * 18 if ca != cb else 0
        rc = (rc[0] - stretch / 2 - 4, rc[1] - 4, rc[2] + stretch / 2 + 4, rc[3] + 4)
        col = ORANGE if t >= T_FRI else (250, 244, 235)
        d.rounded_rectangle(R(rc), radius=26 * K, outline=col + (int(255 * app),), width=3 * K)
        g.rounded_rectangle(R(rc), radius=26 * K, outline=int(255 * app * (0.8 + (1.5 * math.exp(-(t - T_FRI) / 0.15) if t >= T_FRI else 0))), width=5 * K)
    # marker ring around Friday
    pr = eoc((t - T_RING) / 0.42)
    if pr > 0:
        b = cell_rect(FRI); cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; rx, ry = (b[2] - b[0]) / 2 + 26, (b[3] - b[1]) / 2 + 14
        pts = []
        for s in np.linspace(0, 1.1 * pr, max(2, int(140 * pr))):
            an = -2.4 + s * 2 * math.pi; wob = 1 + 0.04 * math.sin(s * 11) + 0.05 * s
            pts.append(((cx + rx * wob * math.cos(an)) * K, (cy + ry * wob * math.sin(an)) * K))
        d.line(pts, fill=ORANGE + (255,), width=6 * K, joint='curve'); g.line(pts, fill=200, width=8 * K)
    return im, gl
def lerp3(a, b, u): return a + (b - a) * u

# ---- camera: settle in, then push into Friday
FB = cell_rect(FRI); FC = ((FB[0] + FB[2]) / 2, (FB[1] + FB[3]) / 2)
def cam(t):
    u0 = eoq((t - T0) / 0.5); z = 1.06 - 0.06 * u0; cx, cy = 540, 960
    u = eic((t - 23.30) / 0.85); z = z * (1 + 1.15 * u)
    fx = 540 + (FC[0] - 540) * u; fy = 1020 + (FC[1] - 1020) * u
    return z, fx, fy
def warp(arr, z, fx, fy, interp=cv2.INTER_AREA):
    s = z / K; M = np.float32([[s, 0, 540 - fx * z], [0, s, 960 - fy * z]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR if z > 1.3 else interp, borderValue=0)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BG = (np.array([15, 14, 13], np.float32) / 255)[None, None] * (1 + 0.35 * np.exp(-(((xx - 540) / 700) ** 2 + ((yy - 760) / 900) ** 2)))[..., None]
VIG = np.clip(1 - 0.22 * (((xx - 540) / 1080) ** 2 + ((yy - 960) / 1920) ** 2) * 3, 0, 1)[..., None]
rng = np.random.default_rng(3); GR = [rng.normal(0, 0.016, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def glow(a):
    sm = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    gg = cv2.GaussianBlur(a, (0, 0), 4) * 0.8 + cv2.GaussianBlur(a, (0, 0), 12) * 0.6
    for s_, wt in ((8, 0.5), (22, 0.3)): gg += cv2.resize(cv2.GaussianBlur(sm, (0, 0), s_), (W, H)) * wt
    return gg
def render(n):
    t = n / FPS; im, gl = scene(t)
    rgba = np.asarray(im).astype(np.float32) / 255; rgba[..., :3] *= rgba[..., 3:4]; gla = np.asarray(gl).astype(np.float32) / 255
    acc = np.zeros((H, W, 4), np.float32); gacc = np.zeros((H, W), np.float32); SUB = 3
    for j in range(SUB):                                               # motion blur on the camera move
        tt = t + (j - (SUB - 1) / 2) / SUB * 0.5 / FPS; z, fx, fy = cam(tt)
        acc += warp(rgba, z, fx, fy) / SUB; gacc += warp(gla, z, fx, fy) / SUB
    z, fx, fy = cam(t)
    # depth: everything but Friday softens as we push in
    u = eic((t - 23.30) / 0.85)
    if u > 0.02:
        bl = cv2.GaussianBlur(acc, (0, 0), 6 * u)
        b = FB; sx0, sy0 = 540 + (b[0] - fx) * z, 960 + (b[1] - fy) * z; sx1, sy1 = 540 + (b[2] - fx) * z, 960 + (b[3] - fy) * z
        m = np.zeros((H, W), np.float32); cv2.rectangle(m, (int(sx0 - 60 * z), int(sy0 - 50 * z)), (int(sx1 + 60 * z), int(sy1 + 50 * z)), 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), 40)[..., None]; acc = acc * m + bl * (1 - m)
    a = acc[..., 3:4]; col = acc[..., :3]
    img = BG * (1 - a) + col                                            # premultiplied-ish over dark bg
    gg = glow(gacc)[..., None]
    gcol = np.where(t >= T_FRI, 1.0, 0.0)
    tint = np.array([1.0, 0.62, 0.36], np.float32) * gcol + np.array([1.0, 0.97, 0.92], np.float32) * (1 - gcol)
    img = 1 - (1 - img) * (1 - np.clip(gg * tint * 0.55, 0, 1))
    img = img * VIG * (1 + 0.5 * math.exp(-(t - T0) / 0.05))
    gr = cv2.resize(GR[(n // 2) % 6], (W, H)); img = img + gr[..., None] * (0.6 + 0.4 * img)
    return np.clip(img, 0, 1)

if __name__ == '__main__':
    out = sys.argv[1]
    if out.endswith('.jpg'):
        fs = [int(x) for x in sys.argv[2].split(',')]
        tiles = [cv2.resize((render(f) * 255).astype(np.uint8), (360, 640), interpolation=cv2.INTER_AREA) for f in fs]
        cv2.imwrite(out, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR)); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for n in range(N0, N1): enc.stdin.write((render(n) * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print('done', N0, N1)
