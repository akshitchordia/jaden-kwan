# Caption style A3: reference match (serif, soft glow, slow-shutter slide-up)
Matched to the "This is what I found at" / "People I meet" captions in Akshit's reference.

## Type
- **Font:** Instrument Serif Regular, a tall, condensed, high-contrast serif like the reference. 100 px; it shrinks automatically if a line would be wider than 940 px.
- **Tracking:** tight, −0.032 em, so the letters nearly touch like the reference. Word spacing is 0.82 × the normal space.
- **Case:** sentence case, as spoken. Names stay capitalised.
- **Colour:** warm white (#FFFAF2). No italics, outline or drop shadow.

## Placement
- **Position:** bottom, centred, baseline y = 1415 (same as the locked placement).
- **Chunking:** 2–4 words per line. Words build up one at a time, then the line is replaced.

## Glow
- **Halo:** constant and soft. Alpha is blurred at σ 4 + σ 12 + quarter-res σ 7, screen-blended at 0.62 in a warm white tint.
- **Bright areas:** only there, a very wide soft darkening (σ 26, max 55%) sits behind the words for readability. It is not a border.

## Animation
- **Word in:** each word slides up 58 px on its spoken onset (onset − 0.04 s) over 0.55 s with a quint ease-out. It is fast at the start, then glides to rest.
- **Opacity:** fades in over the first 0.32 s on a slight curve, so it reveals as it rises.
- **Motion blur:** rendered with a slow, open shutter of 1/12 s, sampled 10 times per frame. The fast start smears vertically, the way a real camera would, then sharpens as the word settles.
- **Line out:** an opacity fade of about 0.16 s, with no movement.
