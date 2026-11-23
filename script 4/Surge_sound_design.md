# Surge v3: sound design (cue sheet + ElevenLabs prompts)

Built from both references:
- **Blackbox film:** deep sub swells, glassy tonal risers that sweep up into reveals, clean sharp transients on cuts, a beat of near-silence before the big hit.
- **Google-story reel:** voice first, a short air swish on almost every cut, tactile Foley on the props (paper, pen, keys, clicks).

**Our rules (from Mochary/Supercell):** restrained and premium; effects sit about 6 dB under the voice; no beeps, buzzers, braams, glitch stutters or data chatter; tactile Foley only where it means something; fewer, better cues.

---

## Part 1: the sound palette (generate these in ElevenLabs)

Settings for every prompt: set the **duration** shown, **prompt influence about 0.6**, generate **3 takes**, download WAV, and name each file with its code (for example `S04_take2.wav`).

| Code | Sound | ElevenLabs prompt | Duration |
|---|---|---|---|
| **S01** | Sub swell | Deep cinematic sub bass swell that blooms and fades, clean and smooth, no distortion, modern tech brand film, no music | 3.0 s |
| **S02** | Air swish | Fast clean air swish, crisp high-frequency whoosh, very short, cinematic transition, no low end, no music | 0.6 s |
| **S03** | Heavy whoosh | Wide cinematic whoosh with a soft sub drop underneath, smooth and expensive, tech commercial transition | 1.4 s |
| **S04** | Tonal riser | Short glassy synth riser sweeping upward, airy and precise, builds tension and stops cleanly, Apple keynote style | 1.8 s |
| **S05** | Reverse swell | Reverse cymbal and air swell building into a cut, smooth, ends abruptly, cinematic | 1.0 s |
| **S06** | Glass shimmer | Soft crystalline shimmer, delicate digital sparkle, high register, gentle and clean | 1.2 s |
| **S07** | Paper drop | Single sheet of thick paper dropped onto a wooden desk, close mic, crisp and dry | 0.5 s |
| **S08** | Pen stroke | Fountain pen drawing one quick confident stroke on textured paper, close mic, dry | 0.8 s |
| **S09** | Typing | Quiet low-profile keyboard typing one short sentence, close mic, clean, no room noise | 1.2 s |
| **S10** | Message sent | Soft airy message-sent sound, minimal and warm, a gentle swoosh with a tiny click, not a beep | 0.5 s |
| **S11** | Light-up tick | Very soft tactile click of a premium light switch, warm, close, single click | 0.3 s |
| **S12** | Glass ping cascade | Twelve soft glassy pings in quick succession, gently rising in pitch, airy reverb tail, elegant | 1.2 s |
| **S13** | Hand truck | Two-wheel hand truck rolling a few steps on a concrete floor, light and short, close mic | 1.4 s |
| **S14** | Marker strikes | Ten quick marker pen strike-through strokes on paper in rapid rhythm, dry, close mic | 0.6 s |
| **S15** | Trading floor | 1980s stock exchange trading floor crowd shouting, reverberant hall, distant and dense | 2.0 s |
| **S16** | Boardroom tone | Tense quiet 1960s boardroom room tone, a chair creak and a cough, warm and analog | 1.5 s |
| **S17** | Film flutter | Vintage 16mm film projector flutter starting up, short, warm and mechanical | 0.8 s |
| **S18** | Split-flap roll | Mechanical split-flap display flipping rapidly then settling with one final clack | 0.8 s |
| **S19** | Camera push | Short punchy camera push whoosh with a subtle low thump, clean, modern | 0.5 s |
| **S20** | Brand impact | Cinematic tech logo impact, deep clean boom with a long glassy shimmer tail, premium, no music | 3.0 s |
| **S21** | Pan whoosh | Smooth slow camera pan whoosh, airy, wide stereo, gentle, like a 3D camera gliding sideways | 0.9 s |
| **S22** | Line draw | Thin soft analog synth tone gliding like a line being drawn, filtered and delicate | 1.0 s |
| **S23** | Fluorescent hum | Old hospital fluorescent light flickering on with a soft hum, short | 0.8 s |

---

## Part 2: cue sheet (every place a sound goes)
Times are on `Surge_v3_final.mp4`. ★ = must-have, ○ = nice-to-have.

### Hook (0.00–3.09)
| Time | Moment | Sound | |
|---|---|---|---|
| 0.00 | Altman, camera pulls back | S01 sub swell, low | ★ |
| 0.21 | Camera glides right to Pichai | S21 pan whoosh | ★ |
| 0.69 | Glides right to Amodei | S21 (another take) | ★ |
| 1.75 | Glides right to the silhouette | S21, slightly longer | ★ |
| 2.09 | "?" lights on his face ("a guy") | S06 glass shimmer | ★ |
| 3.09 | Cut to your face | S05 reverse swell ending exactly on the cut | ○ |

