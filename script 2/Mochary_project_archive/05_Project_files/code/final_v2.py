"""Akshit's B-roll edit -> halftone texture on untextured B-roll, big $10,000/month rolling counter, flash-bloom captions with key-word highlights."""
import sys, re, math, json, difflib, subprocess, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/moch')
from kit import halftone, text, font, glow_of as glow_full, SERIF, MONO, cl, eoc, eoq, W, H, FPS
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
SRC = '/mnt/user-data/uploads/Mochary_zoom_v1.mp4'; OUTF = sys.argv[1]
ONLY = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
SIM = np.load(S + 'ed/sim.npy'); SMALL = np.load(S + 'ed/small.npy')
OPENER = (25, 163)                                                    # already printed with halftone
def needs_texture(n):
    if OPENER[0] <= n <= OPENER[1]: return False
    if SMALL[n].mean() < 3: return False                              # black tail
    return SIM[n] < 0.9
# ---------------- captions
PLAN = [("sam altman once told", "n"),
 ("reddit's ceo that one coach would add a billion dollars to his company that coach is matt mashari", "S"),
 ("he's worked with", "n"), ("altman brian armstrong vlad tenev", "S"),
 ("and his whole playbook", "n"), ("is online", "n"), ("for anybody to read", "n"),
 ("his firm's coaching starts at 10 grand a month", "S"),
 ("so what are they", "n"), ("paying for", "n"), ("not the *advice", "n"),
 ("every session", "n"), ("ends with you", "n"), ("writing down an *action", "n"), ("and him going", "n"),
 ("i'll check in with you at the end of the week", "S"),
 ("he does it", "n"), ("to *himself too", "n"),
 ("he's literally hired", "n"), ("people to sit", "n"), ("on his couch", "n"), ("and read", "n"), ("while he does his admin", "n"),
 ("and honestly", "n"), ("the *free playbook", "n"), ("is the smartest part", "n"), ("it's the *marketing", "n"),
 ("it finds the people", "n"), ("who read it", "n"), ("but don't have the time", "n"), ("to implement it themselves", "n"),
 ("those are his *buyers", "n"),
 ("yc is similar in shape tons of their advice is free but founders still give up 7% for a demo day deadline and the batch", "S"),
 ("here's the *catch", "n"), ("if your product", "n"), ("just does the job", "n"), ("nobody needs a check in", "n"),
 ("but if it", "n"), ("only works", "n"), ("when people change", "n"), ("their *behavior", "n"),
 ("like fitness", "n"), ("coaching", "n"), ("or rolling out", "n"), ("new software", "n"),
 ("then give the playbook", "n"), ("away for *free", "n"), ("and charge for", "n"), ("the *follow-through", "n")]
raw = json.load(open(S + 'ed/words.json'))
def norm(w): return re.sub(r"[^a-z0-9']", "", w.lower())
pw = [(norm(w), t) for w, t in raw]
mine = [norm(w.lstrip('*')) for p, _ in PLAN for w in p.split()]
sm = difflib.SequenceMatcher(a=mine, b=[k for k, _ in pw], autojunk=False); tm = [None] * len(mine)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ("equal", "replace"):
        for d in range(i2 - i1): tm[i1 + d] = pw[min(j1 + d, j2 - 1)][1] if j2 > j1 else None
    if tag != "equal": print("ALIGN", tag, mine[i1:i2], [k for k, _ in pw[j1:j2]], file=sys.stderr)
for k in range(len(tm)):
    if tm[k] is None: tm[k] = tm[k - 1] + 0.16
C = []; idx = 0
for p, kind in PLAN:
    ws = p.split(); C.append(dict(words=[w.lstrip('*') for w in ws], hl=[w.startswith('*') for w in ws], kind=kind,
                                  times=[max(0, tm[idx + j] - 0.05) for j in range(len(ws))])); idx += len(ws)
for k, c in enumerate(C):
    last = c["times"][-1]; nxt = C[k + 1]["times"][0] if k + 1 < len(C) else last + 1.2
    c["end"] = nxt if nxt - last < 1.25 else last + 0.85
    if k + 1 < len(C) and C[k + 1]["kind"] == "S": c["end"] = min(c["end"], C[k + 1]["times"][0])
HARD = [(1.04, 6.84), (7.55, 10.59), (12.80, 15.30), (20.19, 22.27), (37.12, 45.09)]   # graphics already say it
for c in C:
    for a, b in HARD:
        if c["times"][0] < a < c["end"]: c["end"] = a
    if c["words"][:3] == ["so", "what", "are"]: c["times"] = [max(t, 15.36) for t in c["times"]]
