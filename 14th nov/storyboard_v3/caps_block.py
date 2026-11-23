"""Reference caption style: word-by-word BLOCK FLASH (ghost -> white block + glow -> word over fading block -> clean)."""
import numpy as np, cv2
from kit import text_mask, blur, comp, add, tlen, rect_mask, W, H, WARM
FPS = 24000 / 1001
LEAD = 0.12
DARK = (0.08, 0.08, 0.09)

# phrase chunks: (words with times from the v2 transcript); chunks inside big-type beats are left out on purpose
C = [
 [('Meta', .08), ('paid', .48), ('$14', .72), ('billion', 1.05)],
 [('for', 1.76), ('a', 1.92), ('stake', 2.00)], [('in', 2.32), ('a', 2.48), ('company', 2.56)],
 [('that', 2.88), ('started', 3.12), ('with', 3.36)], [('a', 3.60), ('camera', 3.76)], [('in', 4.16), ('a', 4.32), ('fridge', 4.48)],
 [('At', 4.96), ('MIT', 5.12)], [('Alexandr', 5.68), ('Wang', 6.08)],
 [('thought', 6.64), ('his', 6.80), ('roommates', 6.88)], [('were', 7.28), ('stealing', 7.44), ('his', 7.68), ('food', 7.84)],
 [('so', 8.24), ('he', 8.40), ('tried', 8.56), ('to', 8.72), ('build', 8.80)], [('a', 9.04), ('camera', 9.12)], [('to', 9.44), ('catch', 9.76), ('them', 10.00)],
 [('It', 10.32), ("couldn't", 10.48), ('work', 10.72)],
 [('then', 11.36), ('that', 11.68), ('was', 11.76), ('like', 11.92)], [('the', 12.08), ('lightbulb', 12.16), ('moment', 12.64)],
 [('like', 13.04), ('oh', 13.20), ('sh*t', 13.36)], [('if', 13.68), ('I', 13.84), ('really', 13.92)], [('want', 14.08), ('to', 14.16), ('make', 14.32), ('this', 14.56)],
 [('I', 14.96), ('need', 15.12), ('like', 15.36)], [('a', 15.68), ('million', 15.92), ('times', 16.24)], [('more', 16.56), ('data', 16.80)],
 [('than', 17.44), ('I', 17.68), ('have', 17.84), ('now', 18.00)],
 [('So', 18.67), ('he', 18.83), ('bought', 18.91)], [('scaleapi.com', 19.15)], [('one', 20.43), ('night', 20.59)],
 [('and', 20.75), ('launched', 20.91)], [('on', 21.15), ('Product', 21.31), ('Hunt', 21.63)],
 [('An', 22.59), ('API', 22.75)], [('for', 23.31), ('human', 23.47), ('labor', 23.71)],
 [('Random', 24.27), ('engineers', 24.67)], [('showed', 25.31), ('up', 25.47)],
 [('then', 25.87), ('Cruise', 26.11)], [('reached', 26.59), ('out', 26.83)], [('through', 26.99), ('their', 27.15), ('website', 27.31)],
 [('and', 27.95), ('in', 28.11), ('the', 28.19), ('blink', 28.27)], [('of', 28.59), ('an', 28.67), ('eye', 28.75)],
 [('became', 28.99), ('the', 29.23), ('biggest', 29.39), ('customer', 29.79)],
 [('So', 30.35), ('Scale', 30.51), ('went', 30.99)], [('all', 31.15), ('in', 31.31), ('on', 31.47)], [('self-driving', 31.55)],
 [('and', 32.43), ('Wang', 32.59), ('walked', 32.91)], [('a', 33.15), ('computer', 33.31), ('vision', 33.63)], [('conference', 34.03)],
 [('booth', 34.59), ('to', 34.83), ('booth', 34.99)], [('with', 35.23), ('a', 35.39), ('laptop', 35.47)],
 [("That's", 40.04), ('the', 40.36), ('formula', 40.44)], [('for', 40.92), ('winning', 41.00)], [('when', 41.32), ("there's", 41.48)],
 [('And', 44.12), ('this', 44.44), ('July', 44.76)], [('now', 45.32), ('running', 45.56)], [('AI', 45.80), ('at', 46.20), ('Meta', 46.28)],
 [('he', 46.84), ('posted', 47.00)], [('that', 47.48), ('its', 47.72), ('AI', 48.04)], [('could', 48.44)],
 [('This', 49.80), ('problem', 50.04)], [('was', 50.36), ('actually', 50.60)], [('the', 50.84), ('inspiration', 51.00)],
]
# end time of each chunk = next chunk's first word (or +0.7 s after its last word, whichever is first)
CH = []
for k, ch in enumerate(C):
    st = ch[0][1] - LEAD
    nxt = C[k + 1][0][1] - LEAD if k + 1 < len(C) else 99
    end = min(nxt, ch[-1][1] - LEAD + 0.75)
    CH.append((st, end, ch))
