"""Mochary reel — sound design. Bed = Akshit's edit audio (voice + his music, untouched). Every cue is anchored to a measured picture event."""
import sys, math, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
from pedalboard import Pedalboard, Compressor
sys.path.insert(0, '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/sd')
from synth import tick, clack
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad'
SR = 48000; FX = S + '/sfx/'; FPS = 24000 / 1001
bed, _ = sf.read(S + '/ed/ed48.wav'); N = len(bed)
T = lambda t: int(round(t * SR)); fr = lambda n: n / FPS
rng = np.random.default_rng(7)
_cache = {}
def load(name, s0=0.0, s1=None):
    if name not in _cache:
        x, _ = sf.read(FX + name + '.wav'); x = x - x.mean(0)
        _cache[name] = signal.sosfiltfilt(signal.butter(2, 30, 'hp', fs=SR, output='sos'), x, axis=0)
    return _cache[name][T(s0):(T(s1) if s1 else None)].copy()
sfx = np.zeros((N, 2)); log = []
def place(name, at, peak_db, anchor=0.0, s0=0.0, s1=None, pan=0.0, fi=0.003, fo=0.01, hp=None, lp=None, cut=None, x=None):
    if x is None: x = load(name, s0, s1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    if hp: x = signal.sosfilt(signal.butter(2, hp, 'hp', fs=SR, output='sos'), x, axis=0)
    if lp: x = signal.sosfilt(signal.butter(2, lp, 'lp', fs=SR, output='sos'), x, axis=0)
    n = len(x); x = x.copy()
    k = min(n, T(fi)); x[:k] *= np.linspace(0, 1, k)[:, None] if k else 1
    k = min(n, T(fo)); x[n - k:] *= np.linspace(1, 0, k)[:, None] if k else 1
    x *= 10 ** (peak_db / 20) / (np.abs(x).max() + 1e-9)
    x[:, 0] *= np.cos((pan + 1) * np.pi / 4) * 1.414; x[:, 1] *= np.sin((pan + 1) * np.pi / 4) * 1.414
    st = T(at - anchor)
    if cut is not None:
        ce = T(cut) - st
        if 0 < ce < n: r = T(0.005); x[ce - r:ce] *= np.linspace(1, 0, r)[:, None]; x[ce:] = 0
    a0, b0 = max(0, st), min(N, st + n)
    if b0 > a0: sfx[a0:b0] += x[a0 - st:b0 - st]
    log.append((round(at, 3), name, peak_db))
def add_mono(sig, at, db, pan=0.0):
    sig = sig * 10 ** (db / 20) / (np.abs(sig).max() + 1e-9); i = T(at); n = min(len(sig), N - i)
    if n <= 0: return
    sfx[i:i + n, 0] += sig[:n] * np.cos((pan + 1) * np.pi / 4) * 1.414; sfx[i:i + n, 1] += sig[:n] * np.sin((pan + 1) * np.pi / 4) * 1.414
def eoc(u): u = np.clip(u, 0, 1); return 1 - (1 - u) ** 3
def eic(u): u = np.clip(u, 0, 1); return np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)
def reel_ticks(t0, lands, spins, db, base_f=2400, clack_db=None, pan_spread=0.5):
    """slot-machine digit reels: p = target + rot*10*(1-eoc(u)); one tick per integer crossing, clack on landing."""
    lay = np.zeros(N)
    for j, (tl, rot) in enumerate(zip(lands, spins)):
        total = rot * 10; ks = np.arange(1, total + 1)
        u = 1 - (1 - ks / total) ** (1 / 3)                            # eoc inverse
        times = t0 + u * (tl - t0); gaps = np.diff(np.concatenate([[t0], times]))
        f0 = base_f + 220 * j
        for tt, g in zip(times, gaps):
            lvl = np.clip(g / 0.035, 0.15, 1.0) ** 0.6
            s = tick(f0 * rng.uniform(0.96, 1.04), body=780 + 40 * j, level=lvl * 0.5, seed=int(tt * 1e5) + j)
            i = T(tt); lay[i:i + len(s)] += s[:max(0, N - i)]
        s = clack(freq=1750 + 70 * j, level=0.6, seed=j); i = T(tl); lay[i:i + len(s)] += s[:max(0, N - i)]
    lay *= 10 ** (db / 20) / (np.abs(lay).max() + 1e-9)
    sfx[:, 0] += lay * 0.95; sfx[:, 1] += lay * 1.05
