# memory.md: Akshit's talking-head media IP (complete project memory)

Last updated: 26 Oct 2026.

**This file contains everything from `context.md` and more.** It is the single source of truth for *what we've made, how, and why*. `CLAUDE.md` / `agent.md` describes *how Claude works*. Read both before touching any reel in this series.

---
# Project memory

## Brief
## Current status
## Locked decisions
## Prompts that worked
## Prompts that failed
## Feedback log
## Assets
## New info
## Session log (newest first) 


## 0. Quick status

**Series order:**
1. TBH (done)
2. Mochary, "script 2" (done)
3. Supercell (current final: **v17**)
4. **Script 4**, "Surge" rough cut (next)

**Supercell current files:** `supercell media ip\Supercell_v17.mp4`, plus `.srt`, `_mix.wav` and `_sfx_stem.wav`.

**Open items**
- Supercell: replacement logo for 4.9–6.2 s (Akshit will send it).
- Supercell: optional fresh Premiere package for the latest version.
- Script 4: just started. Keep the Supercell zoom direction; **everything else is new**, including a completely new mood board.
- Not done: a precise cutout of the two axe-holding figures, 9:16 PNG with alpha. It was requested, then interrupted by Akshit before running.

---

## 1. The media IP

Short vertical **talking-head reels** about founders and companies, each built around one sharp business insight.

**Format:** 1080×1920, 23.976 fps, roughly 48–62 s, posted as Instagram Reels.

**Akshit's part:**
- writes or picks the script (the FP-style scriptwriting skill exists for this)
- records himself on camera with a Shure mic in a dark room with blue LEDs
- does the first cut, and picks or generates B-roll

**Claude's part:** finishing.
- zooms
- captions
- custom motion graphics
- texture
- hook design
- sound design
- safe-zone checks
- previews
- delivery into his PC folders, plus Premiere packages

**The look of the series:** dark, cinematic, editorial.
- warm-white serif captions with glow
- halftone texture on B-roll
- slow push-in zooms with snaps on key words
- premium, restrained sound

**Hooks** are designed scenes with captions placed into the shot (the Mochary cash-room opener and the Supercell axe hook).

---

## 2. Setup, people, folders, tools

**Akshit Chordia**
- Freelance video producer, editor and creative director. Runs 7twenty Studio. Based in Pune/Ahmedabad.
- Edits in **Premiere Pro 2026 on Windows**. PC device name: `akshit`.
- Often reviews from his phone; works on PC for final files.

