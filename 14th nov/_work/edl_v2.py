"""Fridge v2: tightened edit + J-cut out of the archival + every cut treated with a zoom.
Outputs tl_v2.json (per timeline frame: source, source frame/time, transform samples)
and audio_v2.json (audio edit list)."""
import json, math
from zoomplan import transform as tf_v1, TH_SHOTS, TH_FACE, TH_W, TH_H, AR_FACE, AR_C0, AR_H, AR_Y

FPS = 24000 / 1001
fr = lambda t: int(round(t * FPS))

# ---- edit: talking-head pauses to shrink (silence start, end, target gap) ----
GAPS = [(4.83, 5.33, .20), (10.39, 11.15, .20), (25.43, 25.86, .25), (27.15, 27.71, .20),
        (33.76, 34.29, .20), (39.68, 40.49, .22), (44.08, 44.46, .22), (48.31, 48.80, .20),
        (54.46, 54.87, .22)]
cuts = [(fr(s + g / 2), fr(e - g / 2)) for s, e, g in GAPS]

J = 10  # J-cut: frames of Wang picture under Akshit's first words
AR1 = (23.80, 28.34)   # "then that was like the lightbulb moment ... I need like"
AR2 = (29.84, 32.66)   # "a million times more data than I have now."
RC_RESUME = 515        # src frame where Akshit's audio resumes ("So he bought" at 21.55 s)

# clips: (kind, src_in, src_out) in frames for rc, seconds for ar
clips = []
c = 0
rc_pieces = [(0, cuts[0][0]), (cuts[0][1], cuts[1][0]), (cuts[1][1], fr(11.94))]
for p in rc_pieces:
    clips.append(['rc', *p])
clips.append(['ar', AR1[0], AR1[0] + round((AR1[1] - AR1[0]) * FPS) / FPS])
n2 = round((AR2[1] - AR2[0]) * FPS)
clips.append(['ar', AR2[0], AR2[0] + n2 / FPS])
rest = [RC_RESUME] + [x for ab in cuts[2:] for x in ab] + [1387]
for a, b in zip(rest[::2], rest[1::2]):
    clips.append(['rc', a, b])

# ---- build timeline ----
tl = []          # per frame: [kind, src, clip_index]
audio = []       # [kind, src_t0, src_t1, tl_t0]
for ci, (k, a, b) in enumerate(clips):
    t0 = len(tl) / FPS
    if k == 'rc':
        for f in range(a, b):
            tl.append(['rc', f, ci])
        audio.append(['rc', a / FPS, b / FPS, t0])
    else:
        n = round((b - a) * FPS)
        for j in range(n):
            tl.append(['ar', a + j / FPS, ci])
        audio.append(['ar', a, b, t0])
# J-cut: first J frames of the clip after the archival show Wang's picture (continuing), audio stays Akshit
jc = next(i for i, x in enumerate(tl) if x[2] == 5)
ar_end = clips[4][2]
for j in range(J):
    tl[jc + j] = ['ar', ar_end + j / FPS, 4]
N = len(tl)

def tl_of_src(src_t):
    f = fr(src_t)
    return next(i for i, x in enumerate(tl) if x[0] == 'rc' and x[1] >= f)

# clip boundaries on the timeline (first frame of each clip's picture)
starts = {}
for i, x in enumerate(tl):
    starts.setdefault(x[2], i)
B = [starts[i] for i in range(len(clips))]
B[5] = jc + J  # face picture starts after the J-cut
print('clips', len(clips), 'frames', N, f'{N / FPS:.2f}s')
for i, cl in enumerate(clips):
    print(i, cl[0], cl[1] if cl[0] == 'ar' else f'{cl[1]}({cl[1]/FPS:.2f}s)', cl[2] if cl[0] == 'ar' else f'{cl[2]}({cl[2]/FPS:.2f}s)', 'tl', B[i], f'{B[i]/FPS:.2f}s')

# ---- zoom plan v2 on the timeline ----
def lin(a, b): return lambda u: a + (b - a) * u
def ease(a, b): return lambda u: a + (b - a) * (4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2)
W = 4  # whip half-width in frames

