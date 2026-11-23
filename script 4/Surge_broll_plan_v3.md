# Surge (script 4): B-roll plan v3, final art direction + the one-shot asset list

Built from both references: the Blackbox film (monochrome machine room) and the Google-story reel (editorial paper collage). Times are from your current cut (`final_video.mp4`).

## Art direction: "Archive meets machine"
Two worlds, cut against each other:
1. **Paper (the human side):** grey or beige textured paper, lots of empty space, small warm-white or black serif type (Instrument Serif), typewriter text typing out, hand-drawn script notes with an arrow ("simple idea"), real archival photos as cutouts with serif name labels, simple diagrams (nodes, bars).
2. **Machine room (the data side):** black, dot-matrix shapes, dithered photos, floating UI panels on a faint grid, thin red HUD tracking boxes, tiny lowercase mono labels.

**Colour rule:** black, white and paper tones. **Red is the one accent** (the HUD lines in the Blackbox film, the full-bleed red card in the Google reel). At most one full-bleed red card in the whole reel.

**Rhythm:** like the Google reel, every line gets its own visual idea, 0.7–2 s each, hard cuts. Every approved zoom snap still lands on your face.

**Keep:** all your rendered B-rolls stay. Epic gets graded to B&W, plus a serif label.

### Pinterest mood board
`editorial paper collage video` · `typewriter text animation paper` · `handwritten annotation arrow design` · `archival photo cutout collage` · `monochrome tech brand film` · `dot matrix particle animation` · `red hud tracking boxes` · `floating ui panels dark grid` · `dithered image black and white` · `grey paper texture scan`

---

## Beat by beat
**[GFX]** I build it. **[YOURS]** already in your cut. The letters (A, B, C…) point to the asset list below.

| Time | Line | Visual | Type |
|---|---|---|---|
| 3.3–4.2 | "His company did" | your face | — |
| 4.2–6.7 | "$1.2 billion in 2024 with zero investors" | your techie montage + a serif **$1,200,000,000** rolling up, mono tag "2024" | YOURS + GFX |
| 8.0–9.3 | "His name is Edwin Chen" | your Edwin footage + serif name label "Edwin Chen" with a thin leader line | YOURS + GFX |
| 9.4–10.7 | "and his company, Surge AI" | Surge logo builds on grey paper, then the website slides up in an old browser window | GFX (B) |
| 10.7–12.8 | "makes the data that those labs use to train their models" | machine room: floating panels of text being scored and corrected, red HUD boxes lock on; the lab logos light up in a row at the end | GFX (B, C) |
| 12.8–13.4 | (your paper diagram) | — | YOURS |
| 14.2–15.5 | "about 100 people" | your depth-map crowd + serif counter "≈100" | YOURS + GFX |
| 15.5–17.6 | "profitable since day one" | paper: typewriter types "profitable since day one", a hand-drawn arrow points to a bar chart that never dips | GFX (H) |
| 19.0–20.5 | "no sales team?" | your B&W office archive | YOURS |
| 21.1–23.7 | "only about a dozen buyers on earth" | machine room: dot-matrix Earth, 12 points light up, each with a red HUD box | GFX (I optional) |
| 23.8–25.8 | "researchers that know each other" | paper collage: conference photos pinned around, joined by hand-drawn lines into one web | GFX (D) |
| 25.8–27.2 | "When one moves to a new lab" | paper cutout: a figure carrying a moving box walks from one lab card to the next | GFX (G) |
| 27.3–29.0 | "they ask for Surge to be there too" | a chat window types "can we get surge here too?", cursor hits send. Anonymous names only, no real lab branding | GFX |
| 29.0–30.3 | "So his customers are" | an org card titled "sales team"; the researcher photos drop into it | GFX (D) |
| 31.5–33.1 | "If your market is 10 buyers" | machine room: 10 cells "buyer_01…10" light up | GFX |
| 33.1–34.9 | "don't hire 10 salespeople" | **the red card**: 10 archival salesman cutouts in a row, struck through one by one | GFX (E) |
| 35.0–37.2 | "people inside those companies fight for you" | archival boardroom, fists and raised hands, dithered | GFX (E) |
| 38.0–39.6 | "Epic did that with hospitals" | your Epic aerial, B&W + serif "Epic" label, quick cut to an archival hospital photo | YOURS + GFX (F) |
| 39.6–42.8 | "selling to a million customers that never talk to each other" | a field of tiny dots, none connected (the opposite of the web at 23.8), serif "1,000,000" | GFX (I optional) |
| 43.4–45.7 | "And now investors want in" | archival trading floor, dithered, red HUD boxes on the hands | GFX (E) |
| 45.8–48.5 | "reportedly … $30 billion valuation" | paper: serif **$30,000,000,000** rolls up, a handwritten note "reportedly" with an arrow | GFX |

**On your face:** 3.3–4.2, 6.7–8.0, 13.4–14.2, 17.7–19.0, 20.5–21.1, 30.3–31.5 (snap "sales"), 37.2–38.0 (snap "fight"), 42.8–43.4 (snap "distribution"), 48.5–end (snap "$30").

---

## The one-shot asset list
Drop everything into `script 4\assets\08_broll_v2\`, one subfolder per letter (already made).

**A_edwin** (optional): any extra real photos of Edwin Chen, any era, for the name label or a cutout. What you've already cut in is enough.

**B_surge** (required):
- the Surge AI logo (PNG or SVG, transparent)
- 3–5 full-page screenshots of surgehq.ai (desktop)
- a 10 s screen recording of the site scrolling slowly

**C_logos** (required): transparent PNG or SVG of OpenAI, Google DeepMind, Anthropic, Meta, Microsoft.

**D_conference** (required): 8–10 photos of AI conferences, stages, poster sessions, research labs, whiteboards. Generic crowds only, no recognisable named researchers.

**E_archival** (required):
- 1–2 B&W boardroom clips (`1960s boardroom footage black and white`)
- 1–2 B&W trading floor clips (`trading floor archival footage`)
- 1 vintage salesman photo, full body (`1950s salesman photo`); I repeat it 10 times
- 1 archival hospital photo (`vintage hospital corridor black and white`)

**F_epic** (optional): the Epic Systems logo, or one more campus photo.

**G_cutouts** (required): one photo of a person carrying a cardboard moving box, full body, side view, any background.

**H_textures** (optional but better): 2–3 high-res paper scans, one grey and one beige (`grey paper texture scan`, `beige paper texture high resolution`). Without them I generate paper.

**I_optional:** a B&W Earth-from-space clip; an aerial crowd clip.

**Fonts:** nothing needed. I use Instrument Serif, IBM Plex Mono, a typewriter face and a free handwritten script for the notes. If you know the handwriting font from the Google reel, tell me and I'll match it.

**Higgsfield:** not needed.

## After B-roll
Captions in the locked Instrument Serif style (no commas at line ends, inside the safe zone), then the sound design pass, then final delivery.
