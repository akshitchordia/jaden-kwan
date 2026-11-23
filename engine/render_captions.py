"""Render caption lock v2 over a video section and write: preview MP4 (burned in), caption-only ProRes 4444 alpha MOV, QA report.
Usage: python -I render_captions.py <script.json> <words.json> <video> <out_dir> [t_start] [t_end]"""
import sys, os, json, subprocess, time
import numpy as np, cv2
import config as C
import captions as K

def probe_fps(path):
    r = subprocess.run([C.FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                        '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    a, b = r.split('/'); return float(a) / float(b), r

def face_box(path, t):
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read(); cap.release()
    if not ok: return None
    det = cv2.FaceDetectorYN.create(os.path.join(C.ROOT, 'models', 'face_detection_yunet_2023mar.onnx'), '', (fr.shape[1], fr.shape[0]), 0.6)
    n, faces = det.detect(fr)
    if faces is None or len(faces) == 0: return None
    x, y, w, h = max(faces[:, :4].tolist(), key=lambda r: r[2] * r[3])
    # YuNet box runs brow to chin; pad a little for hair and jaw
    return (int(x - 0.05 * w), int(y - 0.2 * h), int(x + 1.05 * w), int(y + 1.03 * h))

def main(script, words, video, out_dir, t0=0.0, t1=None):
    os.makedirs(out_dir, exist_ok=True)
    phrases = K.align(json.load(open(script, encoding='utf-8')), json.load(open(words, encoding='utf-8'))['words'])
    for P in phrases:
        if not P['skip'] and P['start'] is not None: K.layout(P)
    fps, rate = probe_fps(video)
    fb = face_box(video, max(t0, 0.5))
    dur = (t1 or phrases[-1]['end']) - t0
    issues, glows = K.qa(phrases, fb, dur)
    n = int(round(dur * fps))
    dec = subprocess.Popen([C.FFMPEG, '-v', 'error', '-ss', f'{t0:.4f}', '-i', video, '-t', f'{dur:.4f}', '-f', 'rawvideo',
                            '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=0)
    prev = subprocess.Popen([C.FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{C.W}x{C.H}', '-r', rate,
                             '-i', '-', '-ss', f'{t0:.4f}', '-t', f'{dur:.4f}', '-i', video, '-map', '0:v', '-map', '1:a?',
                             '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                             '-shortest', f'{out_dir}/captions_preview.mp4'], stdin=subprocess.PIPE)
    alpha = subprocess.Popen([C.FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{C.W}x{C.H}', '-r', rate,
                              '-i', '-', '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
                              f'{out_dir}/captions_ALPHA.mov'], stdin=subprocess.PIPE)
    fsz = C.W * C.H * 3; tic = time.time(); stills = {}
    want = set()
    for P in phrases:
        if P['skip'] or P['start'] is None: continue
        for L in P['lines']:
            for tk in L:
                if tk['kind'] in 'kn':
                    for dt in (0.0, 0.07, 0.13, 0.9 if tk['kind'] == 'n' else 0.4):
                        want.add(int(round((tk['t'] + dt - t0) * fps)))
        want.add(int(round(((P['start'] + P['end']) / 2 - t0) * fps)))
    def read_exact(k):
        b = bytearray(k); mv = memoryview(b); got = 0
        while got < k:
            r = dec.stdout.readinto(mv[got:])
            if not r: break
            got += r
        return bytes(b[:got])
    for i in range(n):
        buf = read_exact(fsz)
        if len(buf) < fsz: break
        frame = np.frombuffer(buf, np.uint8).reshape(C.H, C.W, 3).astype(np.float32)
        t = t0 + i / fps
        cap = K.render_rgba(t, phrases)
        a = cap[..., 3:4].astype(np.float32) / 255
        rgb = cap[..., 2::-1].astype(np.float32)          # RGBA -> BGR
        comp = (frame * (1 - a) + rgb * a).astype(np.uint8)
        prev.stdin.write(comp.tobytes()); alpha.stdin.write(cap.tobytes())
        if i in want: stills[i] = comp
    for p in (prev, alpha): p.stdin.close(); p.wait()
    dec.stdout.close(); dec.wait()
    for i, im in stills.items():
        cv2.imwrite(f'{out_dir}/check_{i:04d}.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88])
    rep = {'frames': n, 'fps': fps, 'seconds': round(dur, 2), 'render_s': round(time.time() - tic, 1), 'face_box': fb,
           'glow_words': glows, 'issues': issues,
           'phrases': [{'start': P['start'], 'end': P['end'], 'skip': P['skip'],
                        'text': ' / '.join(' '.join(tk['text'] for tk in L) for L in P['lines'])} for P in phrases]}
    json.dump(rep, open(f'{out_dir}/qa_report.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps({k: rep[k] for k in ('frames', 'seconds', 'render_s', 'face_box', 'glow_words', 'issues')}, indent=1))

if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], a[3], a[4], float(a[5]) if len(a) > 5 else 0.0, float(a[6]) if len(a) > 6 else None)
