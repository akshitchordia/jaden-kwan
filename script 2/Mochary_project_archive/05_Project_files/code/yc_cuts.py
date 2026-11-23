"""'YC is similar in shape. Tons of their advice is free.' — fast vertical cuts through YC Shorts."""
import sys, subprocess, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/scratchpad/'
W, H = 1080, 1920; FPS = 24000 / 1001
N0, N1 = int(round(39.87 * FPS)), int(round(43.38 * FPS))
# source start seconds (inside each stable stretch) and length in output frames
CLIPS = [(2.35, 7), (3.65, 7), (5.80, 7), (7.90, 7), (9.10, 7), (10.75, 7), (12.35, 7), (14.30, 7), (16.15, 7), (19.10, 8)]
CLIPS.append((21.50, (N1 - N0) - sum(n for _, n in CLIPS)))            # Paul Graham holds to the end
X0, Y0, CW_, CH_ = 836, 246, 464, 754                                  # inside the Shorts player, below the hover icons
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', S + 'cf3/yc.mkv', '-vf', f'crop={CW_}:{CH_}:{X0}:{Y0}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
SRC = np.frombuffer(raw, np.uint8).reshape(-1, CH_, CW_, 3)
from PIL import Image, ImageDraw, ImageFont
U = '/root/.claude/uploads/d8b4c3cb-d71b-55fb-ac43-ad142bdbaa67/'
def make_badge():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open(U + 'ceb80d97-image.png').convert('RGB').crop((4, 0, 362, 357)).resize((58, 58), Image.LANCZOS)
    im.paste(lg, (64, 128))
    d.text((136, 168), 'Y Combinator', font=ImageFont.truetype(S + 'fd/inter-500.ttf', 30), fill=(255, 255, 255, 255), anchor='ls')
    a = np.asarray(im).astype(np.float32) / 255
    sh = cv2.GaussianBlur(a[..., 3], (0, 0), 6) * 0.45
    return a[..., :3], a[..., 3:4], sh[..., None]
BCOL, BA, BSH = make_badge()
rng = np.random.default_rng(2); GR = [rng.normal(0, 0.015, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def frame(src_t, k):
    f = SRC[min(len(SRC) - 1, int(round(src_t * 30)))].astype(np.float32) / 255
    s = H / CH_; w = CW_ * s
    img = cv2.resize(f, (int(round(w)), H), interpolation=cv2.INTER_LANCZOS4)
    x = int((img.shape[1] - W) / 2); img = img[:, x:x + W]
    bl = cv2.GaussianBlur(img, (0, 0), 1.8); img = np.clip(img + (img - bl) * 0.55, 0, 1)
    l = img @ np.array([.299, .587, .114], np.float32); img = l[..., None] + (img - l[..., None]) * 0.85
    img = img + cv2.resize(GR[k % 6], (W, H))[..., None] * (0.6 + 0.4 * img)
    fa = min(1.0, k / 6) * 0.92                                        # quiet, constant YC tag top-left
    img = img * (1 - BSH * fa) ; img = img * (1 - BA * fa) + BCOL * BA * fa
    return np.clip(img, 0, 1)
out = sys.argv[1]
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24000/1001', '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
k = 0
for st, n in CLIPS:
    for j in range(n):
        enc.stdin.write((frame(st + j / FPS, k) * 255 + 0.5).astype(np.uint8).tobytes()); k += 1
enc.stdin.close(); enc.wait(); print('frames', k, N0, N1)
