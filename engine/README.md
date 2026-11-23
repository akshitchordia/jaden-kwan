# Reel engine (local, on Akshit's PC)

Built 23 Nov 2026. Renders the locked styles from `design_system\` on this PC. No cloud workspace, no file transfers.

## Installed toolchain
- ffmpeg 9.1 (winget, Gyan build): libx264, ProRes 4444 with alpha, Intel Quick Sync (h264_qsv). Path in `config.py`.
- Python 3.13: numpy, opencv 5.1, Pillow, scipy, soundfile, pyloudnorm, faster-whisper (word timings, model small.en), rembg (cutouts), onnxruntime.
- MATLAB R2024a was already installed (VideoReader works as a fallback decoder).
- Fonts in `fonts\`: Inter (GT Standard stand-in), Newsreader + Newsreader Italic (HW Cigars stand-ins). Swap the files and the axis values in `config.py` once the real brand fonts arrive.
- Models in `models\`: YuNet face detector (OpenCV zoo).

## Modules
| File | Does |
|---|---|
| `config.py` | Every locked number: sizes, spacing, safe zone, placement, animation steps. Mirror changes from `design_system\CAPTION_STYLE_LOCK.md`. |
| `transcribe.py` | Audio or video to word-level timings (`words.json`). |
| `captions.py` | Caption lock v2: aligns a phrase script to word timings, lays out, and draws each frame (plain-word block, option A key-word sweep with glow, rolling numbers, soft shadow). Also runs QA: safe zone, face overlap, glow budget, no glow on two phrases in a row. |
| `render_captions.py` | Burns captions over a video section and writes the preview MP4, a caption-only ProRes 4444 alpha MOV for Premiere, check stills and `qa_report.json`. |

| `firstcut.py` | FIRST_CUT_LOCK.md as code. Silence map (10 ms RMS, -42 dBFS), pauses over 0.35 s cut to 0.20 / 0.22 (section) / 0.25 (dramatic), 6 ms fades, his own picture cuts detected and split, YuNet face anchors per segment, zoom plan (opening curved zoom-out 1.30x over 2.4 s at the first talking-head reveal, pushes and pull-outs, 3-4 snaps, a whip or punch on every cut alternating in and out), render from the full-res master with motion blur, `plan.json` + contact sheet. |
| `verify_cut.py` | Re-transcribes a rendered cut: word count vs the master (no clipped words), longest remaining pauses, frame count. |

First cut:
```
python transcribe.py <master.mov> words_master.json
python firstcut.py <master.mov> words_master.json overrides.json <out_dir> [--plan-only]
python verify_cut.py <out_dir>/firstcut.mp4 words_master.json <out_dir>/verify.json
```
`overrides.json`: `{"snaps": ["14", "biggest", "fridge#2"], "section_starts": ["launch broad"], "dramatic_after": ["later"], "first_th_reveal": 0.0}`. Archival inserts (J-cut, gain match) are not automated yet.

## Caption script format
```json
[{"place": "th", "lines": ["Meta paid", "{n:$14} billion"]},
 {"place": "th", "lines": ["in a", "{k:fridge.}"]},
 {"skip": true, "text": "then Cruise reached out"}]
```
`{k:word}` = key word (accent italic + glow sweep). `{n:$14}` = rolling number. `place`: `th` talking head (chest, left of mic), `center` B-roll, `up` B-roll with a busy centre.

## Run
```
python transcribe.py <video_or_audio> words.json
python render_captions.py script.json words.json <video> <out_dir> [t_start] [t_end]
```
Speed: about 4.5 frames per second on this CPU (11.4 s of 1080x1920 in about 60 s).

## Still to build
First-cut renderer (silence map, tightening, J-cuts, face-anchored zooms, opening curved zoom), B-roll compositing and halftone, sound mix, reel folder state + dashboard, B-roll search.