# ======================================================================== CUES
# --- 1.04 opener: cut into the dark, Altman on the bloom
place('whfast2', 1.04, -24, anchor=0.33, lp=9000)
place('hl1', 1.08, -26, anchor=0.035, s1=0.40, fo=0.08)
place('whslow1', 1.31, -31, anchor=0.45, s0=0.15, s1=1.05, fi=0.05, fo=0.25, pan=0.3)     # Huffman slides in
place('hl3', 1.60, -29, anchor=0.065, s1=0.42, fo=0.08, pan=0.2)                           # connector line draws
place('whslow2', 2.32, -30, anchor=0.70, fi=0.1, fo=0.3)                                    # camera drops to the third slot
place('crt1', 2.54, -22, anchor=0.03, s1=0.9, fo=0.2, hp=200)                              # silhouette flashes on
place('tension2', 2.60, -26, anchor=0.0, s0=0.0, s1=2.4, fi=0.3, fo=0.6, lp=900)          # low bed under the question
# $1,000,000,000 reels: 3.42 -> digits lock left to right 4.05..4.38
reel_ticks(3.42, [4.05, 4.10, 4.15, 4.20, 4.25, 4.29, 4.33, 4.36, 4.38, 4.40], [3, 4, 4, 5, 5, 6, 6, 7, 7, 8], -16, base_f=2500)
place('whslow3', 5.03, -27, anchor=0.59, fi=0.2, fo=0.4)                                    # push into the silhouette
place('riser1', 6.05, -21, anchor=1.43, s0=0.2, s1=1.46, fi=0.3, fo=0.01, hp=140)
place('hit3', 6.06, -13, anchor=0.18, lp=2500, fo=0.6)                                      # Mochary revealed
place('hl1', 6.12, -22, anchor=0.035, s1=0.40, fo=0.08)                                     # title letters bloom
place('snap1', fr(164), -24, anchor=0.08)                                                   # back to camera
# --- client file: Altman / Armstrong / Tenev
for n_, nm, pn in [(181, 'shutter3', -0.15), (204, 'shutter3', 0.1), (227, 'shutter3', 0.0)]:
    place(nm, fr(n_), -20, anchor=0.015, s1=0.25, fo=0.08, pan=pn)
for tt in (7.86, 8.53, 9.49): place('hl3', tt, -27, anchor=0.065, s1=0.42, fo=0.08)        # name glow
# --- 12.80 cheque -> couch, $10,000 rolling counter
place('whfast3', fr(307), -24, anchor=0.21, lp=7000, fo=0.15)
place('paper2', 12.95, -27, anchor=0.55, fo=0.2)
place('whfast3', fr(337), -27, anchor=0.21, lp=6000, fo=0.15, pan=0.15)
reel_ticks(12.98, [14.38, 14.50, 14.60, 14.70, 14.80], [6, 8, 9, 10, 12], -14, base_f=2300)
place('hit1', 14.81, -14, anchor=0.115, lp=1800, fo=0.8)                                    # weight when $10,000 lands
place('snap3', fr(377), -24, anchor=0.12, lp=6000)
# --- 17.56 old tech -> writing
place('glitch3', fr(421), -23, anchor=0.0, s1=0.40, fo=0.15, lp=8000)
place('crt2', fr(429), -24, anchor=0.03, s1=0.9, fo=0.2, hp=120)
place('keys3', fr(431), -24, anchor=0.006, s0=2.1 - 0.006, s1=2.1 + 0.30, fo=0.08)
place('paper1', fr(443), -24, anchor=0.0, fi=0.05, cut=fr(473))                            # pen + paper on the writing shot
place('snap3', fr(473), -26, anchor=0.12, lp=6000)
# --- 20.19 calendar
place('whfast2', fr(484), -24, anchor=0.33, lp=10000)
for i, tt in enumerate([20.48, 20.70, 20.91, 21.12]): place('tap1', tt, -21 + i * 0.5, anchor=0.01, s1=0.12, fo=0.04, pan=-0.4 + 0.2 * i, hp=700)
place('pop2', 21.36, -20, anchor=0.0, s1=0.12, fo=0.05, pan=0.1)                            # Friday lands
place('notif1', 21.43, -21, anchor=0.0, fo=0.3)                                             # check-in event pops in
place('hl3', 21.50, -27, anchor=0.065, s1=0.42, fo=0.08)                                    # marker ring draws
place('whslow2', 21.30, -30, anchor=0.70, fi=0.2, fo=0.3)                                   # push into Friday
# --- 22.27 coaching footage montage + Kling office shots
for n_, pn in [(534, 0.0), (553, 0.2), (586, -0.2), (605, 0.15), (628, -0.1), (648, 0.0)]:
    place('whfast3', fr(n_), -29, anchor=0.21, lp=6500, fo=0.15, pan=pn)
