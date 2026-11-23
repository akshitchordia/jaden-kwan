# context.md: Akshit × Claude, talking-head reel series (TBH → Mochary → Supercell)

Last updated: 26 Oct 2026. This is the full project memory.

It covers:
- what was made and where it lives
- every locked style and the reason for it
- every piece of feedback that changed something
- the technical pipeline used to build it

Read it before touching any of these projects again.

---

## 1. Who and setup

**Akshit Chordia**
- Freelance video producer, editor and creative director.
- Runs 7twenty Studio. Based in India (Pune / Ahmedabad).
- Edits in **Adobe Premiere Pro 2026 on Windows**.
- PC device name: `akshit`. Folders live in `C:\Users\chord\Downloads\`.

**The series.** Short vertical talking-head reels (1080×1920, 23.976 fps, about 50–62 s). Each one tells a founder or company story, and each is made in the same reference style:
1. **TBH**: Nikita Bier, "a gimmick".
2. **Mochary**: "script 2", the CEO coach Matt Mochary.
3. **Supercell**: kill games, soft launch.

**How we work.** Akshit records and does the first cut himself. Claude does:
- zoom passes
- captions
- custom motion graphics and B-roll
- textures
- sound design
- previews and Premiere packages

Claude delivers into his PC folders through the linked-computer bridge.

**Folders on his PC** (all under `C:\Users\chord\Downloads\`)
- `script 2\`: the Mochary project.
  - `Mochary_project_archive\` is the organised archive, with a README.
- `supercell media ip\`: the Supercell project. Contents:
  - all versions v1–v16
  - SRTs, mixes and SFX stems
  - `Premiere project\`, `brolls\`, `caption tests\`, `motion graphics references\`
  - `supercell world moodboard (style lock)\`
  - `_proxy\`, the transfer parts folder; safe to clear
- `Downloads\` root holds his ElevenLabs/SFX mp3 downloads.

**Tools in play**
- **Higgsfield MCP.** He usually prefers that Claude *write prompts* for him. During Supercell he later said **"don't use the Higgsfield MCP any more"**.
- **ElevenLabs MCP**, for sound effects.
  - The flow is "Supercell reel SFX": `qKYYh1qhSw0kF61poQd2`.
  - The plan quota is 10,000 credits; he tops up when it runs out.
  - Files come from `storage.googleapis.com`, which he allowed in Settings → Capabilities.
- **Pinterest** for references; **YouTube** for real footage.
- He records and edits; he sometimes generates his own AI clips (Higgsfield or other tools) and sends them over.

---

## 2. Locked styles, in order of evolution

### 2a. TBH / Mochary caption lock: "flash-bloom" (locked 17 Oct 2026)

The full spec is in `script 2\Mochary_project_archive\04_Plans_and_notes\Caption_style_lock_flash_bloom_TBH_and_Mochary.md`.

**Look**
- Newsreader Medium 500 (opsz 16), about 82–100 px.
- Tracking −0.028 em. White, upright.
- No stroke, no box, no shadow.
- Lowercase except names. No punctuation.
- 1–4 words per line. Baseline y ≈ 1415–1430.

**Animation**
- Each word blooms in: a 6 px blur goes to sharp, with an 8× glow flash, 0.05 s before it is spoken.
- A steady 4-layer glow (σ 3/10/24/72) sits on the text.
- Lines cut with a 0.07 s fade.
- No slide, no italic, never repeat words.

**Counters:** the TBH "5,000,000" and the Mochary "$10,000 / month" use rolling digit reels with motion blur and a lock bloom.

### 2b. Supercell caption lock: "serif glow" (locked 24 Oct 2026, replaces 2a from Supercell onward)

The file is `supercell media ip\Caption_style_LOCK_serif_glow.md`.

**Look**
- Instrument Serif Regular, 112 px (auto-shrinks).
- Warm white #FFF9F0. Sentence case.
- **No italics, no outline or border.**
- Bottom placement.

**Animation**
- Each word rises 34 px out of an invisible mask line on its onset (onset − 0.10 s), over 0.42 s with a quint ease-out.
- Lines drift up 10 px and fade out in 0.14 s.

**Glow**
- A more cinematic glow, on his request: soft glow ×0.85, wide warm halation, a tight bloom, a warm tint, and haze on bright backgrounds.
- The haze reads as a soft drop shadow, and **he wants that shadow kept**. He asked for it back after I removed it once.

**Same animation everywhere.** He rejected unique per-B-roll caption animations and masked or behind-subject words for the body captions. The same talking-head animation runs on every B-roll.

**No commas at line ends.** This applies everywhere, in the video and the SRT.

### 2c. Reels safe zone (enforced from v12)

On 1080×1920:
- **Top 250 px** is unsafe.
- **Bottom 420 px** is unsafe (y > 1500).
- **Left 70 px** is unsafe.
- **Right edge:** for y 250–1110 stay inside x ≤ 1025. For y 1110–1500 stay inside **x ≤ 887**, because the like/comment/share buttons sit there.

Body captions are centred at x 478.5 with a maximum width of about 797 px. Before v12, 14 lines crossed x 887, and he saw captions cut off when posting. **Always check every caption and graphic against this before delivering.**

### 2d. B-roll and graphics look, Supercell

**Supercell-world style lock**
- The mood board is in `supercell media ip\supercell world moodboard (style lock)\`.
- Chunky Pixar-like 3D, warm rim light, gold / green / purple / sky blue, volumetric clouds.

**"Control room at night" direction for graphics**
- Black background, warm-white type, one amber accent for things that are alive.
- Instrument Serif type.
- Things light up and switch off rather than fly in. Slow pushes.

**Texture:** a **halftone texture on every B-roll and graphic, never on the talking head.**

**No clichés.** He rejected:
- treasure chests opening
- generic network lines
- a repeating phone-crowd B-roll
- multicoloured cells

He wants clean, simple, cutout or paper styles.

---

## 3. TBH project (done, archived in earlier sessions)

The full zoom table is in the TBH zoom script (`out/TBH_zoom_script.md`, also in the Mochary archive's notes).

**Zoom pass**
- Face-anchored zooms: CUT, PUSH, EASE IN/OUT and SNAP.
- Snaps land on "a single word", "turn cruel" and "a gimmick". Fast moves have motion blur.

**Graphics**
- 5M counter, anonymous textbox, app blur, the Nikita flash, a Facebook article, a friend map.
- Halftone texture.
- Sound mix (v4).

---

## 4. Mochary project ("script 2"), detailed archive in `script 2\Mochary_project_archive\`

`00_README_Mochary_project.md` there has everything:
- the script
- the zoom moves
- the B-roll plan with Pinterest phrases
- what got built (GFX01 opener, GFX02 client file v1/v3/v4, B02–B11, B04 calendar, B06 founders carousel v1/v2, B07 YC shorts v1/v2, B08 YC equity, C1–C3 coaching footage)
- the captions (flash-bloom)
- the sound design (`mix_moch.py`)
- the cutouts of Altman, Huffman, Mochary, Armstrong and Tenev

**Final:** `Mochary_full_v3_sound.mp4`. The ProRes master is `Mochary_v2_master_ProRes4444.mov` (4.7 GB, in `script 2`).

**Opener with the AI cash-room clip** (`Mochary_opener_cash_captions.mp4` plus an `_ALPHA.mov` overlay)
- Captions are placed beside each person:
  - "Sam / Altman" next to his face
  - "Reddit's CEO"
  - a pull-quote with a leader line: "one coach would add / a billion / dollars" / to his company
  - "that coach is", with the name blurred like his face
  - "Matt Mochary" snapping sharp on the reveal
- An "AI-GENERATED" tag sits top-left.

**Ethics note.** Claude declined to generate a photoreal face-swap of Altman, Huffman and Mochary into a cash-hoarding scene. Claude only captioned his own generated clip on the condition of a visible "AI-generated" tag. His later edit had dropped the tag, and Claude flagged that it should go back before posting.

The quote is the voiceover's wording. No verbatim Altman source was found.

---

## 5. Supercell project (current), `supercell media ip\`

### 5a. Script and word timings

> Supercell has killed more than 30 of its own games. It's launched five hits. That's the company behind Clash of Clans and Clash Royale. The CEO is Ilkka Paananen. And the wild thing is, some of those games were already out with real users. People were actually playing them. Here's how it works. They launch quietly in a few countries like Canada and Australia. They watch the real numbers, and if a game doesn't hit, they kill it. Spooky Pop went into soft launch December 2014. By February, it was gone. And Paananen says it's not even his call. He said, "it's really the game teams that run the show here, not me." So the global launch isn't a test, it's a reward. And you can steal this. Pick a market where the stakes are lower and launch there first. For a consumer app, that's one country. If you need network effects, like a marketplace, that's one city. What you don't do is launch to everyone and pray.

**Timings**
- Base edit: his `Supercell_zoom_v2_motionblur_1.mp4`, 1169 frames, 48.757 s.
- Words were re-transcribed with sherpa-onnx Parakeet and aligned to the script.
- Captions lead each word by 0.10 s.
- Key times:
  - "killed" 0.88
  - "30" 1.36
  - "games" 2.24
  - "five" 4.16
  - "Clash" 6.32
  - "CEO" 8.16
  - "Here's how it works" 14.40
  - "Canada" 17.26, "Australia" 17.82
  - "kill" 21.18
  - "reward" 34.74
  - "one country" ≈ 41.3
  - "one city" 44.51
  - last word → black at frame 1139

### 5b. Final structure (v16)

Frame ranges are at 23.976 fps.

**0–2.33 s, the hook: his axe clip** (American Psycho shot → Clash barbarian in a raincoat → axe close-up; it has its own audio)
- **Shot A (0–0.56):** "Supercell" is big, 228 px, across his chest, centred at x 520, baseline 1068.
  - It has the soft drop shadow plus an extra warm glow.
  - Placements we tried and he rejected: on the top line; behind his head (the masked version); beside his face.
- **Shot B (0.76–1.48):** "has" small, and "**killed**" in red glow with a red underline swipe, top-right in the dark doorway.
- **Shot C (1.48–2.33):** "**30**" at 400 px rolls up from 0 on the wall above the axe head (right-aligned to 1000, baseline 640). Then "of its own / **games**" lands lower right, inside x 887.
- "More than" was removed, at his request.

**2.38–3.09 s, the red "killed" fast cuts**
- Frames 57–73: the 8 game clips from his edit.
- Each gets a crimson duotone and a bright red X: one stroke on the cut frame, the second stroke one frame later.
- A serif counter at the top climbs 4 → 8 → … → 28 → "30+", with "games killed" under it.
- Only this montage gets the treatment; the egg shot after it is untouched.

**From 3.1 s onward: his B-rolls and my graphics.** All of them get halftone texture, and the body captions use the lock.

| Time | What's on screen |
|---|---|
| 4.9–6.2 | Logo build. Still the **Supercell logo placeholder**; he will send a replacement logo. |
| 6.2–8.0, 8.5–10.3 | His B-rolls: Clash art, then the Ilkka clips. |
| 8.51 / 9.05 / 9.59 / 26.74 | CEO clip changes: his supplied SFX (`user_ceo.mp3`) plus a 4-frame warm photo-flash. |
| 11.4–13.1, 21.6–23.3, 26.7–28.1 | His B-rolls. |
| 14.35–17.12 | "Here's how it works": a serif playbook, a gold spark, a dotted globe and pins, and a "Soft launch" tag. |
| 17.12–18.4 | His map clip, with CANADA / AUSTRALIA Clash-style tags popping in. |
| 18.4–20.9 | Goblin numbers clip. |
| 24.8–26.7 | Ghost leaves the tombstone. |
| 28.1–29.4 / 31.4–32.6 | Org chart: a moving sticker cutout of Ilkka Paananen over plain single-tone "Cell" cells, which flips on "not me". |
| 33.9–35.5 | Reward: paper cutouts of Ilkka and a goblin. Crowns drop on "reward", the light warms to gold, three small stars appear. |
| 36.7–39.8 / 39.8–41.9 | Flag, then the dive into one country. |
| 41.9–45.2 | City grows. |
| 47.5 | Cut to black. |

On the hook playbook (14.35–17.12):
- It was first Clash-font; he said that didn't fit the video, so it's serif now.
- A cartoon rocket was replaced by the gold spark.

### 5c. Sound design history, which matters for future taste

| Version | What it was | His verdict |
|---|---|---|
| v4 | My synthesised and library cues | ok at first |
| v6 | Synthesised tech palette | "gimmicky" |
| v7 | 35 ElevenLabs tech sounds, 150 cues | "very heavy tech … extremely ugly" |
| v8 | Restrained, about 50 cues | delivered |
| v8_noSFX | No effects | he asked to do the SFX himself |
| v9 | 26 new ElevenLabs premium sounds, layered and restrained, ducked under the voice | accepted |
| v10 | Shutter plus flash on CEO cuts | — |
| v11 | Replaced with **his own SFX file** on CEO cuts | — |
| v12 | Hook sound design by me | **rejected** |
| v13 | Use **his clip's own audio** for 0–2.33; **removed the braam** on "they kill it" (sounded like a buzzer) | final audio, `Supercell_v13_mix.wav` / `_sfx_stem.wav` |

**Lessons**
- He wants **clean, premium, restrained** sound: cinematic whooshes, risers into hits, booms with tails, and tactile Foley only where it means something.
- **No** dense clicks, glitches, beeps, data chatter, braams or buzzers.
- If he supplies a sound or a clip with audio, **use his, not mine**.

### 5d. Versions in `supercell media ip\`

- **v16 is the current version.** It has the same audio as v13 and its own SRT, `Supercell_v16.srt`.
- v13–v15 were hook caption iterations.
- v12 was the safe-zone fix plus the hook.
- v9–v11 were the sound passes.
- v7/v8 were the red montage, serif playbook and reward scene.
- Earlier versions: v1–v4, the zoom passes and caption tests.

**Premiere package** (`Premiere project\`)
- `Supercell_reel_v3_PREMIERE.xml`, with B-roll media B01–B16, `V3_captions_overlay.mov` and `V1_base_edit.mp4`.
- It was opened and saved as `Supercell reel v3.prproj`.
- It is outdated; rebuild it if he asks.

### 5e. Pending

- **Replacement logo for 4.9–6.2 s.** He will send it.
- Optional: a fresh Premiere package for v16.

---

## 6. Feedback log: what he likes and dislikes

**Likes**
- Dark, cinematic, editorial looks with warm-white serif glow.
- Halftone.
- Slow linear push-ins with snaps only on key words, plus motion blur.
- Paper and sticker cutouts.
- Red as the "killed" accent.
- Big numbers.
- Captions *placed into the scene* for hooks (Mochary opener, Supercell hook).
- Premium, minimal sound.

**Dislikes**
- Clash/Lilita cartoon fonts over his videos ("goes with Supercell vibe but not the video vibe").
- Gimmicky or tech-heavy SFX and buzzers.
- Cliché B-rolls.
- Multicolour UI.
- Abrupt cuts.
- Repeated B-rolls.
- Captions outside the safe zone.
- Commas at line ends.
- Masked or behind-head body captions.
- Text that sits awkwardly over faces.

**His working style**
- Quick, iterative, often from his phone.
- He wants previews fast and decisions shown as **stills first** when he says "show me an image first".
- When he's on PC he wants files in the folder, not phone previews, unless he asks for them.
- He gets frustrated by slow renders and by unrequested extras.

**Speed:** re-render only changed frames (patch the hook frames, copy the rest from the previous version).

---

## 7. Technical pipeline (Claude's workspace; it is ephemeral, so the code is summarised here)

**Base:** his edit, `in1.mp4`.

**Supercell final render**
- `final9.py` (Supercell v12+).
- Patch scripts `hook13`–`hook16.py` re-render only frames 0–56.

**Graphics modules**
- `motion.py`: logo, victory, city.
- `motion2.py`: org chart with the Ilkka cutout (`ilkka_cut2.npz`, u2net_human_seg).
- `motion3.py`: playbook and globe (`global-land-mask` dots).
- `motion4.py`: reward cutouts and crowns (`gob_cut.npz`, ISNet segmentation of the goblin clip).
- `killfx.py`: red montage.
- `ov.py`: Clash tags.
- `caps.py`: caption helpers (`put`, `layout`; Instrument Serif).
- `../moch/kit.py`: halftone.

**Sound**
- `sd/mix_v13.py` uses a `place()` framework, a reverb tail helper and ducking from the bed envelope.
- Master: −14 LUFS integrated, true peak −1.2 dB.
- Sounds are in `el2/` (ElevenLabs premium set) and `user_ceo.mp3` (his).

**Segmentation models:** `u2net_human_seg.onnx` and `isnet-general-use.onnx` (from the rembg GitHub release).

**Delivery to his PC**
1. `zip -0`, then `split -b 24m` into `/mnt/user-data/outputs/<dir>/`.
2. `device_commit_files` into `<project>\_proxy\` (at most 4 parts per call).
3. `device_bash`: `cat` the parts, check the md5, then python `zipfile` extract.

**Watch out:** committing raw .mp4 parts corrupted the first part. Always zip first, and always verify the md5 on both sides.

**Phone previews:** 720×1280 with CRF 24 (about 14 MB), with a timecode in the top-left when he's reviewing timing.
