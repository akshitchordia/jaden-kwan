"""Render each storyboard v3 B-roll as its own 1080x1920 clip (no captions) for the Premiere XML."""
import sys, os, json, subprocess, numpy as np, cv2
sys.path.insert(0, '/home/claude/sb3')
import anim
from anim import FPS, SRC, glitch, b_mit, b_counter, b_scale, b_ph, b_eng, b_cruise, b_dash, b_booth, b_formula, b_budget, b_meta, b_post, b_tyler, b_fridge, b_end
OUT = '/home/claude/sb3/premiere/broll/'; os.makedirs(OUT, exist_ok=True)

def g(t, t0, u, i, base): return glitch(base, i, 1 - (t - 10.33) / .17)
# (name, start, end, beat fn, beat start for t0/u, beat end)
CL = [
    ('B01_MIT', 5.1, 6.6, b_mit, 5.1, 6.6),
    ('B02_glitch_couldnt', 10.33, 10.50, g, 10.33, 10.50),
    ('B03_counter_over_archival', 15.6, 18.7, b_counter, 15.6, 18.7),
    ('B04_scaleapi_2016', 19.6, 20.8, b_scale, 19.6, 20.8),
    ('B05_producthunt', 20.8, 22.5, b_ph, 20.8, 22.5),
    ('B06a_engineers', 24.3, 24.85, b_eng, 24.3, 25.9), ('B06b_engineers', 24.85, 25.35, b_eng, 24.3, 25.9), ('B06c_engineers', 25.35, 25.9, b_eng, 24.3, 25.9),
    ('B07a_cruise_night', 25.9, 26.35, b_cruise, 25.9, 29.2), ('B07b_cruise_night', 26.35, 26.8, b_cruise, 25.9, 29.2), ('B07c_cruise_hero', 26.8, 29.2, b_cruise, 25.9, 29.2),
    ('B08_selfdriving', 30.5, 32.4, b_dash, 30.5, 32.4),
    ('B09_booth_to_booth', 32.4, 35.4, b_booth, 32.4, 35.4),
    ('B10_playbook_type', 36.1, 39.6, b_formula, 36.1, 39.6),
    ('B11_huge_budgets', 41.6, 43.6, b_budget, 41.6, 43.6),
    ('B12_meta', 44.4, 46.8, b_meta, 44.4, 46.8),
    ('B13_post', 46.8, 48.0, b_post, 46.8, 48.0),
    ('B14_order_placed', 48.0, 49.0, b_tyler, 48.0, 49.0),
    ('B15_fridge_behind_head', 49.0, 51.2, b_fridge, 49.0, 51.2),
    ('B16_end_full_circle', 51.2, 52.77, b_end, 51.2, 52.8),
]
def enc_for(name):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '24000/1001', '-i', '-',
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-video_track_timescale', '24000',
                             OUT + name + '.mp4'], stdin=subprocess.PIPE)
cap = cv2.VideoCapture(SRC)
encs, meta = {}, {}
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    t = i / FPS
    c = next((c for c in CL if c[1] <= t < c[2]), None)
    if c:
        name, a, b, fn, ba, bb = c
        base = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        img = fn(t, t - ba, (t - ba) / (bb - ba), i, base)
        if name not in encs:
            encs[name] = enc_for(name); meta[name] = {'start': i, 'frames': 0}
        encs[name].stdin.write((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8).tobytes()); meta[name]['frames'] += 1
    for n, e in list(encs.items()):  # close clips that are finished
        cc = next(x for x in CL if x[0] == n)
        if t >= cc[2] and e.stdin and not e.stdin.closed:
            e.stdin.close(); e.wait()
    i += 1
    if i % 100 == 0: print('frame', i, flush=True)
for e in encs.values():
    if not e.stdin.closed: e.stdin.close(); e.wait()
json.dump(meta, open('/home/claude/sb3/premiere/clips.json', 'w'), indent=1)
print('done', i, meta)