def sgm(a, b, f, lab): return (a, b, f, lab)
b_ = B
fb = tl_of_src(32.84)       # "the biggest"
ff = tl_of_src(53.97)       # "your fridge"
# junction plan: whip = blurred zoom across the cut, punch = hard scale change
SEG = [
    sgm(-.5, 15, lin(1.10, 1.11), 'hook settle'),
    sgm(15, 21, ease(1.11, 1.35), 'SNAP $14 billion'),
    sgm(21, b_[1] - W, lin(1.35, 1.40), 'hook push'),
    sgm(b_[1] - W, b_[1] + W, ease(1.40, 1.00), 'WHIP-OUT into "At MIT"'),
    sgm(b_[1] + W, b_[2] - W, lin(1.00, 1.10), 'push "At MIT ... catch them"'),
    sgm(b_[2] - W, b_[2] + W, ease(1.10, 1.32), 'WHIP-IN into "It couldn\'t work"'),
    sgm(b_[2] + W, b_[3] - .5, lin(1.32, 1.36), 'hold "It couldn\'t work"'),
    sgm(b_[3] - .5, b_[4] - W, lin(1.00, 1.05), 'ARCH push "lightbulb moment"'),
    sgm(b_[4] - W, b_[4] + W, ease(1.05, 1.18), 'WHIP-IN through Wang cut "a million times"'),
    sgm(b_[4] + W, b_[5] - .5, lin(1.18, 1.23), 'ARCH push + J-cut tail'),
    sgm(b_[5] - .5, b_[6] - .5, lin(1.38, 1.20), 'pull-out "So he bought scaleapi.com ... a week later"'),
    sgm(b_[6] - .5, b_[7] - W, lin(1.42, 1.45), 'PUNCH-IN "an API for human labor"'),
    sgm(b_[7] - W, b_[7] + W, ease(1.45, 1.00), 'WHIP-OUT into "Random engineers"'),
    sgm(b_[7] + W, fb, lin(1.00, 1.12), 'push "Random engineers ... became the"'),
    sgm(fb, fb + 6, ease(1.12, 1.45), 'SNAP biggest customer'),
    sgm(fb + 6, b_[8] - .5, lin(1.45, 1.48), 'hold'),
    sgm(b_[8] - .5, b_[9] - W, lin(1.00, 1.12), 'PUNCH-OUT "So Scale went all in ... laptop"'),
    sgm(b_[9] - W, b_[9] + W, ease(1.12, 1.32), 'WHIP-IN into "Launch broad"'),
    sgm(b_[9] + W, b_[10] - .5, lin(1.32, 1.22), 'pull-out "Launch broad ... small"'),
    sgm(b_[10] - .5, b_[11] - W, lin(1.02, 1.14), 'PUNCH-OUT "That\'s the formula ... budgets"'),
    sgm(b_[11] - W, b_[11] + W, ease(1.14, 1.36), 'WHIP-IN into "And this July"'),
    sgm(b_[11] + W, ff, lin(1.36, 1.22), 'pull-out "now running AI at Meta ... refill your"'),
    sgm(ff, ff + 6, ease(1.22, 1.52), 'SNAP fridge'),
    sgm(ff + 6, b_[12] - W, lin(1.52, 1.53), 'hold'),
    sgm(b_[12] - W, b_[12] + W, ease(1.53, 1.12), 'WHIP-OUT into "This problem"'),
    sgm(b_[12] + W, N - .5, lin(1.12, 1.24), 'slow push to the end'),
]
for a, b, f, lab in SEG:
    assert b > a, lab

def z_at(t):
    for a, b, f, _ in SEG:
        if a <= t < b: return f((t - a) / (b - a))
    return SEG[-1][2](1.0)
def seg_of(t):
    for k, (a, b, _, _) in enumerate(SEG):
        if a <= t < b: return k
    return len(SEG) - 1

def transform(i, z):
    k, src, _ = tl[i]
    if k == 'ar':
        s = 1920 / AR_H * z
        fx, fy = AR_FACE
        cx = fx + (AR_C0[0] - fx) / z
        cy = fy + (AR_C0[1] - fy) / z
        hy = AR_H / 2 / z
        cy = min(max(cy, AR_Y[0] + hy), AR_Y[1] - hy)
    else:
        sh = next(n for n, (a, b) in enumerate(TH_SHOTS) if a <= src <= b) if src >= 517 or src <= 288 else 2
        fx, fy = (v * 1.6 for v in TH_FACE[sh])
        s = 1080 / TH_W * z
        cx = fx + (TH_W / 2 - fx) / z; cy = fy + (TH_H / 2 - fy) / z
        hx, hy = TH_W / 2 / z, TH_H / 2 / z
        cx = min(max(cx, hx), TH_W - hx); cy = min(max(cy, hy), TH_H - hy)
    return [round(s, 6), round(540 - s * cx, 3), round(960 - s * cy, 3)]

# whips straddle cuts: blur samples may cross the cut (source stays the frame's own), that is intended
whips = {k for k, sg in enumerate(SEG) if sg[3].startswith('WHIP')}
out = []
for i in range(N):
    k = seg_of(i); a, b = SEG[k][0], SEG[k][1]
    if k in whips:
        t0, t1 = i - .35, i + .35          # longer shutter on whips for more blur
    else:
        t0, t1 = max(i - .25, a + 1e-6), min(i + .25, b - 1e-6)
    z0, z1 = z_at(t0), z_at(t1)
    disp = abs(z1 - z0) / ((z0 + z1) / 2) * 1100
    K = 1 if disp < 1.5 else min(24, int(math.ceil(disp / 1.5)))
    ts = [i] if K == 1 else [t0 + (t1 - t0) * (j + .5) / K for j in range(K)]
    out.append({'k': tl[i][0], 'src': tl[i][1], 'T': [transform(i, z_at(t)) for t in ts]})

json.dump(out, open('tl_v2.json', 'w'))
json.dump(audio, open('audio_v2.json', 'w'))
print('blur frames', sum(len(x['T']) > 1 for x in out))
for a, b, f, lab in SEG:
    print(f'{max(a,0)/FPS:6.2f}-{b/FPS:6.2f}s  z {f(0):.2f}->{f(1):.2f}  {lab}')
print('audio', audio)
