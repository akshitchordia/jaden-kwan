"""Assemble: edit v2 (zoomed talking head + opener + client file) + procedural B-rolls + locked flash-bloom captions."""
import json, re, math, sys, subprocess, difflib, glob, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
BASE = S + 'out/Mochary_edit_v2_wip.mp4'; OUTF = sys.argv[1]
W, H = 1080, 1920; FPS = 24000 / 1001
PLAN = [("because sam altman", "n"),
 ("once told reddit ceo", "S"), ("that one coach", "S"), ("would add a billion dollars", "S"), ("to his company", "S"), ("that coach is", "S"), ("matt mashari", "S"),
 ("he's worked with", "S"), ("altman brian armstrong", "S"), ("vlad tenev", "S"),
 ("and his whole playbook", "n"), ("is online", "n"), ("for anybody to read", "n"),
 ("his firm's coaching", "S"), ("starts at 10 grand", "S"), ("a month", "S"),
 ("so what are they", "n"), ("paying for", "n"), ("not the advice", "n"),
 ("every session", "n"), ("ends with you", "n"), ("writing down an action", "n"), ("and him going", "n"),
 ("i'll check in with you", "n"), ("at the end of the week", "n"), ("he does it", "n"), ("to himself too", "n"),
 ("he's literally hired", "n"), ("people to sit", "n"), ("on his couch", "n"), ("and read", "n"), ("while he does his admin", "n"),
 ("and honestly", "n"), ("the free playbook", "n"), ("is the smartest part", "n"), ("it's the marketing", "n"),
 ("it finds the people", "n"), ("who read it", "n"), ("but don't have the time", "n"), ("to implement it themselves", "n"),
 ("those are his buyers", "n"), ("yc is", "n"), ("similar in shape", "n"), ("tons of their advice", "n"), ("is free", "n"),
 ("but founders still", "S"), ("give up seven percent", "S"),
 ("for a demo day", "n"), ("deadline", "n"), ("and the batch", "n"), ("here's the catch", "n"),
 ("if your product", "n"), ("just does the job", "n"), ("nobody needs a check-in", "n"),
 ("but if it", "n"), ("only works", "n"), ("when people change", "n"), ("their behavior", "n"),
 ("like fitness", "n"), ("coaching", "n"), ("or rolling out", "n"), ("new software", "n"),
 ("then give the playbook", "n"), ("away for free", "n"), ("and charge for", "n"), ("the follow-through", "n")]
raw = json.load(open(S + 'moch/words.json'))
def norm(w): w = w.lower(); return re.sub(r"[^a-z0-9']", "", w)
pw = [(norm(w), t) for w, t in raw]
mine = [norm(w) for p, _ in PLAN for w in p.split()]
sm = difflib.SequenceMatcher(a=mine, b=[k for k, _ in pw], autojunk=False); tm = [None] * len(mine)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ("equal", "replace"):
        for d in range(i2 - i1): tm[i1 + d] = pw[min(j1 + d, j2 - 1)][1] if j2 > j1 else None
    if tag != "equal": print("ALIGN", tag, mine[i1:i2], [k for k, _ in pw[j1:j2]], file=sys.stderr)
for k in range(len(tm)):
    if tm[k] is None: tm[k] = tm[k - 1] + 0.2
C = []; idx = 0
for p, kind in PLAN:
    ws = p.split(); C.append(dict(words=ws, kind=kind, times=[max(0, tm[idx + j] - 0.05) for j in range(len(ws))])); idx += len(ws)
for k, c in enumerate(C):
    last = c["times"][-1]; nxt = C[k + 1]["times"][0] if k + 1 < len(C) else last + 1.2
    c["end"] = nxt if nxt - last < 1.25 else last + 0.85
    if k + 1 < len(C) and C[k + 1]["kind"] == "S": c["end"] = min(c["end"], C[k + 1]["times"][0])
C[0]["end"] = min(C[0]["end"], 1.16)
C = [c for c in C if c["kind"] == "n"]
FONT = S + "fd/newsreader-latin-500-normal.ttf"; SIZE = 82; TRACK = -0.028; F = ImageFont.truetype(FONT, SIZE)
BAND0 = 1080; BH = 560; YB = 1415
PROPER = {"sam": "Sam", "altman": "Altman", "i'll": "I'll", "yc": "YC"}
def clean(w): w = w.strip(".,;:?!"); return PROPER.get(w, w)
def layer_word(w, x, base):
    im = Image.new("L", (W, BH), 0); d = ImageDraw.Draw(im)
    for ch in w: d.text((x, base), ch, font=F, fill=255, anchor="ls"); x += F.getlength(ch) + TRACK * SIZE
    return np.asarray(im).astype(np.float32) / 255