C = [c for c in C if c["kind"] == "n"]
for c in C: print(f'{c["times"][0]:6.2f}-{c["end"]:6.2f}  ' + ' '.join(('*' if h else '') + w for w, h in zip(c["words"], c["hl"])), file=sys.stderr)
FONT = S + "fd/newsreader-latin-500-normal.ttf"; BASE_SIZE = 100; TRACK = -0.028; MAXW = 960
BAND0 = 1060; BH = 600; YB = 1430
PROPER = {"sam": "Sam", "altman": "Altman", "i'll": "I'll", "yc": "YC"}
def clean(w): w = w.strip(".,;:?!"); return PROPER.get(w, w)
def wl(w, F, sz): return sum(F.getlength(ch) for ch in w) + TRACK * sz * (len(w) - 1)
def build_line(c):
    ws = [clean(w) for w in c["words"]]; sz = BASE_SIZE
    while True:
        F = ImageFont.truetype(FONT, sz); sp = F.getlength(" ") * 0.92
        tot = sum(wl(w, F, sz) for w in ws) + sp * (len(ws) - 1)
        if tot <= MAXW or sz <= 70: break
        sz -= 4
    x = (W - tot) / 2; out = []
    for w in ws:
        im = Image.new("L", (W, BH), 0); d = ImageDraw.Draw(im); xx = x
        for ch in w: d.text((xx, YB - BAND0), ch, font=F, fill=255, anchor="ls"); xx += F.getlength(ch) + TRACK * sz
        out.append(np.asarray(im).astype(np.float32) / 255); x += wl(w, F, sz) + sp
    return out
cache = {}
def state(t):
    core = np.zeros((BH, W), np.float32); hl = np.zeros((BH, W), np.float32); gin = np.zeros((BH, W), np.float32); gh = np.zeros((BH, W), np.float32)
    k = next((k for k, c in enumerate(C) if c["times"][0] <= t < c["end"]), None)
    if k is None: return core, hl, gin, gh
    c = C[k]; fo = 1.0
    if c["end"] - t < 0.07: fo = max(0, (c["end"] - t) / 0.07)
    if k not in cache: cache.clear(); cache[k] = build_line(c)
    for L, ts, h in zip(cache[k], c["times"], c["hl"]):
        if t < ts: continue
        dt = t - ts; s = 6.0 * math.exp(-dt / 0.06); a = cv2.GaussianBlur(L, (0, 0), s) if s > 0.2 else L
        if s > 0.2: a = np.clip(a * (1 + s * 0.35), 0, 1)
        a = a * min(1, dt / 0.05) * fo
        if h: hl = np.maximum(hl, a); gh += a * (1.3 + 9.0 * math.exp(-dt / 0.10))
        else: core = np.maximum(core, a); gin += a * (1.0 + 7.0 * math.exp(-dt / 0.085))
    return core, hl, gin, gh