### Act 1 (3.09–13.64)
| Time | Moment | Sound | |
|---|---|---|---|
| 4.13 | Your dark montage in ("$1.2 billion") | S03 heavy whoosh | ★ |
| 6.26 | Back to face | S02 air swish (out) | ○ |
| 6.40 | Snap on "zero" | S19 camera push | ★ |
| 8.17 | Edwin footage in | S02 air swish | ★ |
| 8.60–9.72 | Into the Surge logo | S04 riser ending on 9.72 | ★ |
| 9.72 | Surge logo wipes on | S20 brand impact (keep the tail short, about 1 s) + S06 shimmer on the wipe edge | ★ |
| 10.66 | Benchmarks page floats in | S02 air swish | ★ |
| 11.67 / 11.78 / 11.89 / 12.00 / 12.11 | Five lab logos light up | S11 tick ×5, very quiet | ○ |
| 12.51 | Your paper node diagram | S07 paper drop | ★ |

### Act 2 (13.64–25.80)
| Time | Moment | Sound | |
|---|---|---|---|
| 14.10 | Depth-map crowd ("100 people") | S02 air swish | ★ |
| 14.56 | "100" | S01 sub, short and very low | ○ |
| 16.10 | Paper bar chart | S07 paper drop | ★ |
| 16.90 | Red pen arrow, "day one" | S08 pen stroke | ★ |
| 18.94 | B&W office archive | S17 film flutter | ★ |
| 21.40 | Dot globe in | S03 heavy whoosh | ★ |
| 21.88–22.49 | 12 buyers light up | S12 glass ping cascade (one file, starts 21.88) | ★ |
| 23.72 / 23.92 / 24.12 / 24.32 | Photo cards drop in | S07 paper drop ×4 (vary takes and pitch) | ★ |
| 24.80 | Dotted web draws between them | S22 line draw | ★ |

### Act 3 (25.80–38.04)
| Time | Moment | Sound | |
|---|---|---|---|
| 25.80–27.20 | Mover walks lab A → lab B | S13 hand truck | ★ |
| 27.24 | Chat window | S02 air swish | ○ |
| 27.42–28.12 | "can we get surge in here too?" typing | S09 typing | ★ |
| 28.24 | Sent | S10 message sent | ★ |
| 28.92 | SALES TEAM card | S07 paper drop | ★ |
| 29.17 / 29.34 / 29.51 / 29.68 | Red ticks on each buyer | S08 pen stroke, short ×4 | ○ |
| 30.56 | Snap on "sales" | S19 camera push | ★ |
| 31.48 | 10-buyer grid | S02 air swish | ○ |
| 32.28–32.73 | 10 cells light up | S11 ticks ×10 rapid, very quiet (or skip) | ○ |
| 33.08 | Red card | S03 heavy whoosh | ★ |
| 33.92–34.42 | 10 salesmen struck through | S14 marker strikes | ★ |
| 34.92 | B&W boardroom | S17 film flutter + S16 boardroom tone | ★ |
| 36.10 | Second boardroom | S02 air swish | ○ |
| 37.44 | Snap on "fight" | S19 camera push + S01 sub, short | ★ |

### Act 4 (38.04–end)
| Time | Moment | Sound | |
|---|---|---|---|
| 38.04 | Epic aerial | S03 heavy whoosh (airy) | ★ |
| 38.80 | Hospital corridor | S23 fluorescent hum | ○ |
| 40.44–42.14 | "a million customers" zoom-out | S04 riser over the whole pull-back, S06 shimmer at 42.14 | ★ |
| 43.12 | Snap on "distribution" | S19 camera push + S01 sub | ★ |
| 43.70 | Trading floor | S15 trading floor in | ★ |
| 44.66–45.70 | Trader | S15 continues; cut it dead at 45.70 for contrast | ★ |
| 46.36 | "reportedly" paper | S07 paper drop | ★ |
| 46.65 | Red circle around "reportedly" | S08 pen stroke (circular) | ★ |
| 48.48–49.10 | "a thirty billion" | S05 reverse swell into 49.10 | ★ |
| 49.10–49.60 | $30,000,000,000 rolls | S18 split-flap roll | ★ |
| 49.60 | Number lands | S20 brand impact, full tail over the end | ★ |

---

## What happens next
1. Generate the palette (23 prompts × 3 takes) in ElevenLabs.
2. Drop the WAVs into `script 4\assets\09_sfx\`, keeping the code at the start of each file name.
3. I check every take (onset, tail, low end, how many hits), keep the best, slice multi-hit takes, give dry booms a reverb tail, and place everything on this cue sheet. Effects about 6 dB under the voice, on top of the static music mix. Master −14 LUFS, true peak −1.2.
