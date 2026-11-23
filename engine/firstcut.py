"""First-cut renderer: FIRST_CUT_LOCK.md as code (cut tightening + face-anchored zoom plan + render from the master).

Usage: python firstcut.py <master_video> <words.json> <overrides.json> <out_dir> [--plan-only]

overrides.json (per reel, all optional):
  {"snaps": ["14", "biggest", "fridge#2"],          # words for the 3-4 snaps ("word#n" = n-th occurrence)
   "section_starts": ["launch broad", "this problem"],  # pause before these gets 0.22 s
   "dramatic_after": ["later"],                       # pause after these gets 0.25 s
   "first_th_reveal": 0.0}                            # output time where the talking head first appears (hook before it)
"""
import sys, os, json, math, subprocess, time, re
import numpy as np, cv2
import config as C

FC = dict(sil_db=-42.0, win=0.010, long_pause=0.35, gap=0.20, gap_section=0.22, gap_dramatic=0.25,
          head=0.12, tail=0.35, fade=0.006, zmax=1.53, rest=1.10, push=0.11, pull=0.12, snap=0.30, snap_frames=6,
          whip_frames=4, jump_min=0.20, open_from=1.30, open_dur=2.4, cut_diff=28.0, black_luma=12.0)

def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())

def run(cmd, **kw): return subprocess.run(cmd, check=True, **kw)

