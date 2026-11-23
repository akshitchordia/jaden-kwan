"""Caption lock v2 renderer (design_system/CAPTION_STYLE_LOCK.md).

Phrase script format (one phrase per item):
  {"place": "th" | "center" | "up", "lines": ["Meta paid", "{n:$14} billion"], "skip": false}
Inline marks: {k:word} = key word (accent italic + reference sweep), {n:$14} = rolling number.
`align()` gives every token a start time from the word-level transcript; `render_rgba(t)` draws one frame.
"""
import re, math, json
from difflib import SequenceMatcher
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import config as C

_font_cache = {}
def font(kind):
    if kind in _font_cache: return _font_cache[kind]
    spec = {'p': C.FONT_PRIMARY, 'k': C.FONT_ACCENT_ITALIC, 'n': C.FONT_NUMBER}[kind]
    f = ImageFont.truetype(f'{C.FONTS}/{spec[0]}', C.SIZE[kind])
    f.set_variation_by_axes(spec[1])
    _font_cache[kind] = f
    return f

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

# ---------- parsing + alignment ----------
def parse_line(line):
    toks = []
    for m in re.finditer(r'\{([kn]):([^}]+)\}|(\S+)', line):
        if m.group(3): toks.append({'text': m.group(3), 'kind': 'p'})
        else:
            kind, txt = m.group(1), m.group(2)
            toks.append({'text': txt, 'kind': kind})
    return toks

def align(phrases, words, tail=0.5):
    """Give every token the start time of its first spoken word. Phrases hard-cut at the next phrase start."""
    ws = [(norm(w['w']), w['s'], w['e']) for w in words]
    ptr = 0
    def find(token_text):
        nonlocal ptr
        parts = [norm(p) for p in token_text.split() if norm(p)]
        if not parts: return None
        for j in range(ptr, min(ptr + 25, len(ws))):
            a, b = ws[j][0], parts[0]
            close = len(b) >= 4 and SequenceMatcher(None, a, b).ratio() >= 0.8
            if a == b or (b.isdigit() and a.startswith(b)) or close:
                ptr = j + len(parts)
                return ws[j][1], ws[min(j + len(parts) - 1, len(ws) - 1)][2]
        return None
    out = []
    for ph in phrases:
        P = {'place': ph.get('place', 'th'), 'skip': ph.get('skip', False), 'lines': [], 'start': None, 'end': None}
        src_lines = ph['lines'] if not P['skip'] else [ph['text']]
        for line in src_lines:
            toks = parse_line(line)
            for tk in toks:
                r = find(tk['text'])
                tk['t'] = (r[0] - C.LEAD) if r else None
                tk['t_end'] = r[1] if r else None
            P['lines'].append(toks)
        ts = [tk['t'] for L in P['lines'] for tk in L if tk['t'] is not None]
        te = [tk['t_end'] for L in P['lines'] for tk in L if tk['t_end'] is not None]
        P['start'] = min(ts) if ts else None
        P['last_word_end'] = max(te) if te else None
        # tokens that failed to align (ASR misheard, e.g. "Matt" for "Meta"): sit just before the next timed token
        flat = [tk for L in P['lines'] for tk in L]
        for i, tk in enumerate(flat):
            if tk['t'] is None:
                nxt = next((q['t'] for q in flat[i + 1:] if q['t'] is not None), None)
                prv = next((q['t'] for q in reversed(flat[:i]) if q['t'] is not None), None)
                tk['t'] = (nxt - 0.22) if nxt is not None else prv
        ts = [tk['t'] for tk in flat if tk['t'] is not None]
        P['start'] = min(ts) if ts else None
        out.append(P)
    for i, P in enumerate(out):
        nxt = next((Q['start'] for Q in out[i + 1:] if Q['start'] is not None), None)
        P['end'] = nxt if nxt is not None else (P['last_word_end'] or P['start']) + tail
    return out

# ---------- layout ----------
def text_width(txt, kind):
    f = font(kind); n = len(txt)
    return f.getlength(txt) + C.TRACK[kind] * C.SIZE[kind] * max(0, n - 1)

