"""Mochary reel: zoom choreography render (same system as TBH zoom.py).
Source: 1728x3072 ProRes master (via two H.264 CRF14 proxies), output 1080x1920 @ 23.976."""
import sys, math, json, subprocess, numpy as np, cv2, soundfile as sf
P = "/mnt/user-data/uploads/script 2/_proxy/"
AUD = P + "mochary_audio.wav"
FPS = 24000 / 1001; SW, SH = 1728, 3072; W, H = 1080, 1920
FACE = (820.0, 1000.0)                      # face centre in source px; stays fixed on screen
NFR = 1489
def eio(x): x = min(1, max(0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)
def eic(x): x = min(1, max(0, x)); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def eoc(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

# --- snap each cut into the quietest moment of the pause before the phrase, on a frame boundary
a, sr = sf.read(AUD); a = a.mean(1) if a.ndim > 1 else a
w = int(0.02 * sr); env = np.array([np.sqrt(np.mean(a[i:i + w] ** 2)) for i in range(0, len(a) - w, w)])
def cut_before(onset, lo):
    i0, i1 = int(lo / 0.02), int((onset - 0.03) / 0.02)
    if i1 <= i0: t = onset - 0.06
    else: t = (i0 + int(np.argmin(env[i0:i1]))) * 0.02 + 0.01
    return round(t * FPS) / FPS
def f(n): return n / FPS                    # exact source jump-cut frames
C = lambda onset, prev: cut_before(onset, prev + 0.22)

# (cut_time, start_zoom, events)  push=(t_end,z)  ease/snap=(t_start,dur,z)
SHOTS = [
 (0.00,                1.15, [("push", 3.86, 1.19), ("snap", 3.86, 0.28, 1.32), ("push", C(5.76, 4.88), 1.34)]),          # hook / "a billion dollars"
 (C(5.76, 4.88),       1.00, [("push", 6.51, 1.02), ("ease", 6.51, 0.40, 1.12), ("push", C(7.68, 6.80), 1.13)]),          # "That coach is | Matt Mochary"
 (C(7.68, 6.80),       1.18, [("push", 10.91, 1.22)]),                                                                       # the names
 (10.91,               1.22, [("ease", 10.91, 0.60, 1.00), ("push", C(13.84, 13.20), 1.04)]),                              # "his whole playbook is online" (reveal)
 (C(13.84, 13.20),     1.14, [("push", 15.47, 1.17), ("snap", 15.47, 0.25, 1.30), ("push", C(16.56, 16.16), 1.31)]),       # "10 grand a month"
 (C(16.56, 16.16),     1.05, [("push", C(18.00, 17.52), 1.08)]),                                                             # "So what are they paying for?"
 (C(18.00, 17.52),     1.28, [("push", C(19.28, 18.40), 1.30)]),                                                             # "Not the advice." (punch)
 (C(19.28, 18.40),     1.00, [("push", C(22.32, 21.76), 1.05)]),                                                             # "Every session ends..."
 (C(22.32, 21.76),     1.18, [("push", C(24.32, 23.76), 1.21)]),                                                             # "I'll check in with you..."
 (C(24.32, 23.76),     1.08, [("push", f(718), 1.20)]),                                                                      # "He does it to himself too... couch" (slow build)
 (f(718),              1.00, [("push", 32.29, 1.03), ("ease", 32.29, 0.40, 1.15), ("push", 33.49, 1.16),                    # "the free playbook is | the smartest part"
                              ("snap", 33.49, 0.25, 1.34), ("push", C(34.50, 33.70), 1.35)]),                               # "It's | the marketing."
 (C(34.50, 33.70),     1.05, [("push", C(38.64, 37.78), 1.10)]),                                                             # "It finds the people who..."
 (C(38.64, 37.78),     1.22, [("push", C(39.92, 39.28), 1.24)]),                                                             # "Those are his buyers."
 (C(39.92, 39.28),     1.00, [("push", C(41.76, 41.20), 1.03)]),                                                             # "YC is similar in shape." (topic shift)
 (C(41.76, 41.20),     1.15, [("push", C(43.44, 42.88), 1.17)]),                                                             # "Tons of their advice is free."
 (C(43.44, 42.88),     1.05, [("push", 44.59, 1.08), ("ease", 44.59, 0.40, 1.20), ("push", C(48.00, 47.12), 1.22)]),       # "seven percent"
 (C(48.00, 47.12),     1.28, [("push", C(49.04, 48.40), 1.30)]),                                                             # "Here's the catch:"
 (C(49.04, 48.40),     1.30, [("ease", C(49.04, 48.40), 0.60, 1.00), ("push", f(1254), 1.05)]),                             # "if your product just does the job..."
 (f(1254),             1.12, [("push", C(55.78, 55.06), 1.16)]),                                                             # "But if it only works when..."
 (C(55.78, 55.06),     1.04, [("push", C(58.66, 57.86), 1.07)]),                                                             # "like fitness, coaching..."
 (C(58.66, 57.86),     1.15, [("push", 60.53, 1.22), ("ease", 60.53, 0.50, 1.38), ("push", 62.11, 1.39)]),                 # "charge for the follow-through"
]
def zoom_at(t):
    t = max(0.0, t); i = max(k for k, s in enumerate(SHOTS) if s[0] <= t + 1e-6); t0, z, evs = SHOTS[i]; cur = t0
    for e in evs:
        if e[0] == "push":
            tend, zt = e[1], e[2]
            if t < tend: return z + (zt - z) * eio((t - cur) / max(1e-6, tend - cur))
            z, cur = zt, tend
        else:
            ts, d, zt = e[1], e[2], e[3]
            if t < ts: return z
            if t < ts + d: return z + (zt - z) * (eoc if e[0] == "snap" else eic)((t - ts) / d)
            z, cur = zt, ts + d
    return z

if __name__ == "__main__" and sys.argv[1] == "plan":
    for s in SHOTS: print(f"{s[0]:6.3f} {s[1]:.2f}", [(e[0],) + tuple(round(x, 3) for x in e[1:]) for e in s[2]])
    sys.exit()

FY = FACE[1] / SH
def render(src, z):
    s = z * (2 * W / SW)
    M = np.float32([[s, 0, 2 * W * FACE[0] / SW - s * FACE[0]], [0, s, 2 * H * FY - s * FACE[1]]])
    big = cv2.warpAffine(src, M, (2 * W, 2 * H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", P + "part1.mp4", "-i", P + "part2.mp4", "-filter_complex",
                        "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24000/1001", "-i", "-",
                        "-i", AUD, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", sys.argv[1]], stdin=subprocess.PIPE)
log = open(sys.argv[2], "w"); cuts = [s[0] for s in SHOTS]
for n in range(NFR):
    raw = dec.stdout.read(SW * SH * 3)
    if len(raw) < SW * SH * 3: break
    src = np.frombuffer(raw, np.uint8).reshape(SH, SW, 3); t = n / FPS
    z0 = zoom_at(t - 0.25 / FPS); z1 = zoom_at(t + 0.25 / FPS); z = zoom_at(t)
    cut = any(abs(t - c) < 0.6 / FPS for c in cuts)
    if abs(z1 - z0) > 0.003 and not cut:            # motion blur on fast moves, 180-degree shutter
        fr = np.mean([render(src, z0 + (z1 - z0) * k / 5).astype(np.float32) for k in range(6)], axis=0).astype(np.uint8)
    else: fr = render(src, z)
    log.write(f"{t:.3f} {z:.4f}\n"); enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("done", n + 1)
