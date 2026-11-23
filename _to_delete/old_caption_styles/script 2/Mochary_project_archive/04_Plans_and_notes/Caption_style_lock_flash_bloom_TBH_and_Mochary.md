# TBH Talking Head — Caption Style Lock

Locked 17 Oct 2026. Reference: snapgram.io_926q5u83yd46 (NYSE edit). Approved render: TBH_glow_first5s_counter.mp4.
Canvas: 1080 x 1920, 23.976 fps. All pixel values are at this size; scale proportionally for other sizes.

```json
{
  "style_lock": {
    "name": "TBH flash-bloom captions",
    "font": {
      "family": "Newsreader (Production Type, Google Fonts, OFL)",
      "style": "Upright (roman), not italic",
      "weight": "Medium 500",
      "optical_size": "16pt (static 'Newsreader 16pt Medium', or variable opsz = 16)",
      "size_captions_px": 82,
      "size_counter_px": 124,
      "tracking": "-0.028 em  (After Effects tracking -28)",
      "word_space": "0.92 x the font's normal space",
      "color": "#FFFFFF, no stroke, no box, no drop shadow"
    },
    "copy_rules": {
      "case": "all lowercase except I and proper nouns (TBH, Nikita Bier, X, Instagram, Snapchat, Facebook)",
      "punctuation": "none",
      "chunking": "1-4 words per spoken phrase, one line only"
    },
    "layout": {
      "caption_baseline_y": 1415,
      "counter_baseline_y": 1297,
      "alignment": "line centered on the FULL phrase width; positions fixed before any word appears, so nothing shifts as words light up"
    },
    "word_reveal": {
      "trigger": "each word starts 0.05 s (about 1 frame) before its spoken onset",
      "opacity": "0 -> 100 over 0.05 s",
      "core_blur": "Gaussian 6 px -> 0, exponential decay, time constant 0.06 s (sharp after about 0.2 s); core brightness boosted while blurred so it reads as a white blob",
      "flash_glow": "glow exposure 8x -> 1x, exponential decay, time constant 0.085 s (about 4-6 frames)",
      "motion": "none. No slide, no scale, no position change"
    },
    "steady_glow": {
      "blend": "Screen, opacity 80%",
      "color": "neutral warm-white #FFFAF2",
      "layers_sigma_px_x_strength": ["3 x 0.95", "10 x 0.75", "24 x 0.50", "72 x 0.28"]
    },
    "line_change": "next phrase replaces the line with a 0.07 s fade (reads as a cut)",
    "temporal_sampling": "4 sub-frames per frame, 180-degree shutter (12 during the counter roll)",
    "counter_5_000_000": {
      "trigger": "on the spoken word 'five'; '5 million' is removed from the caption line, 'downloads' stays in it",
      "row": "own row above captions so it can hold while captions continue",
      "columns": "fixed digit width (widest digit), commas static",
      "reels": "digit j (left to right, j=0..6) spins ceil(1 + 0.5j) full turns + target digit, duration 0.95 + 0.10j s, ease-out quint; lands left to right",
      "window": "each digit masked to its own cell, 24 px soft top/bottom feather",
      "motion_blur": "true multi-sample, 12 sub-frames, 180-degree shutter",
      "entrance": "same flash-bloom as words",
      "lock_bloom": "each digit flashes as it lands: extra glow 1 + 3.5 x e^(-t/0.09 s)",
      "hold": "about 1.05 s after the last digit lands",
      "exit": "0.35 s cosine fade with blur 0 -> 6 px"
    },
    "hard_negative": [
      "no slide-in or slide-up motion",
      "no italic, no Playfair",
      "no repeating or rebuilding words on a second line",
      "no re-centering as words are added",
      "no amber / heavy warm glow tint",
      "no punctuation",
      "no strobing digits: counter must always use true motion blur, never stepped",
      "no stroke, box, or drop shadow"
    ]
  }
}
```

## After Effects / Premiere rebuild (per word)

1. Text: Newsreader 16pt Medium, 82 px, tracking -28, white. Place every word of the phrase in its final position first.
2. Start each word's layer at its spoken frame minus 1.
3. Opacity 0 -> 100 over 1-2 frames.
4. Gaussian Blur 6 -> 0 over about 4 frames, ease out.
5. Deep Glow (white, radius about 70): exposure 8 -> 1 over about 6 frames, ease out. Then hold at 1.
   No Deep Glow? Stack four Glow effects at radius 3, 10, 24, 72 instead.
6. Phrase change: cut to the next line (2-frame fade).

Counter: Slider-driven or per-digit reel layers with a 0.10 s stagger left to right, ease-out quint, motion blur on (180 degrees, 12+ samples), Deep Glow exposure spike of about 4.5x over 3 frames on each digit's landing frame.