def glow_band(a):
    small = cv2.resize(a, (W // 4, BH // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, BH)) * wt
    return g
GCOL = np.array([1.0, 0.98, 0.95], np.float32); ORANGE = np.array([0.98, 0.50, 0.24], np.float32); OGLOW = np.array([1.0, 0.62, 0.36], np.float32)
# ---------------- $10,000 / month rolling counter (big)
CT0, CT_OUT = 12.98, 15.24
CHARS = '$10,000'; CSIZE = 262; LANDS = [14.38, 14.50, 14.60, 14.70, 14.80]; SPINS = [6, 8, 9, 10, 12]
_dig = {}
def dtile(dg):
    if dg not in _dig:
        f = font(SERIF, CSIZE); im = Image.new('L', (int(CSIZE * 0.72), int(CSIZE * 1.3)), 0)
        ImageDraw.Draw(im).text((im.width / 2, CSIZE * 1.02), str(dg), font=f, fill=255, anchor='ms'); _dig[dg] = np.asarray(im).astype(np.float32) / 255
    return _dig[dg]
def counter(T):
    core = np.zeros((H, W), np.float32); gin = np.zeros((H, W), np.float32); acc = np.zeros((H, W), np.float32)
    if T < CT0: return core, gin, acc, 0.0
    fo = 1 - cl((T - CT_OUT) / 0.08); f = font(SERIF, CSIZE); pitch = CSIZE * 1.04; base = 1000
    widths = [f.getlength(ch) * (1.0 if ch in '$,' else 1.0) for ch in CHARS]; x = (W - sum(widths)) / 2; di = 0
    a_in = cl((T - CT0) / 0.10)
    for ch, wd in zip(CHARS, widths):
        if ch in '$,':
            L = text(ch, SERIF, CSIZE, x, base, 'ls'); dt = T - CT0; s = 6 * math.exp(-dt / 0.06)
            a = np.clip(cv2.GaussianBlur(L, (0, 0), s) * (1 + s * 0.3), 0, 1) if s > 0.25 else L
            core = np.maximum(core, a * a_in * fo); gin += a * (0.9 + 6 * math.exp(-dt / 0.09)) * a_in * fo; x += wd; continue
        tl = LANDS[di]; tg = int(ch); rot = SPINS[di]; di += 1
        u = cl((T - CT0) / (tl - CT0)); p = tg + rot * 10 * (1 - eoc(u))
        u2 = cl((T + 1 / FPS - CT0) / (tl - CT0)); spd = abs(rot * 10 * (eoc(u2) - eoc(u)))
        th = int(CSIZE * 1.3); tw = int(CSIZE * 0.72); col = np.zeros((th, tw), np.float32)
        bd = math.floor(p); fr_ = p - bd
        for j, dd in enumerate((bd, bd + 1)):
            off = int(round((j - fr_) * pitch)) * -1 if False else int(round((fr_ - j) * pitch))
            tile = dtile(int(dd) % 10); ys, ye = max(0, off), min(th, th + off)
            if ye > ys: col[ys:ye] = np.maximum(col[ys:ye], tile[ys - off:ye - off])
        sig = min(48.0, spd * pitch * 0.45)
        if sig > 0.6: col = cv2.GaussianBlur(col, (0, 0), sigmaX=0.3, sigmaY=sig)
        yy = np.linspace(-1, 1, th)[:, None]; col *= np.clip((0.86 - np.abs(yy)) / 0.18, 0, 1)
        top = int(base - CSIZE * 1.02); xl = int(x + (wd - tw) / 2)
        y0, x0 = max(0, top), max(0, xl); y1, x1 = min(H, top + th), min(W, xl + tw)
        sub = col[y0 - top:y1 - top, x0 - xl:x1 - xl] * a_in * fo
        core[y0:y1, x0:x1] = np.maximum(core[y0:y1, x0:x1], sub)
        gin[y0:y1, x0:x1] += sub * (0.8 + 7 * math.exp(-max(0, T - tl) / 0.1) * (T >= tl) + 4 * math.exp(-(T - CT0) / 0.1))
        x += wd
    # "/ MONTH" types in on "a month"
    tm_ = 14.92
    if T >= tm_:
        txt = '/ MONTH'; n_ = int(cl((T - tm_) / 0.22) * len(txt) + 0.999)
        L = text(txt[:n_], MONO, 64, W / 2 - font(MONO, 64).getlength(txt) / 2 - 0.22 * 64 * 3, 1150, 'ls', 0.22)
        acc = np.maximum(acc, L * fo); gin += L * fo * 0.4
    dim = cl((T - CT0) / 0.15) * fo
    return core, gin, acc, dim
def apply_counter(f, T):
    core, gin, acc, dim = counter(T)
    if dim <= 0 and gin.max() < 0.002: return f
    f = f * (1 - 0.62 * dim)                                           # sink the footage so the number owns the frame
    g = glow_full(gin); f = 1 - (1 - f) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
    ga = glow_full(acc)[..., None] * OGLOW * 0.7; f = 1 - (1 - f) * (1 - np.clip(ga, 0, 1))
    f = f * (1 - core[..., None]) + core[..., None] * np.array([1.0, 0.965, 0.915], np.float32)
    f = f * (1 - acc[..., None]) + acc[..., None] * ORANGE
    return f
# ---------------- main loop
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
if ONLY is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24000/1001", "-i", "-", "-i", SRC,
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", OUTF], stdin=subprocess.PIPE)
SH = 0.5 / FPS; n = 0; FS = W * H * 3; tiles = []
while True:
    buf = dec.stdout.read(FS)
    if len(buf) < FS: break
    if ONLY is not None and n not in ONLY: n += 1; continue
    t = n / FPS; f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    if CT0 <= t < CT_OUT + 0.1: f = apply_counter(f, t)
    if needs_texture(n): f = halftone(f, n)
    core = np.zeros((BH, W), np.float32); hl = np.zeros((BH, W), np.float32); gin = np.zeros((BH, W), np.float32); gh = np.zeros((BH, W), np.float32)
    for j in range(4):
        c_, h_, g_, gh_ = state(t + (j + 0.5) / 4 * SH - SH / 2); core += c_ / 4; hl += h_ / 4; gin += g_ / 4; gh += gh_ / 4
    if gin.max() + gh.max() > 0.002:
        band = f[BAND0:BAND0 + BH]; lum = float(band.mean())
        if lum > 0.40:
            k_ = min(0.65, (lum - 0.40) * 2.2); halo = cv2.GaussianBlur(core + hl, (0, 0), 22) * k_
            band = band * (1 - np.clip(halo, 0, 0.75)[..., None])
        g = glow_band(gin); band = 1 - (1 - band) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
        go = glow_band(gh); band = 1 - (1 - band) * (1 - np.clip(go[..., None] * OGLOW * 0.75, 0, 1))
        band = band * (1 - core[..., None]) + core[..., None]
        band = band * (1 - hl[..., None]) + hl[..., None] * ORANGE
        f = f.copy(); f[BAND0:BAND0 + BH] = band
    out = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
    if ONLY is not None: tiles.append(cv2.resize(out, (300, 533), interpolation=cv2.INTER_AREA))
    else: enc.stdin.write(out.tobytes())
    n += 1
if ONLY is not None: cv2.imwrite(OUTF, cv2.cvtColor(np.hstack(tiles), cv2.COLOR_RGB2BGR))
else: enc.stdin.close(); enc.wait()
print("frames", n)
