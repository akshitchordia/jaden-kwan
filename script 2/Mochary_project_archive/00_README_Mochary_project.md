# Mochary reel ("script 2"): project archive

This is a talking-head reel about CEO coach Matt Mochary. It follows the TBH video in the same series and uses the same reference style.

- **Format:** 1080 × 1920, 23.976 fps, about 62 s (1,555 frames).
- **Edit chain:**
  1. Your ProRes master: `Mochary_v2_master_ProRes4444.mov`
  2. My zoom pass: `Mochary_zoom_v1.mp4`
  3. Your B-roll edit
  4. My texture, captions and counter pass: `Mochary_full_v3_captions.mp4`
  5. The sound pass: `Mochary_full_v3_sound.mp4`

## Where everything is

Everything is inside this folder except the 4.7 GB ProRes master, `Mochary_v2_master_ProRes4444.mov`, which stays one level up in `script 2`.

**01_Final**

| What | File |
|---|---|
| Final video with sound design | `Mochary_full_v3_sound.mp4` |
| Final video, captions only (your original audio) | `Mochary_full_v3_captions.mp4` |
| Full mix (voice and music bed plus SFX, −14 LUFS) | `Mochary_v3_mix.wav` |
| SFX on their own | `Mochary_v3_sfx_stem.wav` |
| On-screen captions as SRT (the 44 lines shown in v3) | `Mochary_captions_onscreen_v3.srt` |
| Full transcript SRT, including lines covered by graphics | `Mochary_transcript_full.srt` |

**02_Earlier_versions**
- Zoom pass only: `Mochary_zoom_v1.mp4`
- Edit WIPs: `Mochary_edit_v1_wip.mp4`, `Mochary_edit_v2_wip.mp4`
- Full cuts: `Mochary_full_v1.mp4`, `Mochary_full_v2_captions.mp4`
- Opening animation, early versions: `Mochary_open_v1.mp4`, `Mochary_open_v2.mp4`

**03_Brolls_and_graphics**

Every B-roll, graphic and coaching-footage clip, listed in the B-roll section below.

## Script, as spoken
> Sam Altman once told Reddit's CEO that one coach would add a billion dollars to his company. That coach is Matt Mochary. He's worked with Altman, Brian Armstrong, Vlad Tenev, and his whole playbook is online for anybody to read. His firm's coaching starts at 10 grand a month. So what are they paying for? Not the advice. Every session ends with you writing down an action and him going, "I'll check in with you at the end of the week." He does it to himself too. He's literally hired people to sit on his couch and read while he does his admin. And honestly, the free playbook is the smartest part. It's the marketing. It finds the people who read it but don't have the time to implement it themselves. Those are his buyers. YC is similar in shape. Tons of their advice is free, but founders still give up 7% for a demo day deadline and the batch. Here's the catch: if your product just does the job, nobody needs a check-in. But if it only works when people change their behavior, like fitness, coaching, or rolling out new software, then give the playbook away for free and charge for the follow-through.

Word-level timings are in `05_Project_files\data\words_edit_timings.json`. These are the ones the captions use.

## Zoom pass
The full move list is in `04_Plans_and_notes\Mochary_zoom_script.md`.
- Every zoom is anchored on the face.
- Hard cuts sit in the pauses, and slow pushes run across each line.
- SNAP zooms land on "a billion dollars", "10 grand" and "the marketing".
- Punch cuts land on "Not the advice", "Those are his buyers" and "Here's the catch".
- Fast moves have motion blur.
- The cuts at 0:29.9 and 0:52.3 sit on your own jump cuts.

## B-rolls and graphics
The plan, with Pinterest search phrases for each shot, is in `04_Plans_and_notes\Mochary_broll_plan.md`. The look is the same as TBH: fast, abstract or cinematic, never literal stock, halftone texture, and punch lines stay on your face.

What got built, all in `03_Brolls_and_graphics`. The timeline position is in each file name, for example `in-0m22s05f` means it starts at 0:22, frame 5.

