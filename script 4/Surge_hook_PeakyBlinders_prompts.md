# Surge (script 4): hook prompts, Peaky Blinders direction

Hook = 0:00.00 to 0:03.09 (frames 0 to 73, the jump cut is at f74).
Line: "OpenAI, Google, and Anthropic all buy from a guy you've never heard of."

## Shot timing (locked to his word timings)

| Shot | Time | Frames | Words | What we see |
|---|---|---|---|---|
| 1 | 0.00 to 1.58 s | f0 to f37 | OpenAI (0.00) · Google (0.64) · and Anthropic (0.96) | Over the quiet man's shoulder: a long table stretching away, three bosses waiting |
| 2 | 1.58 to 2.08 s | f38 to f49 | all buy from | Top-down insert: three thick envelopes slide across the wood toward camera |
| 3 | 2.08 to 3.09 s | f50 to f73 | a guy you've **never** (2.56, f61) heard of | The quiet man in the flat cap, face in shadow. Snap zoom on "never" |

Generate each shot as its own 9:16 clip at 5 s. I'll trim them to the frames above, so let each move start slowly and keep the action in the first 2 seconds.

## Why the prompts never say "Peaky Blinders"

If the show is named, video models drift toward the actors' faces. The prompts describe the world instead (1920s Birmingham back room, flat caps, wool coats, haze). Everyone stays anonymous. The three bosses are generic men, and the companies are named only by my captions, not by faces or logos. The quiet man's eyes stay under the brim of his cap.

---

## Shared style block (paste at the end of every prompt)

> 1920s industrial Birmingham, a private back room above a pub, cinematic 35mm film still, single bare tungsten bulb hanging over the table, thick cigarette haze catching the light, deep crushed blacks, warm amber key light with a cold blue rim from a rain-streaked window, wet brick walls, dark wood, heavy wool overcoats, flat caps and waistcoats, shallow depth of field, anamorphic lens, fine film grain, slow and tense, vertical 9:16 composition

**Negative / avoid:** text, letters, logos, subtitles, watermark, modern objects, phones, celebrity likeness, famous actor, cartoon, CGI look, bright lighting, smiling, fast camera shake

---

## Shot 1: the table (0.00 to 1.58 s)

**Image prompt (start frame)**
> Over-the-shoulder shot from behind a man in a dark flat cap and wool coat, his shoulder and cap a dark out-of-focus silhouette filling the bottom of the frame. In front of him a long dark wooden table stretches away into the haze. Three stern men in their fifties wait at the table: one seated on the left side close to camera, one seated on the right side further back, one standing at the far end directly under the hanging bulb. They all look toward camera. Whisky glasses, an ashtray, a ledger on the table. [shared style block]

**Video prompt**
> Very slow dolly forward along the table. The three men stay still and watch, smoke drifts through the bulb light, the bulb sways slightly. No one speaks.

**Composition I need:** left boss in the lower-left third, right boss in the right middle, far boss small and centred near the top third. That leaves dark space beside each for the names.

---

## Shot 2: the envelopes (1.58 to 2.08 s)

**Image prompt (start frame)**
> Top-down close-up of a dark scarred wooden table under a single warm bulb. Three hands in dark coat sleeves each push a thick sealed brown paper envelope across the wood toward the bottom of the frame. Coins of light on the wood, smoke haze. [shared style block]

**Video prompt**
> The three envelopes slide quickly toward camera and stop together at the bottom of the frame. The hands pull back into the darkness. Quick and decisive, then still.

---

## Shot 3: the quiet man (2.08 to 3.09 s)

**Image prompt (start frame)**
> Medium close-up of a quiet young man sitting alone at the near end of the table, dark flat cap pulled low so the brim shadow hides his eyes, only his jaw and mouth lit by the warm bulb from above. Dark wool overcoat with the collar up, three brown envelopes in front of him on the table. Completely calm and unreadable. Background lost in haze and darkness. [shared style block]

**Video prompt**
> Slow push in on the man. He does not move except for one slow breath; smoke drifts across his face. At the end he lifts his chin very slightly, but the eyes stay in shadow.

(The snap on "never" is done in my edit, so keep the camera move in the clip slow.)

---

## Captions I'll place (1080×1920, all inside the Reels safe zone)

| Word(s) | On at | Where | Size |
|---|---|---|---|
| OpenAI | f0 | beside the left boss, lower left (x from 90, baseline about y 1000) | large |
| Google | f15 | beside the right boss, right middle (right edge at x 1000 or less, baseline about y 760) | medium |
| Anthropic | f23 | beside the far boss under the bulb (centred, baseline about y 520) | smaller (sits in the depth) |
| all buy from | f38 | over the dark wood above the envelopes (centred, about y 700) | medium |
| a guy you've | f50 | small, above his cap (about y 430) | small |
| **never** | f61 | huge, across his coat below the jaw (centred x 540, baseline about y 1080), with the snap zoom | about 300 px |
| heard of. | f65 | small, under "never" (centred at x 478, about y 1240, right edge at x 887 or less) | small |

Caption typeface and colour for script 4 aren't locked yet. A new look comes with the new mood board, and I'll show stills before anything is rendered.

## Pinterest / reference searches

- 1920s gangster back room cinematography
- single bulb table smoke film still
- flat cap silhouette chiaroscuro
- over the shoulder long table meeting cinematic
- envelope sliding across table close up
- Birmingham 1920s industrial interior

## What to send back

Drop the three generated clips (or the best take of each) into `script 4`, named roughly shot1 / shot2 / shot3. If a clip has its own sound, say whether you want it kept. I'll then cut them to the frames above, add the placed captions and the snap on "never", and render Surge hook v1 on top of the approved zoom pass.