amb = load('office1', 0.0, 4.0)
place('office1', fr(605), -30, anchor=0.0, x=np.concatenate([amb, amb[::-1]])[:T(fr(628) - fr(605))], fi=0.06, fo=0.03)
place('crt3', fr(628), -26, anchor=0.03, s1=0.8, fo=0.2, hp=120)                            # green-screen terminal
place('keys1', fr(632), -27, anchor=0.0, s1=0.6, fo=0.1)
amb3 = load('office3', 0.0, 3.0)
place('office3', fr(648), -29, anchor=0.0, x=amb3[:T(fr(690) - fr(648))], fi=0.08, fo=0.04)   # boardroom room tone
place('snap1', fr(690), -25, anchor=0.08)
# --- 31.87 founders carousel: one soft tick per card through centre, glide whoosh, lock-on
place('whfast2', 31.87, -23, anchor=0.33, lp=9000)
dt = 1e-3; p, v = -7.5, 7.5; w, z = 3.3, 0.82; last = math.floor(p + 0.5); t = 0.0
while t < 1.9:
    a = -w * w * p - 2 * z * w * v; v += a * dt; p += v * dt; t += dt
    k = math.floor(p + 0.5)
    if k != last:
        sp = abs(v); lvl = np.clip(sp / 7.0, 0.25, 1.0)
        s = tick(1900 * rng.uniform(0.95, 1.05), body=520, dur=0.02, level=1.0, seed=int(t * 1e4))
        add_mono(s, 31.87 + t, -26 + 20 * np.log10(lvl) * 0.6, pan=float(np.clip(-v / 12, -0.4, 0.4)))
        last = k
place('whslow1', 31.95, -28, anchor=0.45, s0=0.15, s1=1.05, fi=0.05, fo=0.3)
place('hit2', 33.57, -18, anchor=0.0, lp=420, fo=0.6)                                       # felt-not-heard lock weight
place('hl1', 33.58, -21, anchor=0.035, s1=0.40, fo=0.08)                                    # orange ring blooms on
place('whslow3', 34.05, -31, anchor=0.59, fi=0.2, fo=0.4)                                   # dissolve back to camera
# --- 37.12 YC shorts: one restrained digital tick per cut
cuts = [890, 897, 904, 911, 918, 925, 932, 939, 946, 953, 961]
for i, n_ in enumerate(cuts):
    place(['glitch1', 'glitch2', 'glitch3'][i % 3], fr(n_), -24 - (i % 2), anchor=0.0, s1=0.12, fo=0.04, pan=[-0.4, 0.3, -0.2, 0.4, 0.0, -0.3, 0.2, -0.1, 0.3, -0.4, 0.0][i])
