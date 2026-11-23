# Caption style lock (from reference Video-36963, 23 Nov 2026)

Akshit: "These are the captions we go forward with." Fonts are locked to the brand pair. Everything else (size, placement, how words come on, which words glow, when to drop captions) matches the reference.

Reference: `C:\Users\chord\Downloads\Video-36963.mp4` (720x1280, 30 fps, 33.3 s; Adam Neumann / WeWork). Frames and crops are in `references\Video-36963\`.

## Fonts (locked)
- **Primary (plain words):** GT Standard, Medium. Stand-in: Inter Medium.
- **Accent (important words):** HW Cigars, *italic*. Stand-in: Newsreader Italic. The reference sets every key word in a serif italic. If HW Cigars has no italic licensed, use HW Cigars Regular and keep everything else the same.
- White (#FFFFFF), with a soft shadow only (0 2 10 px, black 35%). No box, no stroke.
- Sentence case, like speech: capital at the start of a sentence and on names, otherwise lowercase. Full stops stay at sentence ends. **No commas at line ends** (house rule; the reference sometimes keeps them).

## Size (measured, converted to 1080x1920)
- Plain sans: **66 px** (ascender height about 50 px).
- Accent serif italic: **72 px**, so its x-height reads the same as the sans.
- Line pitch: **57 px** (line height about 0.86). Lines nearly touch; descenders may overlap the next line.
- Letter spacing: about -2%.
- One chunk is 1 to 4 words per line, at most 3 lines (usually 2).

## CURRENT SIZE + TALKING-HEAD PLACEMENT (Akshit, 23 Nov 2026, latest; overrides everything below)
- **Sizes:** plain sans **84 px**, accent serif italic **92 px**, numbers **132 px** (on 1080 wide).
- **Line spacing:** each line is **1.12x** the biggest word on it (more breathing room).
- **Talking head, never on the face:** measured on his framing, the chin sits at about y 1050 and the mic starts at x 620 / y 1040. Captions start at **y 1160** (about 110 px below the chin), left edge **x 90**, on the chest left of the mic. Keep lines to about 12 characters (1-2 words) so they stay clear of the mic, and up to 3 lines (bottom stays above y 1500).
- B-roll keeps the centred placement (about 52%, or moved up when the centre is busy) at the same new sizes.

## Changes from Akshit, 23 Nov 2026 (override the measurements above; sizes and talking-head spot superseded by the section above)
- **Bigger:** plain sans **76 px**, accent serif italic **84 px**, numbers **120 px**.
- **Spacing fixed:** each line is 1.02x the biggest word on it, so lines never collide (the reference's 57 px pitch made "Meta paid" crash into "$14 billion").
- **KEY-WORD ENTRANCE LOCKED 23 Nov 2026 = option A, "Reference sweep":** the reference's own move with nothing added. f0-f1 a white block over the first 25% of the word with a soft glow halo (inner 30 px / outer 110 px on 1080), f2 55%, f3 75%, f4 100% at full glow, f5 the clean word. No trail, no ghost, no echoes. Rejected alternatives: B ink tile, C light bloom, D light-line wipe, E mask rise, and the cinematic light-bar.
- **(REMOVED 23 Nov 2026, he doesn't like it)** ~~Slow-shutter trail on every glow word:~~ a blurred ghost first. As the glowing block grows, its earlier positions linger as a fading trail (40% white, sideways blur). The word lands smeared sideways with two fading echoes trailing left (40% and 18%), then sharpens over 2 frames. Plain words get no trail.
- **Numbers always roll:** every digit spins like an odometer, blurred vertically while it spins, eased to a stop. Digits land left to right, 4 frames apart, with a soft glow that fades over 6 frames after the last one lands. The rest of the key phrase ("billion") then sweeps in.
- **Talking head: never on the face.** The talking-head framing is the same in every reel, so captions go on the chest, left of the mic: left edge at x 110, top at y 1000 (below the chin), lines short enough (1 to 2 words) to stay clear of the mic at x 660+ / y 1050+. B-roll keeps the centred placement below.

## Placement
- The stack is centred on the frame horizontally (x 540). Lines inside it are **left-aligned to each other**, and an accent line may sit indented or pushed right (a staggered stack, like "what do / I need to do / *first*").
- Default height: the block centre sits at **about 52% of the frame** (y about 1000). On a talking head that is the chest, just under the chin.
- **If the centre is busy** (a screen, a phone, a face, text in the shot), move the stack up to **about 30-36%** (y 580-690).
- The left edge stays fixed while words are added. Nothing re-centres mid-phrase.
- It must stay inside the Reels safe zone (x 70+, y 250-1500, x <= 1025 above y 1110, x <= 887 below).

## How words come on (at 30 fps)
Words appear one at a time on the spoken word (lead about 0.1 s). The phrase builds up, holds, then hard-cuts to the next phrase, usually on a shot change.

**Plain word (most words): flat block, no glow**
- f0: a solid white block the size of the word (ascender to baseline), with no halo.
- f1: the word, clean.

**Important word (accent font): sweep with glow** (frame by frame from "*knock*", f849-f856)
- f0-f1: the word is already there, with a white block over its first letter (0-25%). A big soft glow halo surrounds the block (about 45 px radius on 1080) and lights the footage.
- f2: the block grows to about 55%.
- f3: the block reaches about 75%.
- f4: the block covers the whole word, with the glow at its strongest.
- f5: the word, clean, no glow.
- Variation seen on "*first*": one frame before, a motion-blurred ghost of the word (horizontal blur, about 50% opacity), then the full block with glow, then the block slides off to the right over 3 frames.

## Which words are important
- Only the words that carry the line: the payoff noun or verb, the number, the name, the contrast word ("*vision*", "*high*", "*stars*", "*moon*", "*basics*", "*first / second / third*", "*knock on doors*", "*entrepreneurship*").
- About one per phrase, never every phrase. Never the filler ("the", "to", "and", "I need to").
- An accent chunk can be 1 to 3 words when they read as one idea ("*knock on doors*", "*$14 billion*").

## Glow budget (Akshit, 23 Nov 2026: "if you overuse that glow flash effect, it will just be unwatchable")
- The glow sweep goes only on the important lines' payoff word: the hook payoff, the story turn, the product definition, the big result, the takeaway, the final name.
- **About 6 per 50-60 s reel (roughly 1 every 8-10 s).** Never on two phrases in a row. Never two glow words in one phrase.
- Numbers use the roll as their emphasis and don't count against the budget.
- When in doubt, leave it plain. List the near-misses so he can add one.

## When captions drop out (Akshit, 23 Nov 2026)
- **Caption every spoken line by default.**
- Skip a line only when the shot itself already shows the same words: a wordmark, sign or headline that says what's being said (the Cruise logo shot on "then Cruise reached out" is the example).
- Never skip a line just because it seems obvious or the frame looks busy. If the centre is busy, move the stack (see Placement) instead of dropping it.

## Status
- **This is the ONLY caption style.** All older ones are retired: Instrument Serif glow (Supercell), Newsreader flash-bloom (TBH/Mochary), Fridge Inter block-flash (v4/v5), and the Figma v1 caption components. Their old files are in `_to_delete\old_caption_styles\`.
- **LOCKED: caption lock v2** (glow sweep + slow-shutter trail on key words, rolling numbers, sizes and placement above). Approved 23 Nov 2026.
- A softer "cinematic" key-word entrance (light-bar sweep with rise and settle) was tried and **rejected** ("Keep v2"). Don't use it.
- Hooks follow this same caption style unless he asks for a designed hook.