def layout(P):
    """Absolute boxes for every token. Lines are left-aligned to each other."""
    space = font('p').getlength(' ')
    rows, block_w, y = [], 0, 0
    for L in P['lines']:
        big = max(C.SIZE[tk['kind']] for tk in L)
        lh = big * C.LINE_SPACING
        x = 0
        for i, tk in enumerate(L):
            if i: x += space
            w = text_width(tk['text'], tk['kind'])
            tk['_x'], tk['_w'] = x, w
            x += w
        rows.append((L, y, lh, big))
        block_w = max(block_w, x); y += lh
    block_h = y
    if P['place'] == 'th':
        ox, oy = C.TH_ANCHOR
    else:
        cy = C.CENTER_Y if P['place'] == 'center' else C.UP_Y
        ox, oy = C.W / 2 - block_w / 2, cy - block_h / 2
    for L, ly, lh, big in rows:
        base = oy + ly + lh * 0.5 + big * 0.36          # optical baseline inside the line box
        for tk in L:
            s = C.SIZE[tk['kind']]
            tk['x'] = ox + tk['_x']; tk['w'] = tk['_w']; tk['base'] = base
            tk['box'] = (tk['x'], base - 0.76 * s, tk['x'] + tk['w'], base + 0.06 * s)   # block / glow box
            tk['ink'] = (tk['x'], base - 0.95 * s, tk['x'] + tk['w'], base + 0.28 * s)   # full glyph extent
    P['bbox'] = (ox, oy, ox + block_w, oy + block_h)
    return P

# ---------- drawing ----------
def draw_text(draw, tk, alpha=255, dx=0, dy=0):
    f = font(tk['kind']); s = C.SIZE[tk['kind']]; tr = C.TRACK[tk['kind']] * s
    txt = tk['text']
    for i, ch in enumerate(txt):
        x = tk['x'] + f.getlength(txt[:i]) + tr * i + dx
        draw.text((x, tk['base'] + dy), ch, font=f, fill=alpha, anchor='ls')

def roll_digits(tk, k):
    """Draw a rolling number into its own alpha tile; returns (tile, x0, y0, rolling)."""
    f = font('n'); s = C.SIZE['n']
    txt = tk['text']
    pad = int(s * 0.4)
    x0, y0 = int(tk['x']) - pad, int(tk['base'] - s * 1.05) - pad
    tw, th = int(tk['w']) + 2 * pad, int(s * 1.35) + 2 * pad
    tile = np.zeros((th, tw), np.float32)
    digit_i, rolling = 0, False
    cell_top = tk['base'] - s * 0.98; cell_bot = tk['base'] + s * 0.12
    for i, ch in enumerate(txt):
        cx = tk['x'] + f.getlength(txt[:i]) + C.TRACK['n'] * s * i
        layer = Image.new('L', (tw, th), 0); d = ImageDraw.Draw(layer)
        if ch.isdigit():
            target = int(ch); spins = 2 + digit_i; steps = spins * 10 + target
            dur = C.NUM_ROLL + 4 * digit_i
            u = min(1.0, max(0.0, k / dur)); e = 1 - (1 - u) ** 3
            pos = e * steps
            speed = 3 * (1 - u) ** 2 * steps / dur if u < 1 else 0.0
            if u < 1: rolling = True
            base_d = int(math.floor(pos)); frac = pos - base_d
            cell = s * 1.0
            for off, dd in ((0, base_d % 10), (1, (base_d + 1) % 10)):
                yy = tk['base'] + (off - frac) * cell
                d.text((cx - x0, yy - y0), str(dd), font=f, fill=255, anchor='ls')
            a = np.asarray(layer, np.float32) / 255
            ky = int(min(0.6 * cell, speed * cell * 0.35))
            if ky >= 2:
                a = cv2.blur(a, (1, ky))
            # clip to the digit cell
            yt, yb = int(cell_top - y0), int(cell_bot - y0)
            a[:max(0, yt)] = 0; a[max(0, yb):] = 0
            digit_i += 1
        else:
            d.text((cx - x0, tk['base'] - y0), ch, font=f, fill=255, anchor='ls')
            a = np.asarray(layer, np.float32) / 255
        tile = np.maximum(tile, a)
    return tile, x0, y0, rolling

def gaussian_glow(mask, r1, r2):
    g1 = cv2.GaussianBlur(mask, (0, 0), r1)
    g2 = cv2.GaussianBlur(mask, (0, 0), r2)
    return g1, g2