**PC folders** (`C:\Users\chord\Downloads\`)
- `script 2\`: the Mochary project.
  - `Mochary_project_archive\` (01_Final, 02_Earlier_versions, 03_Brolls_and_graphics, 04_Plans_and_notes, 05_Project_files with code, data and cutouts, 06_Check_frames, and `00_README_Mochary_project.md`)
  - plus all deliverables and `Mochary_v2_master_ProRes4444.mov` (4.7 GB)
- `supercell media ip\`: the Supercell project.
  - versions v1–v17, SRTs, mixes and SFX stems
  - `Premiere project\`, `brolls\`, `caption tests\`
  - `motion graphics references\` (11 direction folders and a YouTube references folder)
  - `supercell world moodboard (style lock)\`
  - `Supercell_v1_master_ProRes4444.mov`
  - `_proxy\`: transfer parts; safe to clear
- `Claude_project_brain\`: `CLAUDE.md`, `agent.md`, `context.md`, `memory.md`. Copies also sit in each project folder.
- `Downloads\` root: his downloaded SFX mp3s (ElevenLabs downloads).

**Tools**
- **Higgsfield MCP.** He usually prefers Claude **writes prompts** for him to run. During Supercell he explicitly said **"don't use Higgsfield MCP any more"**, so Claude built its own motion graphics.
- **ElevenLabs MCP**, for sound effects.
  - The flow is "Supercell reel SFX": `qKYYh1qhSw0kF61poQd2`.
  - The plan quota is 10,000 credits. It ran out twice; he topped up.
  - Files download from `storage.googleapis.com`, which he allowed in claude.ai Settings → Capabilities.
- **Pinterest** for references, **YouTube** for real footage. He also generates AI clips himself (the axe/barbarian clip, the cash room).

---

## 3. The production playbook (repeat this for every reel)

1. **Receive the rough cut.** It usually comes as an mp4, sometimes as a ProRes master.
2. **Transcribe to word timings.** Use sherpa-onnx Parakeet, align to the script with difflib, and correct the names (Ilkka Paananen, Mochary…). Captions lead each word by about 0.10 s.
3. **Zoom script.** Face-anchored zooms:
   - slow linear push-ins across lines
   - resets only on jump cuts or phrase changes
   - **snaps only on 3–4 key words**
   - **motion blur** on every move
   - Options so far: v1 plain, v2 motion blur, v3 zoom-through.
4. **B-roll plan.** A beat-by-beat table, each beat marked GFX (Claude builds) or FOOTAGE (he sources), with **Pinterest search phrases**. Cinematic but grounded; avoid clichés.
5. **Mood board / style lock** for the reel's B-roll world (Supercell had the "Supercell world" board).
6. **Motion graphics.** Built in code by Claude: Python, numpy, cv2, PIL. They follow the reel's direction, e.g. "control room at night" for Supercell.
7. **Captions** in the locked style, with **no commas at line ends** and **inside the safe zone**. SRT delivered too.
8. **Hook.** A designed opener with placed captions: big words, numbers, red for "killed", text beside or over the subject, never in the unsafe areas.
9. **Texture.** Halftone on every B-roll and graphic, never on the talking head.
10. **Sound design.** Restrained and premium, or his own SFX and clip audio when he provides them. Master at −14 LUFS, TP −1.2. Deliver the mix, an SFX stem and a no-SFX version on request.
11. **Check.**
    - stills at the changed moments
    - a safe-zone overlay
    - audio balance at key beats
    - frame count and duration (Supercell: 1169 frames, 48.757 s)
12. **Deliver.**
    - zip, then split into parts, then copy to `<project>\_proxy\`, then verify the md5, then extract
    - a phone preview (720p) only when he's on his phone or asks
    - a Premiere package (XML, media, caption overlay MOV) when he wants to edit in the timeline

---

## 4. Locked styles

### 4a. TBH / Mochary caption lock: "flash-bloom" (17 Oct 2026)

**Look**
- Newsreader Medium 500 (opsz 16), about 82–100 px.
- Tracking −0.028 em. White, upright.
- No stroke, box or shadow.
- Lowercase except names. No punctuation.
- 1–4 words per line. Baseline about y 1415–1430.

**Animation**
- Each word blooms in from a 6 px blur with an 8× glow flash, 0.05 s before it's spoken.
- A steady 4-layer glow (σ 3/10/24/72).
- Lines cut with a 0.07 s fade.
- No slide, no italic, never repeat words.

**Key-word highlights:** e.g. advice, action, marketing, buyers.

**Counters:** TBH "5,000,000" and Mochary "$10,000 / month" use rolling digit reels with motion blur and a lock bloom.

**No captions where a graphic already says the words.**

The full spec is in `Mochary_project_archive\04_Plans_and_notes\Caption_style_lock_flash_bloom_TBH_and_Mochary.md`.

### 4b. Supercell caption lock: "serif glow" (24 Oct 2026, replaces 4a from Supercell onward)

It came from three tests (A editorial serif, B viral sans, C field-notes mono), then A2 serif glow and A3; A2 was locked with his changes.

**Look**
- Instrument Serif Regular, 112 px (auto-shrinks).
- Warm white #FFF9F0. Sentence case.
- **No italics, no outline or border.**
- Bottom placement.

**Animation**
- Each word rises 34 px out of an invisible mask line on its onset, over 0.42 s with a quint ease-out.
- Lines drift up 10 px and fade out in 0.14 s.

**Glow:** the more cinematic glow he asked for:
- soft glow ×0.85
- wide warm halation
- tight bloom
- warm tint
- haze on bright backgrounds

**The haze reads as a soft drop shadow; he wants it kept.** He asked for it back after I removed it once.

**Same animation on every shot, including B-rolls.** He rejected unique per-B-roll animations and masked or behind-subject body captions.

**No commas at line ends**, in the video and the SRT.

The file is `supercell media ip\Caption_style_LOCK_serif_glow.md`.

### 4c. Reels safe zone (from his reference image; enforced from Supercell v12)

On 1080×1920:
- top 250 px unsafe
- bottom 420 px unsafe (y > 1500)
- left 70 px unsafe
- right edge: for y 250–1110, x ≤ 1025; **for y 1110–1500, x ≤ 887** (the action buttons)

Body captions are centred at x 478.5 with a maximum width of about 797 px.

**History:** before v12, 14 Supercell lines reached x 890–929, and he had captions cut off when posting. **Check every caption and graphic against this with an overlay.**

### 4d. Looks

- **Dark, cinematic, editorial.** Deep blacks, warm-white serif, one accent colour.
- **Supercell B-roll world:** chunky Pixar-like 3D (Clash of Clans, Clash Royale, Boom Beach, Hay Day), warm rim light, gold / green / purple / sky blue.
- **Supercell graphics:** "control room at night". Things light up and switch off rather than fly in; slow pushes; Instrument Serif; amber or gold for the things that are alive.
- **Red** is the "killed" accent: crimson duotone and a red X.
- **Halftone** on all B-rolls and graphics, never on the talking head.
- **Paper or sticker cutouts** (white border, paper grain, drop shadow, stop-motion wobble) are a look he likes.
- **No** cartoon or Clash/Lilita fonts in captions or UI ("goes with Supercell vibe but not the video vibe"), no multicolour UI, no cliché B-roll.

### 4e. Sound rules (learned the hard way on Supercell)

**Do**
- clean air whooshes into B-rolls (one per entrance, a whisper swish on inner cuts)
- risers that peak on hits
- booms with long reverb tails
- tactile Foley only where it means something: stamps on the red X's, paper on cutouts, coins on the goblin, a crowd swell on "reward"
- effects about 6 dB under the voice, ducked under speech

**Don't**
- dense clicks, glitches, beeps, data chatter
- tech-heavy palettes
- braams or buzzers (he called one on "they kill it" a buzzer)
- piling SFX onto every cut

**If he gives SFX, or a clip with its own audio, use his untouched.**

---

## 5. TBH reel (done)

Talking head about the TBH app and Nikita Bier ("a gimmick").

**Zoom script** (face-anchored CUT / PUSH / EASE / SNAP):
- snaps on "a single word", "turn cruel" and "a gimmick"
- a punch cut on "best smile"
- motion blur on fast moves

**Built**
- 5M counter with glow
- anonymous textbox
- app blur
- Nikita flash
- Facebook article
- friend map
- halftone texture
- sound mix (v4)

**Captions:** the flash-bloom lock (4a) was born here.

**B-roll:** he picks from Pinterest; Nikita footage from YouTube.

---

## 6. Mochary reel ("script 2", done)

Everything is archived in `script 2\Mochary_project_archive\`. The README there has the full details.

**Script, as spoken:** "Sam Altman once told Reddit's CEO that one coach would add a billion dollars to his company. That coach is Matt Mochary. He's worked with Altman, Brian Armstrong, Vlad Tenev, and his whole playbook is online … charge for the follow-through." About 62 s, 1555 frames.

**Zoom pass**
- snaps on "a billion dollars", "10 grand" and "the marketing"
- punch cuts on "Not the advice", "Those are his buyers" and "Here's the catch"
- cuts at 0:29.9 and 0:52.3 sit on his jump cuts

**Built**
- GFX01 opener (Altman/Huffman cutouts, a "?" silhouette, a $1,000,000,000 counter, the Mochary reveal)
- GFX02 client file (v1/v3/v4)
- B02–B11 procedural B-rolls (10k coins, session card, Friday check-in, couch room, buyer funnel, same-shape cards, 7% batch, gears machine, habit loop, fitness/coach/software)
- B04 calendar, B06 founders carousel v1/v2, B07 YC shorts v1/v2, B08 YC equity/demo day/batch
- C1–C3 coaching footage
- a $10,000/month rolling counter
- halftone texture
- flash-bloom captions
- sound design (`mix_moch.py`)

**Finals:** `Mochary_full_v3_sound.mp4` and `Mochary_full_v3_captions.mp4`, plus the v3 mix and SFX stem.

**SRTs:** `Mochary_captions_onscreen_v3.srt` and `Mochary_transcript_full.srt`, both generated into the archive.

**Opener with the AI cash-room clip**
- His clip: realistic Altman, Huffman-lookalike and Mochary-lookalike in a cash-hoarding scene. Claude declined to generate that face-swap itself and offered anonymous or collage alternatives.
- Claude captioned his clip only with a visible **"AI-GENERATED"** tag. The files are `Mochary_opener_cash_captions.mp4` plus an `_ALPHA.mov` overlay.
- Caption placement:
  - "Sam / Altman" beside his face
  - "Reddit's / CEO" over the dark area
  - a pull-quote with a leader line to Altman: "“one coach would add / a billion / dollars” / to his company"
  - "that coach is", with the name blurred like his face, then "Matt / Mochary" snapping sharp on the reveal
- **His later edit dropped the AI tag.** Claude flagged that it should go back before posting.
- The quote is the voiceover's wording; no verbatim source was found.

---

## 7. Supercell reel (current), full log

### 7a. Script and timings

> Supercell has killed more than 30 of its own games. It's launched five hits. That's the company behind Clash of Clans and Clash Royale. The CEO is Ilkka Paananen. And the wild thing is, some of those games were already out with real users. People were actually playing them. Here's how it works. They launch quietly in a few countries like Canada and Australia. They watch the real numbers, and if a game doesn't hit, they kill it. Spooky Pop went into soft launch December 2014. By February, it was gone. And Paananen says it's not even his call. He said, "it's really the game teams that run the show here, not me." So the global launch isn't a test, it's a reward. And you can steal this. Pick a market where the stakes are lower and launch there first. For a consumer app, that's one country. If you need network effects, like a marketplace, that's one city. What you don't do is launch to everyone and pray.

**Base edit:** his `Supercell_zoom_v2_motionblur_1.mp4`, 1169 frames, 48.757 s.

**Word times**
- "killed" 0.88, "30" 1.36, "games" 2.24
- "five" 4.16
- "Clash" 6.32
- "CEO" 8.16
- "Here's how it works" 14.40
- "Canada" 17.26, "Australia" 17.82
- "kill" 21.18
- "reward" 34.74
- "one country" ≈ 41.3, "one city" 44.51
- black at frame 1139

**Zoom snaps:** "five hits", "kill it", "reward" and "pray". Motion blur on all moves; v3 also had zoom-through transitions.

### 7b. Chronological log (every request and what came of it)

**Pre-production**
1. Zoom passes v1, v2 (motion blur), v3 (zoom-through). The transcript, zoom script and B-roll plan went into `Supercell_broll_plan.md`.
2. Caption tests: A editorial serif, B viral sans, C field-notes mono, then A2 serif glow and A3. **Locked the serif glow**: no italics, no outline, bottom, constant soft glow.
3. Pinterest references for motion graphics went into `motion graphics references\`: 11 directions (soft-launch map, game graveyard, CRT shut-off, live numbers, retro terminal, one city, chess, big number type, game teams, Dec 2014 date stamp) plus YouTube shot references. The direction doc is "Control room at night".
4. Higgsfield prompts:
   - TV wall with the Supercell logo glitching, turning off at 3–4 s (Kling, 9:16, 5 s max)
   - embedding the logo on every TV with a CRT effect
   - a natural glitch shut-off
5. **Supercell-world mood board**: 24 references plus a style lock md, used as the B-roll style lock.
6. A Canada/Australia animation, 9:16.

**B-roll versions**
7. B-roll v1: his B-rolls plus Higgsfield (Kling/Seedance) and my graphics. Rules: no B-roll on top of B-roll, don't fill everything with B-roll. Then captions v1.
8. v2: unique caption animations on B-rolls, masked captions, "the 5 behind the guy", safe space.
9. v3:
   - Fixed abrupt cuts (12 s, 28 s, 32 s) and removed the repeating phone-crowd B-roll.
   - **Stopped using Higgsfield.**
   - Replaced cliché B-rolls (crate opening, network connections) with my own motion graphics.
   - **Reverted** to the talking-head caption animation everywhere and added a more cinematic glow.
   - Org chart: a **moving cutout of Ilkka Paananen** with plain single-tone cells.
   - **Halftone on all B-rolls.**
   - Re-timed captions, which had been late; the words were re-transcribed.
   - Logo animation placeholder; his logo is pending.
10. He asked to open it in the timeline editor. I made the Premiere package (XML plus media B01–B16, a caption overlay MOV, the V1 base and the SRT), saved as `Supercell reel v3.prproj`.

**Captions and first sound passes**
11. v4: **removed commas at line ends**; first SFX pass.
12. Phone preview; the "Here's how it works" animation (playbook, then rocket, then globe, then into the map) → v5.
13. v6:
    - better SFX
    - a new **reward B-roll**: paper cutouts of Ilkka and a goblin (the goblin is ISNet-cut from his goblin B-roll); crowns drop on "reward"; small stars; the old big flashing stars removed
14. v7:
    - the playbook in **serif** instead of the Clash font, with a gold spark instead of the cartoon rocket
    - a **red "killed" treatment only on the fast-cut montage**: crimson duotone, a red X per game, a serif counter 4 → 30+
    - ElevenLabs SFX. The storage domain was blocked, so he allowed it.
    - "No more phone previews; on PC now."

**Sound passes**
15. v7's sound was "very heavy tech, extremely ugly". v8 was a restrained cinematic pass (ElevenLabs credits ran out).
16. **v8_noSFX** delivered (original audio) so he could do the SFX himself.
17. v9 premium pass: he topped up credits, 26 new ElevenLabs sounds, layered, ducked. Accepted.
18. v10: shutter plus photo-flash on CEO clip changes.
19. v11: replaced with **his own SFX** on the CEO cuts (8.51, 9.05, 9.59, 26.74 s); the picture flash kept.

**The axe hook**
20. v12:
    - his **axe clip** (American Psycho shot → Clash barbarian in a raincoat → axe close-up) as the hook, 0–2.33 s
    - dynamic placed captions
    - **all captions moved into the Reels safe zone**
21. v13:
    - removed the **buzzer-like braam** on "they kill it"
    - **used his clip's own audio** for the hook and removed my hook SFX
    - "Supercell" tried behind his head
22. v14: "Supercell" beside his face, with more glow.
23. v15: "Supercell" **bigger, over his chest (option B), a little lower**; shadow removed; "more than 30" removed.
24. v16: **shadow back**; a big **30** on the wall above the axe head.
25. `context.md` and `CLAUDE.md` / `agent.md` written and saved.
26. **v17 (current):** his **second axe clip** ("…Burning_Money_2") swapped in as the hook base, with its own audio. Same cut points, so everything else is identical to v16.

### 7c. Final structure (v17)

Frame ranges are at 23.976 fps.

**0–2.33 s, the hook** (his clip v2 and its audio)
- **0–0.56:** "Supercell" 228 px across his chest, centred at x 520, baseline 1068, with shadow plus warm glow. Rejected before this: the top line, behind the head, beside the face.
- **0.76–1.48:** "has" small, and "**killed**" in red glow with a red underline swipe, top-right in the dark doorway.
- **1.48–2.33:** a big **30** (400 px) rolls up from 0 on the wall above the axe (right edge x 1000, baseline 640). Then "of its own / **games**" lands lower right, inside x 887.

**2.38–3.09 s:** the red "killed" fast cuts, frames 57–73.
- 8 game clips, each with a crimson duotone and a red X (two strokes over two frames).
- The counter climbs 4 → 8 → … → 28 → **30+**, with "games killed".
- The egg shot after it is untouched.

**From 3.1 s onward:** his B-rolls plus my graphics, with halftone and body captions.

| Time | What's on screen |
|---|---|
| 4.9–6.2 | Logo build. **Supercell logo placeholder**; his replacement is pending. |
| 6.2–8.0 / 8.5–10.3 | His B-rolls: Clash art, then Ilkka clips. |
| 8.51 / 9.05 / 9.59 / 26.74 | CEO clip changes: his SFX plus a 4-frame warm photo-flash. |
| 11.4–13.1, 21.6–23.3, 26.7–28.1 | His B-rolls. |
| 14.35–17.12 | Serif playbook ("The *Playbook*": Launch quietly / Watch the numbers / Kill or scale), a gold spark, a dotted night globe with pins on Canada, Australia and NZ, and a "Soft launch" tag. |
| 17.12–18.4 | His map clip, with CANADA / AUSTRALIA Clash-style tags. |
| 18.4–20.9 | Goblin numbers. |
| 24.8–26.7 | Ghost leaves the tombstone. |
| 28.1–29.4 / 31.4–32.6 | Org chart: the Ilkka sticker cutout over plain "Cell" cells, flipping on "not me". |
| 33.9–35.5 | Reward: paper cutouts of Ilkka and a goblin; crowns land on "reward"; gold light; three small stars. |
| 36.7–39.8 / 39.8–41.9 | Flag, then the dive into one country. |
| 41.9–45.2 | City grows. |
| 47.5 | Cut to black. |

### 7d. Sound (v17 = v13 sound, with clip v2 audio)

| Moment | Sound |
|---|---|
| 0–2.33 | His clip's audio only. |
| Fast cuts | A rubber stamp per X, a heartbeat on alternate cuts, a boom on "30+". |
| Logo | Riser, clicks on the rows, boom, flash pop and shimmer on the glint. |
| B-roll entrances | One clean whoosh in, whisper swishes on inner cuts, a soft swish back to camera. |
| Playbook | Title punch, step clicks, a riser on the spark, a soft hit and shimmer on the pin, ticks on the pins, a reverse swell into the map, soft hits under the tags. |
| Goblin | Gold coins. |
| "They kill it" | Boom only (braam removed). |
| Ghost | Drone, slow whoosh, shimmer on "gone". |
| Cutouts | Paper slaps, a riser into "reward", a boom plus a distant crowd roar plus gold shimmer on the crowns. |
| Flag | Hits. |
| Country / city | Risers into "one country" and "one city", accelerating ticks on the city. |
| End | Reverse swell into a final boom over black. |

**Master:** −14 LUFS, TP −1.2, effects about 6 dB under the voice and ducked.

**Version history of the sound and his verdicts:**
- v4 ok
- v6 "gimmicky"
- v7 "ugly, too tech"
- v8 restrained
- v8_noSFX
- v9 premium (accepted)
- v10 / v11 CEO-cut sound (his own)
- v12 my hook SFX (rejected)
- v13+ his clip audio

### 7e. Files in `supercell media ip\`

- **v17**: current.
- v16: v17 with the first axe clip.
- v15 / v14 / v13: hook caption iterations.
- v12: safe zone plus hook.
- v11 / v10 / v9: sound passes.
- v8 and v8_noSFX.
- v7 and v7_picture_oldSFX.
- v4_sfx.
- caption tests and captions v1–v3, zoom v1–v3, brolls v1.

Each recent version has its `.srt`. Mixes and stems: v4, v7, v8, v9, v12, v13, v17.

**Premiere package** (`Premiere project\`, from v3): outdated; rebuild on request.

---

## 8. Hook idea bank (for this and future reels)

The **zone he likes**, set by the Mochary opener, is the **staged editorial satire tableau**:
- one surreal, high-status room shot like a flash-lit magazine cover
- real power players act out the script's metaphor literally
- cuts land on the name drops
- captions sit beside the subjects
- the final beat is a reveal

Ideas pitched for Supercell:
- **Emperor's Arena / Colosseum:** a thumbs down on 30 gladiator games, thumbs up on 5, the arena revealed as Clash Royale.
- **Golden Buzzer:** a talent show with red X's and five golden buzzers.
- **Trophy Lodge:** a Wes Anderson hunting room with 30 mounted game trophies and 5 gold ones.
- **Flatline Ward:** 30 monitors flatlining and 5 heartbeats.
- **Corporate Layoff:** game mascots carrying boxes out of a Helsinki office.
- **Pruning Greenhouse:** cut 30, five grow into trees.
- **Game Graveyard**, **Kill Room** (stamping "KILLED"), **Lights-Out Arcade**, **Tabletop Sweep**.

**He chose:** an American Psycho riff. The axe-holding man becomes a Clash barbarian in a raincoat.

---

## 9. What he likes and dislikes (feedback log)

**Likes**
- dark editorial cinema
- warm-white serif with glow and a soft shadow
- halftone
- slow pushes with snaps and motion blur
- paper and sticker cutouts
- red "killed" accents
- big numbers
- captions placed into hook scenes
- the playbook in serif
- clean premium sound
- fast iteration with stills first

**Dislikes**
- Clash/Lilita fonts over his video
- gimmicky or tech-heavy SFX, buzzers or braams
- cliché B-roll (chests, network lines)
- multicolour cells
- abrupt cuts
- repeated B-roll
- captions outside the safe zone or cut off
- commas at line ends
- masked or behind-head body captions
- text awkwardly over faces
- being sent phone previews when he's on PC
- unrequested extras
- slow turnarounds

**How he gives direction:** voice-typed, short, sometimes with a screenshot and a circle ("add it there"). He means the visible dark or empty area in the screenshot.

---

## 10. Ethics decisions (keep consistent)

**Declined:** photoreal face-swaps of real people (Altman, Huffman, Mochary) into a cash-hoarding or corruption scene.

**Offered instead:**
- anonymous figures
- obvious paper-cutout collages over a generated plate (Higgsfield prompts A/B were given)
- silhouettes

**His own clips of real people:** edit or caption them only with a visible **AI-generated** tag. Remind him if it's dropped.

**No verbatim quotes invented for real people.** Use the voiceover's wording and note that it's paraphrased.

**IP:** I don't draw known characters myself. Compositing his own footage and clips is fine.

---

## 11. Technical pipeline and gotchas

**Code** (Claude's workspace, `scratchpad/sc2` and `sd`; **ephemeral**, so it is summarised here)
- `final9.py`: full Supercell render.
  - captions recentred to the safe zone
  - hook clip and hook captions
  - kill FX
  - CEO flashes
  - map tags
  - halftone
- `hook13`–`hook16.py`: patch only frames 0–56; copy the rest from the previous version. Fast: about 1.5 min.
- Modules:
  - `motion.py`: logo, victory, city
  - `motion2.py`: org chart with the Ilkka cutout from u2net_human_seg
  - `motion3.py`: playbook and globe, using global-land-mask dots
  - `motion4.py`: reward, with the goblin from ISNet plus crowns
  - `killfx.py`: red montage
  - `ov.py`: Clash tags
  - `caps.py`: caption helpers (`put`, `layout`)
  - `../moch/kit.py`: halftone
- Sound: `sd/mix_v17.py` (`place()` framework, reverb tails, ducking).
- Sources: `el2/` (the premium ElevenLabs set), `user_ceo.mp3` (his), `/tmp/jk/clip_audio.wav` (hook clip audio).
- Models: `u2net_human_seg.onnx` and `isnet-general-use.onnx` (rembg GitHub release).
- Transcription: sherpa-onnx Parakeet. Matting: PyMatting and GrabCut are available.

**Delivery to his PC**
1. `zip -0`, then `split -b 24m` into `/mnt/user-data/outputs/<dir>/`.
2. `device_commit_files` into `<project>\_proxy\`, at most 4 parts per call.
3. `device_bash`: `cat` the parts, check the md5, then python `zipfile` extract.

**Gotchas**
- **Committing raw .mp4 parts corrupted the first part. Always zip first and verify the md5 on both sides.**
- Long device copies time out at about 3 min. Split them into smaller commands.
- The bridge can't delete; use a `_to_delete\` folder.

**Phone previews:** 720×1280, CRF 24 (about 14 MB), with a timecode top-left when he's judging timing.
