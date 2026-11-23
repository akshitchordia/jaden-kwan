"""Fridge reel zoom v1: per-frame transforms with motion blur samples.
Frames at 23.976 fps, 1387 frames. Talking head from master 1728x3072,
archival (frames 289-516) from the Shawn Ryan Show screen recording."""
import json, math

FPS = 24000 / 1001
N = 1387

def lin(a, b):
    return lambda u: a + (b - a) * u

def snap(a, b):  # ease in-out cubic
    return lambda u: a + (b - a) * (4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2)

def smooth(a, b):  # ease in-out sine for the finale pull-out
    return lambda u: a + (b - a) * (1 - math.cos(math.pi * u)) / 2

# (start_frame, end_frame, curve, label). Boundaries at x.5 so the shutter never straddles a cut.
SEG = [
    # S1 hook: "Meta paid $14 billion ... camera in a fridge"
    (-0.5, 15, lin(1.10, 1.11), 'S1 settle'),
    (15, 21, snap(1.11, 1.35), 'SNAP $14 billion'),
    (21, 121.5, lin(1.35, 1.42), 'S1 push'),
    # S2 "At MIT ... It couldn't work."
    (121.5, 288.5, lin(1.00, 1.14), 'S2 slow push'),
    # ARCH "then that was like the lightbulb moment ... a million times more data"
    (288.5, 432, lin(1.00, 1.04), 'ARCH push'),
    (432, 438, snap(1.04, 1.16), 'SNAP a million times'),
    (438, 516.5, lin(1.16, 1.20), 'ARCH push'),
    # S3 "So he bought scaleapi.com ... human labor." pull out
    (516.5, 656.5, lin(1.38, 1.18), 'S3 pull-out'),
    # S4 "Random engineers ... biggest customer"
    (656.5, 788, lin(1.10, 1.20), 'S4 push'),
    (788, 794, snap(1.20, 1.45), 'SNAP biggest customer'),
    (794, 815.5, lin(1.45, 1.48), 'S4 hold'),
    # S5 "So Scale went all in ... with a laptop."
    (815.5, 967.5, lin(1.00, 1.12), 'S5a push'),
    # punch cut on "Launch broad" then pull out
    (967.5, 1067.5, lin(1.32, 1.22), 'S5b punch + pull-out'),
    # punch cut wide on "That's the formula"
    (1067.5, 1163.5, lin(1.05, 1.15), 'S5c push'),
    # S6 "And this July ... refill your fridge. This problem was ... Scale AI."
    (1163.5, 1295, lin(1.12, 1.24), 'S6 push'),
    (1295, 1301, snap(1.24, 1.50), 'SNAP fridge'),
    (1301, 1312, lin(1.50, 1.505), 'S6 hold'),
    (1312, 1386.5, smooth(1.505, 1.12), 'S6 finale pull-out'),
]

def z_at(t):
    for a, b, f, _ in SEG:
        if a <= t < b:
            return f((t - a) / (b - a))
    return SEG[-1][2](1.0)

def seg_of(t):
    for k, (a, b, _, _) in enumerate(SEG):
        if a <= t < b:
            return k
    return len(SEG) - 1

# shot anchors (face centres)
TH_W, TH_H = 1728, 3072
TH_FACE = {  # proxy medians x1.6
    0: (544, 829), 1: (536, 835), 2: (532, 845), 3: (529, 847), 4: (531, 850), 5: (513, 849)}
TH_SHOTS = [(0, 121), (122, 288), (517, 656), (657, 815), (816, 1163), (1164, 1386)]
ARCH = (289, 516)
AR_FACE = (1026, 388)
AR_C0 = (1026, 548.0)   # centre of the 9:16 crop inside the YouTube player area
AR_H = 956              # player picture height (y 70..1026)
AR_Y = (70, 1026)

def transform(i, z):
    """return [s, tx, ty]: out = s*p + t, output 1080x1920"""
    if ARCH[0] <= i <= ARCH[1]:
        s = 1920 / AR_H * z
        fx, fy = AR_FACE
        cx = AR_C0[0] + 0 * fx
        cy = fy + (AR_C0[1] - fy) / z
        hy = AR_H / 2 / z
        cy = min(max(cy, AR_Y[0] + hy), AR_Y[1] - hy)
        cx = fx + (AR_C0[0] - fx) / z
    else:
        k = next(n for n, (a, b) in enumerate(TH_SHOTS) if a <= i <= b)
        fx, fy = (v * 1.6 for v in TH_FACE[k])
        s = 1080 / TH_W * z
        cx = fx + (TH_W / 2 - fx) / z
        cy = fy + (TH_H / 2 - fy) / z
        hx, hy = TH_W / 2 / z, TH_H / 2 / z
        cx = min(max(cx, hx), TH_W - hx)
        cy = min(max(cy, hy), TH_H - hy)
    return [round(s, 6), round(540 - s * cx, 3), round(960 - s * cy, 3)]

def build():
    frames = []
    for i in range(N):
        k = seg_of(i)
        a, b = SEG[k][0], SEG[k][1]
        # 180-degree shutter, samples kept inside the segment
        t0, t1 = max(i - 0.25, a + 1e-6), min(i + 0.25, b - 1e-6)
        z0, z1 = z_at(t0), z_at(t1)
        disp = abs(z1 - z0) / ((z0 + z1) / 2) * 1100  # px at frame corner
        K = 1 if disp < 1.5 else min(24, int(math.ceil(disp / 1.5)))
        ts = [i] if K == 1 else [t0 + (t1 - t0) * (j + .5) / K for j in range(K)]
        frames.append([transform(i, z_at(t)) for t in ts])
    return frames

if __name__ == '__main__':
    fr = build()
    json.dump(fr, open('zoom_v1.json', 'w'))
    for a, b, f, lab in SEG:
        print(f'{max(a,0)/FPS:6.2f}-{b/FPS:6.2f}s  z {f(0):.2f}->{f(1):.2f}  {lab}')
    print('blur frames:', sum(len(x) > 1 for x in fr), 'max samples', max(len(x) for x in fr))