# --- 40.62 YC: 7% / demo day / batch
place('whfast2', fr(974), -23, anchor=0.33, lp=9000)
place('pop1', 40.70, -19, anchor=0.0, s1=0.15, fo=0.05)                                      # disc pops in
place('pop2', 40.94, -20, anchor=0.0, s1=0.12, fo=0.05, pan=0.05)                           # Y logo pops in
place('snap3', 41.50, -22, anchor=0.12, lp=7000)                                            # slice is scored
place('whfast3', 41.90, -22, anchor=0.21, lp=8000, pan=0.2)                                 # slice flies to YC
place('hit1', 42.47, -15, anchor=0.115, lp=2000, fo=0.6)                                    # lands in the logo
place('hl3', 42.50, -24, anchor=0.065, s1=0.42, fo=0.08)
place('whslow2', 42.60, -29, anchor=0.70, fi=0.15, fo=0.3)                                   # into demo day
u_cross = []                                                                                # weeks 12 -> 0 roll
for k_ in range(1, 13):
    target = 12 - k_; uu = np.linspace(0, 1, 20001); vv = 12 * (1 - eic(uu)); idx = np.argmax(vv <= target + 0.5)
    u_cross.append(42.69 + uu[idx] * 1.05)
for i, tt in enumerate(u_cross):
    s = clack(freq=1600 + 30 * (i % 3), level=0.5, seed=i) if i == 11 else tick(2300, body=700, level=0.5, seed=i)
    add_mono(s, tt, -21 if i < 11 else -16)
place('whslow3', 44.00, -30, anchor=0.59, fi=0.1, fo=0.3)
for i in range(14):                                                                         # batch tiles pop out in a wave
    place('tap1', 44.10 + i * 0.022 + rng.uniform(-0.006, 0.006), -24 - i * 0.55, anchor=0.01, s1=0.12, fo=0.04, pan=float(rng.uniform(-0.5, 0.5)), hp=900)
place('snap1', fr(1081), -24, anchor=0.08)
# --- 52.80 fitness / coaching / software
place('whfast3', fr(1266), -24, anchor=0.21, lp=7000, fo=0.15)
place('whfast3', fr(1285), -25, anchor=0.21, lp=7000, fo=0.15, pan=0.2)
place('whfast3', fr(1307), -25, anchor=0.21, lp=7000, fo=0.15, pan=-0.2)
place('riser1', fr(1336), -24, anchor=1.43, s0=0.4, s1=1.46, fi=0.35, fo=0.01, hp=140)     # lift into the conclusion
place('hit3', fr(1336), -16, anchor=0.18, lp=1200, fo=1.0)
# --- the last line
place('hl1', 58.25, -25, anchor=0.035, s1=0.40, fo=0.08)                                    # "the follow-through"
place('hit2', 58.62, -19, anchor=0.0, lp=380, fo=0.9)
# ======================================================================== sum + master
mix = bed + sfx
master = Pedalboard([Compressor(threshold_db=-14, ratio=1.5, attack_ms=20, release_ms=200)])
m = master(mix.T.astype(np.float32), SR).T.astype(np.float64)
meter = pyln.Meter(SR)
def tp_limit(x, ceil_db=-1.2, look=0.003, rel=0.08):
    up = signal.resample_poly(x, 4, 1, axis=0); pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(x)]
    g = np.minimum(1.0, 10 ** (ceil_db / 20) / np.maximum(pk, 1e-9)); L = int(look * SR); g = minimum_filter1d(g, 2 * L + 1)
    a = np.exp(-1 / (rel * SR)); out = np.empty_like(g); s = 1.0
    for i in range(len(g)): s = g[i] if g[i] < s else a * s + (1 - a) * g[i]; out[i] = s
    out = np.convolve(out, np.ones(L) / L, mode='same'); out = np.minimum(out, g); return x * out[:, None]
gain = -14.0 - meter.integrated_loudness(m)
for it in range(3):
    pre = m * 10 ** (gain / 20); y = tp_limit(pre); gain += (-14.0 - meter.integrated_loudness(y))
up = signal.resample_poly(y, 4, 1, axis=0)
print('LUFS', round(meter.integrated_loudness(y), 2), 'TP', round(20 * np.log10(np.abs(up).max()), 2), 'bed LUFS', round(meter.integrated_loudness(bed), 2))
sf.write(S + '/out/Mochary_v3_mix.wav', y, SR, subtype='PCM_24')
sf.write(S + '/out/Mochary_v3_sfx_stem.wav', sfx * 10 ** (gain / 20), SR, subtype='PCM_24')
print(len(log), 'cues')