def probe(path):
    out = subprocess.run([C.FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', path],
                         capture_output=True, text=True).stdout
    j = json.loads(out); s = j['streams'][0]; a, b = s['r_frame_rate'].split('/')
    return dict(w=int(s['width']), h=int(s['height']), fps=float(a) / float(b), rate=s['r_frame_rate'],
                dur=float(j['format']['duration']))

def load_audio(path, sr=48000, ch=2):
    raw = subprocess.run([C.FFMPEG, '-v', 'error', '-i', path, '-map', '0:a:0', '-f', 'f32le', '-ac', str(ch), '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()

# ---------------- A. the cut ----------------
def silence_runs(mono, sr):
    n = int(FC['win'] * sr); k = len(mono) // n
    rms = np.sqrt(np.mean(mono[:k * n].reshape(k, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    sil = db < FC['sil_db']
    runs, i = [], 0
    while i < k:
        if sil[i]:
            j = i
            while j < k and sil[j]: j += 1
            runs.append((i * FC['win'], j * FC['win'])); i = j
        else: i += 1
    speech = np.where(~sil)[0]
    return runs, (speech[0] * FC['win'], (speech[-1] + 1) * FC['win'])

def nth_word(words, spec):
    w, n = (spec.split('#') + ['1'])[:2]; n = int(n); target = norm(w); c = 0
    for x in words:
        if norm(x['w']) == target or (target.isdigit() and norm(x['w']).startswith(target)):
            c += 1
            if c == n: return x
    return None

def build_edl(words, runs, bounds, fps, ov, black):
    sec = [norm(s) for s in ov.get('section_starts', [])]
    dram = [norm(s) for s in ov.get('dramatic_after', [])]
    start, end = max(0.0, bounds[0] - FC['head']), bounds[1] + FC['tail']
    cuts = []   # (out_t, in_t, gap, reason)
    for rs, re_ in runs:
        if re_ <= start or rs >= end or (re_ - rs) <= FC['long_pause']: continue
        nxt = [w for w in words if w['s'] >= re_ - 0.25]
        prv = [w for w in words if w['e'] <= rs + 0.30]
        gap, why = FC['gap'], 'pause'
        if nxt:
            phrase = norm(' '.join(w['w'] for w in nxt[:3]))
            if any(phrase.startswith(s) for s in sec): gap, why = FC['gap_section'], 'section'
        if prv and norm(prv[-1]['w']) in dram: gap, why = FC['gap_dramatic'], 'dramatic'
        cuts.append((rs + gap / 2, re_ - gap / 2, gap, why, re_ - rs))
    segs, cur = [], start
    for o, i, g, why, plen in cuts:
        segs.append([cur, o]); cur = i
    segs.append([cur, end])
    F = lambda t: int(round(t * fps))
    segs = [[F(a), F(b)] for a, b in segs if F(b) - F(a) >= 2]
    # trim black frames at segment edges (e.g. an empty archival slot)
    for s in segs:
        while s[1] - s[0] > 2 and black.get(s[1] - 1, False): s[1] -= 1
        while s[1] - s[0] > 2 and black.get(s[0], False): s[0] += 1
    return segs, cuts

# ---------------- tracking (faces + his own picture cuts) ----------------
def track(master, info, every=4):
    sw, sh = 432, 768
    p = subprocess.Popen([C.FFMPEG, '-v', 'error', '-i', master, '-map', '0:v:0', '-vf', f'scale={sw}:{sh}', '-f', 'rawvideo',
                          '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=0)
    det = cv2.FaceDetectorYN.create(os.path.join(C.ROOT, 'models', 'face_detection_yunet_2023mar.onnx'), '', (sw, sh), 0.6)
    fsz = sw * sh * 3; prev = None; idx = 0
    faces, diffs, black = {}, {}, {}
    buf = bytearray(fsz); mv = memoryview(buf)
    while True:
        got = 0
        while got < fsz:
            r = p.stdout.readinto(mv[got:])
            if not r: break
            got += r
        if got < fsz: break
        fr = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        black[idx] = float(g.mean()) < FC['black_luma']
        if prev is not None: diffs[idx] = float(np.mean(np.abs(g - prev)))
        prev = g
        if idx % every == 0 and not black[idx]:
            n, f = det.detect(fr)
            if f is not None and len(f):
                x, y, w, h = max(f[:, :4].tolist(), key=lambda r: r[2] * r[3])
                k = info['w'] / sw
                faces[idx] = ((x + w / 2) * k, (y + h * 0.45) * k, w * k, h * k)   # anchor between the eyes and nose
        idx += 1
    p.wait()
    return faces, diffs, black, idx

def split_on_picture_cuts(segs, diffs, black):
    out, pcuts = [], []
    for a, b in segs:
        cur = a
        for f in range(a + 3, b - 3):
            if diffs.get(f, 0) > FC['cut_diff'] and not black.get(f, False) and not black.get(f - 1, False):
                out.append([cur, f]); pcuts.append(f); cur = f
        out.append([cur, b])
    return out, pcuts

def seg_anchor(seg, faces, info):
    pts = [faces[f] for f in range(seg[0], seg[1]) if f in faces]
    if not pts: return (info['w'] / 2, info['h'] * 0.42)
    a = np.median(np.array(pts), axis=0); return (float(a[0]), float(a[1]))

# ---------------- B. the zoom plan ----------------
def ease_io(u): return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2
def ease_out_expo(u): return 1.0 if u >= 1 else 1 - 2 ** (-10 * u)

def plan_zoom(segs, fps, words, ov):
    """Returns per-output-frame zoom list, per-frame segment index, per-frame shutter, and the move log."""
    starts, t = [], 0
    for a, b in segs: starts.append(t); t += b - a
    N = t
    z = np.zeros(N); segi = np.zeros(N, int); shut = np.full(N, 0.25); log = []
    # map source frame -> output frame
    def src2out(sf):
        for i, (a, b) in enumerate(segs):
            if a <= sf < b: return starts[i] + (sf - a)
        return None
    snaps = []
    for sp in ov.get('snaps', [])[:4]:
        w = nth_word(words, sp)
        if w:
            o = src2out(int(round((w['s'] - 0.10) * fps)))
            if o is not None: snaps.append((o, sp))
    reveal = int(round(ov.get('first_th_reveal', 0.0) * fps))
    od = int(round(FC['open_dur'] * fps))
    skipped = [s for s in snaps if reveal <= s[0] < reveal + od]          # the opening move owns its 2.4 s: no snaps inside it
    snaps = [s for s in snaps if s not in skipped]
    for so, name in skipped: log.append(dict(t=round(so / fps, 2), move=f'SNAP "{name}" skipped (inside the opening zoom-out)', z=''))
    pattern = ['whip', 'whip', 'punch']
    direction, prev_end = None, FC['rest']
    for i, (a, b) in enumerate(segs):
        o0, n = starts[i], b - a
        segi[o0:o0 + n] = i
        if i == 0:
            enter, kind = FC['rest'], 'open'
        else:
            kind = pattern[(i - 1) % 3]
            want = 'out' if prev_end >= 1.30 else 'in' if prev_end <= 1.15 else ('in' if direction == 'out' else 'out')
            if want == 'in' and prev_end + FC['jump_min'] > FC['zmax']: want = 'out'
            if want == 'out' and prev_end - FC['jump_min'] < 1.0: want = 'in'
            enter = min(FC['zmax'] - 0.03, prev_end + 0.24) if want == 'in' else max(1.0, prev_end - 0.32)
            direction = want
            log.append(dict(t=round(o0 / fps, 2), move=f'{kind.upper()}-{want.upper()}', z=f'{prev_end:.2f} -> {enter:.2f}'))
        end = enter - FC['pull'] if enter >= 1.28 else min(FC['zmax'] - 0.05, enter + FC['push'])
        for k in range(n):
            z[o0 + k] = enter + (end - enter) * (k / max(1, n - 1))
        # snaps inside this segment: 6-frame ease-in-out, then a near-hold
        for so, name in snaps:
            if o0 <= so < o0 + n:
                z0 = z[so]; z1 = min(FC['zmax'] - 0.02, z0 + FC['snap'])
                for k in range(so, o0 + n):
                    if k < so + FC['snap_frames']: z[k] = z0 + (z1 - z0) * ease_io((k - so + 1) / FC['snap_frames'])
                    else: z[k] = z1 + 0.02 * (k - so - FC['snap_frames']) / max(1, o0 + n - so - FC['snap_frames'])
                log.append(dict(t=round(so / fps, 2), move=f'SNAP "{name}"', z=f'{z0:.2f} -> {z1:.2f}'))
        prev_end = z[o0 + n - 1]
    # opening curved zoom-out at the first talking-head reveal (overrides the base move for 2.4 s)
    for k in range(reveal, min(N, reveal + od)):
        if segi[k] != segi[reveal]: break
        z[k] = min(FC['zmax'], z[k] * (1 + (FC['open_from'] - 1) * (1 - ease_out_expo((k - reveal) / od))))
    log.insert(0, dict(t=round(reveal / fps, 2), move='OPEN curved zoom-out', z=f'{z[reveal]:.2f} -> {z[min(N - 1, reveal + od - 1)]:.2f} over {FC["open_dur"]} s'))
    # whips: blurred zoom across the cut, +/-4 frames, ease-in-out, wider shutter
    wf = FC['whip_frames']
    for i in range(1, len(segs)):
        c = starts[i]
        if pattern[(i - 1) % 3] != 'whip': continue
        A, B = max(0, c - wf), min(N - 1, c + wf)
        zA, zB = z[A], z[B]
        for k in range(A, B + 1):
            z[k] = zA + (zB - zA) * ease_io((k - A) / (B - A))
            shut[k] = 0.35
    return np.minimum(z, FC['zmax']), segi, shut, starts, log, N

# ---------------- render ----------------
def warp(src, zz, anchor, info):
    sw, sh = info['w'], info['h']
    s = zz * C.W / sw
    cw, ch = sw / zz, sh / zz
    x0 = min(max(anchor[0] * (1 - 1 / zz), 0), sw - cw)
    y0 = min(max(anchor[1] * (1 - 1 / zz), 0), sh - ch)
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return M

def render(master, info, segs, z, segi, shut, starts, anchors, N, out_mp4, audio_wav):
    fps = info['fps']
    dec = subprocess.Popen([C.FFMPEG, '-v', 'error', '-i', master, '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                           stdout=subprocess.PIPE, bufsize=0)
    enc = subprocess.Popen([C.FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{C.W}x{C.H}', '-r', info['rate'],
                            '-i', '-', '-i', audio_wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '15', '-preset', 'faster',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k', '-shortest', out_mp4], stdin=subprocess.PIPE)
    fsz = info['w'] * info['h'] * 3; buf = bytearray(fsz); mv = memoryview(buf); have = -1; frame = None
    def zat(k, frac):
        kk = min(N - 1, max(0, k + frac)); lo = int(math.floor(kk)); hi = min(N - 1, lo + 1); u = kk - lo
        if segi[hi] != segi[k]: hi = lo
        if segi[lo] != segi[k]: lo = hi
        return z[lo] + (z[hi] - z[lo]) * u
    tic = time.time()
    for k in range(N):
        i = segi[k]; sf = segs[i][0] + (k - starts[i])
        while have < sf:
            got = 0
            while got < fsz:
                r = dec.stdout.readinto(mv[got:])
                if not r: break
                got += r
            if got < fsz: raise RuntimeError(f'master ended early at source frame {have + 1}')
            have += 1
        frame = np.frombuffer(buf, np.uint8).reshape(info['h'], info['w'], 3)
        a, b = zat(k, -shut[k]), zat(k, shut[k])
        disp = C.W * abs(b / a - 1) * 0.7
        ns = int(min(12, max(1, math.ceil(disp / 1.5))))
        if ns == 1:
            out = cv2.warpAffine(frame, warp(frame, z[k], anchors[i], info), (C.W, C.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        else:
            acc = np.zeros((C.H, C.W, 3), np.float32)
            for j in range(ns):
                zz = zat(k, -shut[k] + 2 * shut[k] * (j + 0.5) / ns)
                acc += cv2.warpAffine(frame, warp(frame, zz, anchors[i], info), (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            out = (acc / ns).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        if k % 100 == 0: print(f'  frame {k}/{N}  {k / max(1e-6, time.time() - tic):.1f} fps', flush=True)
    enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.terminate()
    return time.time() - tic

def build_audio(master, info, segs, path):
    sr = 48000; a = load_audio(master, sr, 2); fps = info['fps']; nf = int(round(FC['fade'] * sr))
    parts = []
    for i, (s, e) in enumerate(segs):
        x = a[int(round(s / fps * sr)):int(round(e / fps * sr))].copy()
        cont_prev = i > 0 and segs[i - 1][1] == s
        cont_next = i < len(segs) - 1 and segs[i + 1][0] == e
        if not cont_prev and len(x) > nf: x[:nf] *= np.linspace(0, 1, nf)[:, None]
        if not cont_next and len(x) > nf: x[-nf:] *= np.linspace(1, 0, nf)[:, None]
        parts.append(x)
    y = np.concatenate(parts)
    run([C.FFMPEG, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', '-', '-c:a', 'pcm_s24le', path], input=y.tobytes())
    return len(y) / sr

def contact_sheet(mp4, times, path):
    cap = cv2.VideoCapture(mp4); ims = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read()
        if ok:
            f = cv2.resize(f, (216, 384)); cv2.putText(f, f'{t:.2f}', (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            ims.append(f)
    cap.release()
    rows = [np.hstack(ims[i:i + 8] + [np.zeros_like(ims[0])] * (8 - len(ims[i:i + 8]))) for i in range(0, len(ims), 8)]
    cv2.imwrite(path, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])

def main(master, words_path, ov_path, out, plan_only=False):
    os.makedirs(out, exist_ok=True)
    info = probe(master); fps = info['fps']
    words = json.load(open(words_path, encoding='utf-8'))['words']
    ov = json.load(open(ov_path, encoding='utf-8')) if ov_path and os.path.exists(ov_path) else {}
    print('master', info)
    mono = load_audio(master, 48000, 1)[:, 0]
    runs, bounds = silence_runs(mono, 48000)
    print('tracking faces and picture cuts...', flush=True)
    faces, diffs, black, nframes = track(master, info)
    segs, cuts = build_edl(words, runs, bounds, fps, ov, black)
    segs = [[a, min(b, nframes)] for a, b in segs if a < nframes and min(b, nframes) - a >= 2]   # tail padding can't pass the master's end
    segs, pcuts = split_on_picture_cuts(segs, diffs, black)
    anchors = [seg_anchor(s, faces, info) for s in segs]
    z, segi, shut, starts, log, N = plan_zoom(segs, fps, words, ov)
    plan = dict(master=master, fps=fps, source_frames=nframes, output_frames=N, output_seconds=round(N / fps, 3),
                segments=segs, anchors=[[round(a, 1), round(b, 1)] for a, b in anchors],
                pauses_cut=[dict(at=round(o, 2), was=round(p, 2), gap=g, why=w) for o, i, g, w, p in cuts],
                picture_cuts=pcuts, moves=log, zoom=[round(float(v), 4) for v in z])
    json.dump(plan, open(f'{out}/plan.json', 'w'), indent=1)
    print(json.dumps({k: plan[k] for k in ('source_frames', 'output_frames', 'output_seconds')}))
    for m in log: print('  ', m)
    if plan_only: return
    wav = f'{out}/firstcut_mix.wav'
    asec = build_audio(master, info, segs, wav)
    secs = render(master, info, segs, z, segi, shut, starts, anchors, N, f'{out}/firstcut.mp4', wav)
    times = sorted(set([0.05, 1.0, 2.4] + [round(starts[i] / fps + d, 2) for i in range(1, len(segs)) for d in (-0.08, 0.04)]))[:40]
    contact_sheet(f'{out}/firstcut.mp4', times, f'{out}/sheet_cuts.jpg')
    print(f'done: {N} frames, audio {asec:.2f}s, render {secs:.0f}s')

if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], a[3], a[4], '--plan-only' in a)
