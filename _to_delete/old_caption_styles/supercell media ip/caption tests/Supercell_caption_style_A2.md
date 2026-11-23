# Caption style A2: serif with a soft glow (Supercell test)
This is the serif style with Akshit's changes:
- no italics
- no shadow or outline
- placed at the bottom, like the old locked style
- a constant soft glow

## Look
- **Font:** Instrument Serif Regular, 112 px. It shrinks automatically when a line would be wider than 960 px.
- **Case:** sentence case, as spoken. Names stay capitalised.
- **Colour:** warm white (#FFF9F0). Every word is the same weight and style.

## Placement
- **Position:** bottom, centred, baseline y = 1415 (same as the TBH/Mochary lock).
- **Chunking:** 2–4 words per line, broken at natural phrase breaks.

## Animation
- **Word in:** each word rises 34 px out of an invisible mask line on its spoken onset (onset − 0.04 s), over 0.42 s with a quint ease-out. Opacity reaches full in 0.12 s.
- **Line out:** when the phrase ends, the line drifts up 10 px and fades out in 0.14 s.

## Glow
- **Halo:** constant and soft, never flashing. Text alpha is blurred at σ 4 (0.55) + σ 12 (0.45) + quarter-res σ 7 (0.35), screen-blended at 0.5 in a warm white tint.
- **Readability:** only where the shot is bright (the white T-shirt, for example), a very wide soft darkening (σ 26, max 62%) sits behind the words. It reads as diffusion, not a border.