def wl(w): return sum(F.getlength(c) for c in w) + TRACK * SIZE * (len(w) - 1)
def build_line(c):
    ws = [clean(w) for w in c["words"]]; sp = F.getlength(" ") * 0.92
    tot = sum(wl(w) for w in ws) + sp * (len(ws) - 1); x = (W - tot) / 2; out = []
    for w in ws: out.append(layer_word(w, x, YB - BAND0)); x += wl(w) + sp
    return out
cache = {}
def state(t):
    core = np.zeros((BH, W), np.float32); gin = np.zeros((BH, W), np.float32)
    k = next((k for k, c in enumerate(C) if c["times"][0] <= t < c["end"]), None)
    if k is None: return core, gin
    c = C[k]; fo = 1.0
    if c["end"] - t < 0.07: fo = max(0, (c["end"] - t) / 0.07)
    if k not in cache: cache.clear(); cache[k] = build_line(c)
    for L, ts in zip(cache[k], c["times"]):
        if t < ts: continue
        dt = t - ts; s = 6.0 * math.exp(-dt / 0.06); a = cv2.GaussianBlur(L, (0, 0), s) if s > 0.2 else L
        if s > 0.2: a = np.clip(a * (1 + s * 0.35), 0, 1)
        a = a * min(1, dt / 0.05) * fo; core = np.maximum(core, a); gin += a * (1.0 + 7.0 * math.exp(-dt / 0.085))
    return core, gin
def glow_of(a):
    small = cv2.resize(a, (W // 4, BH // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(a, (0, 0), 3) * 0.95 + cv2.GaussianBlur(a, (0, 0), 10) * 0.75
    for s_, wt in ((6, 0.5), (18, 0.28)): g += cv2.resize(cv2.GaussianBlur(small, (0, 0), s_), (W, BH)) * wt
    return g
GCOL = np.array([1.0, 0.98, 0.95], np.float32)
# ---- B-roll clips: out/broll/<name>_<firstframe>.mp4
clips = []
for p in sorted(glob.glob(S + 'out/broll/*_*.mp4')):
    n0 = int(os.path.basename(p)[:-4].split('_')[1])
    nf = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip())
    clips.append([n0, n0 + nf, p, None])
clips.sort(); print('clips', [(a, b, os.path.basename(p)) for a, b, p, _ in clips], flush=True)
def dec(path): return subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
base = dec(BASE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24000/1001", "-i", "-", "-i", BASE,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", OUTF], stdin=subprocess.PIPE)
SH = 0.5 / FPS; n = 0; FS = W * H * 3
while True:
    buf = base.stdout.read(FS)
    if len(buf) < FS: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); t = n / FPS
    for cl_ in clips:
        if cl_[0] <= n < cl_[1]:
            if cl_[3] is None: cl_[3] = dec(cl_[2])
            b2 = cl_[3].stdout.read(FS)
            if len(b2) == FS: fr = np.frombuffer(b2, np.uint8).reshape(H, W, 3).copy()
    core = np.zeros((BH, W), np.float32); gin = np.zeros((BH, W), np.float32)
    for j in range(4):
        c_, g_ = state(t + (j + 0.5) / 4 * SH - SH / 2); core += c_ / 4; gin += g_ / 4
    if gin.max() > 0.002:
        band = fr[BAND0:BAND0 + BH].astype(np.float32) / 255; lum = float(band.mean())
        if lum > 0.45:
            k_ = min(0.6, (lum - 0.45) * 2.2); halo = cv2.GaussianBlur(core, (0, 0), 22) * k_
            band = band * (1 - np.clip(halo, 0, 0.75)[..., None])
        g = glow_of(gin); band = 1 - (1 - band) * (1 - np.clip(g[..., None] * GCOL * 0.8, 0, 1))
        band = band * (1 - core[..., None]) + core[..., None]
        fr[BAND0:BAND0 + BH] = (np.clip(band, 0, 1) * 255 + 0.5).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