| Shot | Files |
|---|---|
| Opener: black, Altman and Huffman cutouts, "?" silhouette, $1,000,000,000 counter, then the Mochary reveal | `Mochary_GFX01_opening`, `Mochary_open_v1`, `Mochary_open_v2` |
| Client file: Altman, Armstrong and Tenev with tracking boxes and labels | `Mochary_GFX02_clientfile` (v1, v3, v4) |
| $10K counter (B02), session card (B03), Friday check-in (B04), couch room (B05), buyer funnel (B06), same-shape cards (B07), 7% batch (B08), gears machine (B09), habit loop (B10), fitness/coach/software install (B11) | `Mochary_brolls\` subfolder |
| Calendar check-in, newer version | `Mochary_B04_calendar_checkin` |
| Founders carousel | `Mochary_B06_founders_carousel` (v1, v2) |
| YC shorts fast cuts | `Mochary_B07_yc_shorts_cuts` (v1, v2) |
| YC equity, demo day and batch | `Mochary_B08_yc_equity_demoday_batch` |
| Coaching footage: stage, webcam, client session | `Mochary_C1_stage`, `Mochary_C2_webcam`, `Mochary_C3_client` |

The portrait cutouts and masks for Altman, Huffman, Mochary, Armstrong and Tenev are in `05_Project_files\cutouts\`.

## Captions: the flash-bloom lock, shared with TBH
The full spec is in `04_Plans_and_notes\Caption_style_lock_flash_bloom_TBH_and_Mochary.md`.

**Look**
- Newsreader Medium (opsz 16) at 100 px.
- Tracking −0.028 em.
- White, sitting at the bottom: baseline about y 1430.
- Shrinks automatically above 960 px wide.
- Lowercase except names.
- No punctuation.

**Animation**
- Each word blooms in from a 6 px blur with an 8× glow flash, 0.05 s before it is spoken.
- A steady four-layer glow sits on the text.
- The next line cuts in with a 0.07 s fade.

**Key words** get a highlight: advice, action, himself, free, marketing, buyers, catch, behavior, follow-through.

**No captions** where a graphic already says the words: 1.04–6.84, 7.55–10.59, 12.80–15.30, 20.19–22.27 and 37.12–45.09 s.

**Other details**
- A big **$10,000 / month** rolling counter sits over the cheque and couch shot. It runs on the same reel-counter logic as the TBH 5M counter, and the footage dims to 62% under it.
- Halftone texture is on every B-roll that didn't already have it. The talking head has none.

(From the Supercell reel onward, captions switched to the new serif glow lock: Instrument Serif. Mochary stays on flash-bloom.)

## Sound design (v3)
The script is `05_Project_files\code\mix_moch.py`.

**Bed:** your edit audio (voice and music), untouched.

**Cues, each anchored to a picture event:**
- **Opener:** the cut into the dark, then Altman appearing on the bloom.
- **Client file:** hits as each portrait lands.
- **Cheque and couch shot:** ticks as the $10,000 counter rolls.
- **Writing and calendar shots:** sounds for the old tech, the writing and the calendar check-in.
- **Coaching montage:** sound under the coaching footage.
- **Founders carousel:** one soft tick per card, a glide whoosh, then a lock-on.
- **YC shorts:** one restrained digital tick per cut.
- **7% / demo day / batch:** accents.
- **Fitness / coaching / software:** accents.
- **Last line:** an ending hit.

**Master:** −14 LUFS, true peak −1.2 dB.

## Project files (to rebuild or tweak anything)
`05_Project_files\code\` has the Python used to render everything:
- `zoom2.py`: zoom pass
- `open_anim.py`: opener
- `clients_anim.py`, `clients_v3.py`, `clients_v4.py`: client file
- `brolls.py`: B02–B11
- `calendar_anim.py`, `faces_carousel_v2.py`, `yc_cuts.py`, `yc_equity.py`, `coach_footage.py`: individual shots
- `final_v3.py`: captions, counter and texture
- `kit.py`: shared helpers, including the halftone and fonts
- `mix_moch.py`: sound

`05_Project_files\data\` has the word timings, the zoom log and the caption timing log. `06_Check_frames\` has the review contact sheets made along the way.