CUT_END = 51.2  # end card is quiet

# where captions sit (y baseline) and their colour, by time
ZONES = [  # (start, end, y, dark)
    (5.1, 6.6, 330, False), (11.1, 18.9, 1270, False), (19.6, 20.8, 360, False), (20.8, 22.5, 330, False),
    (24.3, 25.9, 1250, False), (25.9, 26.8, 420, False), (26.8, 29.2, 420, True), (30.5, 32.4, 420, False),
    (32.4, 35.4, 380, False), (44.4, 46.8, 420, True), (46.8, 48.0, 1480, False), (48.0, 49.0, 330, True),
]
def zone(t):
    for a, b, y, d in ZONES:
        if a <= t < b: return y, d
    return 1230, False

_fcache = {}
def font():
    if 'f' not in _fcache:
        from frames3 import inter
        _fcache['f'] = inter(50, 540)
    return _fcache['f']

def draw(img, t):
    if t >= CUT_END: return img
    act = next((c for c in CH if c[0] <= t < c[1]), None)
    if act is None: return img
    _, _, words = act
    y, dark = zone(t); col = np.array(DARK if dark else WARM, np.float32)
    f = font(); gap = 50 * .30
    fr = lambda wt: int(np.floor((t - (wt - LEAD)) * FPS))  # frames since this word lands
    vis = [(w, wt) for w, wt in words if fr(wt) >= 0]
    ghost = next(((w, wt) for w, wt in words if fr(wt) == -1), None)
    lay = vis + ([ghost] if ghost else [])
    ws = [tlen(w, f) for w, _ in lay]
    total = sum(ws[:len(vis)]) + gap * max(0, len(vis) - 1)
    x = 478.5 - total / 2
    asc, desc = f.getmetrics()
    for idx, ((w, wt), wd) in enumerate(zip(lay, ws)):
        n = fr(wt)
        if n == -1:  # ghost: faint motion-blurred word sliding in
            mk = text_mask(w, f, (x + 22, y))
            mk = cv2.blur(mk, (31, 1))
            img = comp(img, mk, col, .35)
        else:
            mk = text_mask(w, f, (x, y))
            box = rect_mask(x - 7, y - asc * .78 - 8, x + wd + 7, y + desc * .55 + 6, 3)
            if n == 0:
                img = add(img, blur(box, 22), (1, 1, 1), .55 if not dark else .15)
                img = comp(img, box, (1, 1, 1) if not dark else (0.1, 0.1, 0.11), 1)
            else:
                if n <= 2:
                    img = comp(img, box, (1, 1, 1) if not dark else (0.1, 0.1, 0.11), [0, .35, .15][n])
                img = img * (1 - (blur(np.roll(mk, 3, 0), 6) * .5)[..., None])
                img = comp(img, mk, col, 1)
        x += wd + gap
    return img
