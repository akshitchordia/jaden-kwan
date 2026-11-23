# FIRST CUT LOCK: the holy brief for every first cut (locked 14 Nov 2026)

Akshit, 14 Nov 2026: "This is going to be our holy thesis and brief for our first cut. The zoom should be exactly like what we did right now, and the cut should also be exactly like what we did right now. No difference, no changes."

**Reference video:** `14th nov\Fridge_zoom_v2_tight.mp4` (Alexandr Wang / Scale AI fridge reel, 1265 frames, 52.76 s, md5 bdc422cc919050f4746c9dbc17eb4240).
**Reference code:** `_first_cut_lock\` (`edl_v2.py`, `zoomplan.py`, `render_v2.py`, `audio_v2.py`, `tl_v2.json`). Reuse it; change only the per-reel inputs (gaps, word times, face positions, archival in/out).

**EDIT ORDER (Akshit, 23 Nov 2026, overrides any older order):** 1) refine the cuts (section A) → 2) add B-rolls and motion graphics, so the video's structure and look are set → 3) ONLY THEN the zoom-ins and zoom-outs (section B), planned around where the B-roll sits → 4) captions last. The first frame is almost always B-roll, so the opening curved zoom-out never goes on frame one; it goes on the first talking-head shot after the B-roll.

Every first cut of a talking-head reel follows this exactly. Do not invent a different zoom style or cut rhythm. If a new reel needs something this doesn't cover, follow the closest rule here and tell Akshit.

---

## A. The cut (tightening)

1. **Map the pauses.** Transcribe (sherpa-onnx Parakeet) for word times. Make a silence map from the voice: 10 ms RMS windows, silence = below −42 dBFS (his voice sits around −20 LUFS, speech p90 about −19 dBFS). Trust the energy map over ASR word times (ASR lags 0.1–0.4 s).
2. **Shrink every pause longer than 0.35 s** to:
   - **0.20 s** at a normal sentence end (the default)
   - **0.22 s** before a new section or the takeaway line (e.g. "Launch broad…", "This problem…")
   - **0.25 s** for a deliberate dramatic beat inside a sentence (e.g. "a week later, | an API for human labor")
   - Pauses of 0.35 s or less stay as they are (commas and breaths).
3. **Cut points:** out = silence start + gap/2, in = silence end − gap/2, both rounded to the nearest frame (23.976 fps). Picture and audio cut together, with a **6 ms audio fade** on both sides of every cut.
4. **Into an archival/interview clip:** cut away about 0.13 s after his last word. Start the archival on its own camera cut or the first word's onset. Gap from his last word to the archival's first word is about 0.1–0.15 s.
5. **Inside the archival:** cut filler repeats ("like… like… like") only where the meaning stays identical ("I need like a million times more data"). The cut sits in the archival's silence; hide it with a whip (section B).
6. **Archival audio:** gain-match to his voice by integrated LUFS (fridge: +7.5 dB), otherwise untouched. Out about 0.1 s after the last word.
7. **J-cut out of the archival (always):** his audio resumes about 0.07 s before his first word, so there's about 0.2–0.25 s from the archival's last word to his first. The archival picture keeps running under his first words for **10 frames (0.42 s)**, then his face cuts in. Never leave dead air between the archival and him.
8. Result on the reference: 57.85 s → 52.76 s, longest remaining pause 0.38 s, no clipped words (check by re-transcribing the cut).

## B. The zoom

**Mechanics**
- **Face-anchored:** zoom about the face centre (per-shot median face position from detection), so the face stays at the same spot on screen while the scale changes. Clamp the crop inside the frame.
- Render from the **full-res master** (1728×3072 for his camera). Max zoom about 1.53, never past the master's headroom (1728/1080 = 1.6) so nothing is upscaled.
- **Motion blur:** 180° shutter. Sample the zoom at sub-frame times and average whenever the frame corner moves more than 1.5 px per frame; cap at 12 samples on the PC render.

**Moves**
- **Base:** slow linear push-ins of about +0.10 to +0.12 across a line (e.g. 1.00 → 1.12), alternating with slow pull-outs of about −0.10 to −0.20 (e.g. 1.38 → 1.20, 1.32 → 1.22, 1.36 → 1.22).
- **Snaps:** 3–4 key words per reel. 6 frames, ease-in-out cubic, about +0.24 to +0.33 (e.g. 1.12 → 1.45, 1.22 → 1.52), then a near-hold (+0.01 to +0.03) until the next cut. Reference snaps: "$14 billion", "biggest customer", "fridge".
- **Every jump cut gets a treatment. Never a bare jump cut.** Use one of two:
  - **WHIP:** a blurred zoom across the cut. ±4 frames around the cut, ease-in-out cubic, shutter widened to ±0.35 frame, scale change of at least 0.2 (in: 1.10 → 1.32, 1.12 → 1.32, 1.14 → 1.36; out: 1.40 → 1.00, 1.45 → 1.00, 1.53 → 1.12). The source switches at the cut, inside the blur.
  - **PUNCH:** a hard cut with a scale jump of at least 0.2 (in: 1.20 → 1.42; out: 1.48 → 1.00, 1.22 → 1.02).
  - Mix on the reference: 7 whips and 3 punches in 53 s. Alternate in and out so it never feels repetitive.
- **First talking-head reveal (LOCKED 23 Nov 2026, standard for every video):** the moment his talking head FIRST appears in the reel, it opens with a slow curved zoom-out. That's usually right after the hook, because hooks normally show no talking head. If a reel opens on the talking head, it happens at 0:00. Spec (option C, slowed): start **1.30x tighter** than the rest framing and ease out to the rest framing over **2.4 s** on an **exponential ease-out** curve (fast at the very start, long smooth glide). Face-anchored, motion blur while fast (none once it settles), cut from the full-res master. The normal zoom plan continues from there.
- ~~**Opening:** start at 1.10 with a snap on the hook's key number or word.~~ (replaced 23 Nov 2026)
- **Archival:** slow push 1.00 → 1.05, whip through its internal cut into the key line (1.05 → 1.18), slow push 1.18 → 1.23 through the J-cut tail.
- **After the archival:** the face comes in tight (1.38) and pulls out.
- **Ending:** whip-out into the last line (1.53 → 1.12), then a slow push to the end (1.12 → 1.24).

**Reference zoom sheet (fridge v2, timeline seconds)**

| Time | Zoom | Move |
|-|-|-|
| 0.00–0.63 | 1.10 → 1.11 | hook settle |
| 0.63–0.88 | 1.11 → 1.35 | SNAP "$14 billion" |
| 0.88–4.75 | 1.35 → 1.40 | push |
| 4.75–5.09 | 1.40 → 1.00 | WHIP-OUT into "At MIT" |
| 5.09–10.05 | 1.00 → 1.10 | push |
| 10.05–10.39 | 1.10 → 1.32 | WHIP-IN into "It couldn't work" |
| 10.39–11.07 | 1.32 → 1.36 | hold |
| 11.07–15.47 | 1.00 → 1.05 | archival push |
| 15.47–15.81 | 1.05 → 1.18 | WHIP-IN through Wang's cut, "a million times" |
| 15.81–18.87 | 1.18 → 1.23 | archival push + J-cut tail |
| 18.87–22.54 | 1.38 → 1.20 | pull-out "So he bought…" |
| 22.54–23.90 | 1.42 → 1.45 | PUNCH-IN "an API for human labor" |
| 23.90–24.23 | 1.45 → 1.00 | WHIP-OUT into "Random engineers" |
| 24.23–29.28 | 1.00 → 1.12 | push |
| 29.28–29.53 | 1.12 → 1.45 | SNAP "biggest customer" |
| 29.53–30.30 | 1.45 → 1.48 | hold |
| 30.30–35.74 | 1.00 → 1.12 | PUNCH-OUT "So Scale went all in…", push |
| 35.74–36.08 | 1.12 → 1.32 | WHIP-IN into "Launch broad" |
| 36.08–39.73 | 1.32 → 1.22 | pull-out |
| 39.73–43.67 | 1.02 → 1.14 | PUNCH-OUT "That's the formula…", push |
| 43.67–44.00 | 1.14 → 1.36 | WHIP-IN into "And this July" |
| 44.00–49.09 | 1.36 → 1.22 | pull-out |
| 49.09–49.34 | 1.22 → 1.52 | SNAP "fridge" |
| 49.34–49.51 | 1.52 → 1.53 | hold |
| 49.51–49.84 | 1.53 → 1.12 | WHIP-OUT into "This problem" |
| 49.84–52.74 | 1.12 → 1.24 | slow push to the end |

## C. Pipeline that made it (so it can be repeated fast)
1. Make a 1080 proxy on the PC (to `_work`), plus 16 kHz audio for transcription.
2. Transcribe, map silences, track the face (Haar cascade on the proxy, per-shot medians).
3. Build the edit list and zoom plan with `edl_v2.py` (gaps, archival in/out, J = 10 frames, the segment list).
4. Render the archival frames in the cloud workspace (Lanczos plus light unsharp for the upscale) and send them zipped.
5. Render the talking head on the PC from the master with `render_v2.py`, into `/tmp` on the VM (never write big intermediates into C:\Video editor from the shell). Read the pipe with `readinto` (bufsize=0) and use cubic warps: about 5–6 fps. Chunks of about 250–300 frames per command (each command must finish in under 3 minutes; background jobs die).
6. Build the audio on the PC with `audio_v2.py` from the master PCM plus the archival wav. Mux AAC 320k. Unmastered at this stage (sound design and the −14 LUFS master come later).
7. Check: frame count, contact sheet of the cut and whip frames, re-transcribe to confirm no clipped words and that no pause over about 0.4 s is left.
8. Copy the final into the project folder with dd in parts and verify the md5 on the PC.