def render_rgba(t, phrases):
    """One caption frame at time t (seconds) as an RGBA uint8 array (H, W, 4)."""
    P = next((P for P in phrases if not P['skip'] and P['start'] is not None and P['start'] <= t < P['end']), None)
    out = np.zeros((C.H, C.W, 4), np.uint8)
    if P is None: return out
    text_img = Image.new('L', (C.W, C.H), 0); td = ImageDraw.Draw(text_img)
    block = np.zeros((C.H, C.W), np.float32)
    glow_mask = np.zeros((C.H, C.W), np.float32)
    num_alpha = np.zeros((C.H, C.W), np.float32)
    num_glow = 0.0
    for L in P['lines']:
        for tk in L:
            k = math.floor((t - tk['t']) * C.ANIM_FPS + 1e-6)
            if k < 0: continue
            x1, y1, x2, y2 = tk['box']
            if tk['kind'] == 'p':
                if k == 0:
                    block[int(y1):int(y2), int(x1):int(math.ceil(x2))] = 1
                else:
                    draw_text(td, tk)
            elif tk['kind'] == 'k':
                draw_text(td, tk)
                if k < len(C.KEY_STEPS):
                    xr = x1 + (x2 - x1) * C.KEY_STEPS[k] / 100
                    block[int(y1):int(y2), int(x1):int(math.ceil(xr))] = 1
                    glow_mask[int(y1):int(y2), int(x1):int(math.ceil(xr))] = 0.9 if k == 0 else 1.0
            else:  # rolling number
                tile, x0, y0, rolling = roll_digits(tk, k)
                hh, ww = tile.shape
                ys, xs = max(0, y0), max(0, x0)
                ye, xe = min(C.H, y0 + hh), min(C.W, x0 + ww)
                num_alpha[ys:ye, xs:xe] = np.maximum(num_alpha[ys:ye, xs:xe], tile[ys - y0:ye - y0, xs - x0:xe - x0])
                settle = k - (C.NUM_ROLL + 4 * (sum(c.isdigit() for c in tk['text']) - 1))
                num_glow = max(num_glow, 1.0 if rolling else max(0.0, 1 - settle / 6))
    text = np.asarray(text_img, np.float32) / 255
    text = np.maximum(text, num_alpha)
    # soft shadow under all type
    sh = C.SHADOW; s = C.SIZE['p']
    shadow = cv2.GaussianBlur(np.roll(text, int(sh['dy'] * s), axis=0), (0, 0), sh['blur'] * s * 0.5) * sh['alpha']
    # glow around key-word blocks: inner 30 px, outer 110 px (on 1080)
    glow = np.zeros_like(text)
    if glow_mask.any():
        g1, g2 = gaussian_glow(glow_mask, 16, 60)
        glow = np.clip(g1 * 1.5 + g2 * 1.15, 0, 1)
    if num_glow > 0:
        g1, g2 = gaussian_glow(num_alpha, 10, 32)
        glow = np.maximum(glow, np.clip((g1 * 1.2 * 0.85 + g2 * 1.6 * 0.4) * num_glow, 0, 1))
    white = np.clip(np.maximum(np.maximum(text, block), glow), 0, 1)
    # composite white-over-shadow: colour = white where white, black where only shadow
    a = white + shadow * (1 - white)
    rgb = np.where(a[..., None] > 1e-4, (white / np.maximum(a, 1e-4))[..., None] * 255, 0)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return out

# ---------- QA ----------
def qa(phrases, face_box=None, duration=None):
    """Safe zone, face overlap, glow budget, coverage. Returns list of issues (empty = pass)."""
    S = C.SAFE; issues = []
    glows = 0
    for i, P in enumerate(phrases):
        if P['skip']: continue
        if P['start'] is None: issues.append(f'phrase {i + 1}: no words aligned'); continue
        for L in P['lines']:
            for tk in L:
                x1, y1, x2, y2 = tk['ink']
                if tk['kind'] == 'k': glows += 1
                bad = []
                if x1 < S['left']: bad.append('left')
                if y1 < S['top']: bad.append('top')
                if y2 > S['bottom']: bad.append('bottom')
                if y1 < S['split_y'] and x2 > S['right_upper']: bad.append('right')
                if y2 > S['split_y'] and x2 > S['right_lower']: bad.append('right (buttons)')
                if face_box and P['place'] == 'th':
                    fx1, fy1, fx2, fy2 = face_box
                    if x1 < fx2 and x2 > fx1 and y1 < fy2 and y2 > fy1: bad.append('ON FACE')
                if bad: issues.append(f"phrase {i + 1} '{tk['text']}': {', '.join(bad)}")
    if duration:
        budget = max(2, round(C.GLOW_BUDGET_PER_MIN * duration / 60))
        if glows > budget: issues.append(f'glow budget: {glows} key words in {duration:.0f}s (max {budget})')
    shown = [P for P in phrases if not P['skip'] and P['start'] is not None]
    for a, b in zip(shown, shown[1:]):
        if any(tk['kind'] == 'k' for L in a['lines'] for tk in L) and any(tk['kind'] == 'k' for L in b['lines'] for tk in L):
            issues.append('glow on two phrases in a row: ' + ' '.join(tk['text'] for L in b['lines'] for tk in L))
    for P in shown:
        if sum(tk['kind'] == 'k' for L in P['lines'] for tk in L) > 1:
            issues.append('two glow words in one phrase: ' + ' '.join(tk['text'] for L in P['lines'] for tk in L))
    return issues, glows
