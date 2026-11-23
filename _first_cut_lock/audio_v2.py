"""Device audio assembly for Fridge v2 -> /tmp/fr2/mix_v2.wav"""
import json, subprocess, numpy as np
FPS = 24000 / 1001; SR = 48000
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)
# rebuild master audio from the v1 chunk wavs (each starts at (A-0.5)/FPS)
master = np.zeros((int(58 * SR), 2), np.float32)
for A in (0, 517, 807, 1097):
    a = load(f'/tmp/fr/a_{A:04d}.wav'); o = int(round((A - 0.5) / FPS * SR)) if A else 0
    master[o:o + len(a)] = a[:len(master) - o]
arch = load('/tmp/fr/arch_audio.wav'); ARCH0 = 23.72      # already +7.5 dB
edl = json.load(open('/tmp/fr2/audio_v2.json'))
N = json.load(open('/tmp/fr2/n_frames.json'))
out = np.zeros((int(round(N / FPS * SR)) + SR, 2), np.float32)
fade = int(0.006 * SR); ramp = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
for k, s0, s1, t0 in edl:
    if k == 'rc':
        seg = master[int(round(s0 * SR)):int(round(s1 * SR))].copy()
    else:
        seg = arch[int(round((s0 - ARCH0) * SR)):int(round((s1 - ARCH0) * SR))].copy()
    seg[:fade] *= ramp; seg[-fade:] *= ramp[::-1]
    o = int(round(t0 * SR)); out[o:o + len(seg)] += seg
out = out[:int(round(N / FPS * SR))]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-c:a', 'pcm_s24le', '/tmp/fr2/mix_v2.wav'], input=out.tobytes())
print('audio', len(out) / SR, 's')
