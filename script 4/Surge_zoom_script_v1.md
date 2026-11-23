# Surge (script 4): zoom pass v1

Source: `Surge_RoughCut_v2_ProRes4444 (1).mov`, 1728×3072, 23.976 fps, 1207 frames (50.34 s).
Output: `Surge_zoom_v1_motionblur.mp4`, 1080×1920, same frame count, his audio untouched.

## Direction (carried over from Supercell, zooms only)
Measured off `Supercell_v17.mp4` with optical flow and face tracking, not guessed:
- **Slow linear push-in** through every shot: about +0.13% scale per frame (≈3% per second). Long shots ease it to 1.0–1.2‰ so nothing goes past 1.36×.
- **Sudden push-in only on key words:** +13% over 7 frames with a hard ease-out (the same curve as Supercell's snaps: 12 / 53 / 34 / 19 / 8 / 2.5 ‰ per frame), starting one frame before the word.
- **Each jump cut resets wider**, so the cut reads as a reframe, never a stutter. Starts alternate between about 1.00× and 1.14×.
- **Face-anchored:** each shot zooms about the median face centre (x ≈ 0.47–0.49, y ≈ 0.40–0.41), so the face holds still while the frame moves in around it.
- **Motion blur:** 180° shutter, with sub-frame samples (up to 32) in proportion to how far the frame edge travels. Snaps get heavy blur, and slow pushes stay crisp because their motion is under a pixel.
- Max zoom is 1.36×, which is still sampled from the 1728 px source with no upscaling.

## Zoom table
| # | Time | Frames | Zoom | Push | Snap | Line |
|---|---|---|---|---|---|---|
| 1 | 0:00.00–0:03.09 | f0–73 | 1.00× → 1.24× | 1.30‰/frame | SNAP +13% on "never" at 0:02.50 (f60) | OpenAI, Google, and Anthropic all buy from a guy you've never heard of. |
| 2 | 0:03.09–0:07.42 | f74–177 | 1.08× → 1.36× | 1.04‰/frame | SNAP +13% on "zero" at 0:06.34 (f152) | His company did $1.2 billion in 2024 with zero investors. |
| 3 | 0:07.42–0:13.35 | f178–319 | 1.00× → 1.36× | 1.30‰/frame | SNAP +13% on "Edwin" at 0:08.26 (f198) | His name is Edwin Chen, and his company, Surge AI, makes the data that those labs use to train their models. |
| 4 | 0:13.35–0:17.48 | f320–418 | 1.08× → 1.36× | 1.09‰/frame | SNAP +13% on "100" at 0:14.51 (f348) | And the wild thing is, it's about 100 people, and he says it's been profitable since day one. |
| 5 | 0:17.48–0:20.44 | f419–489 | 1.00× → 1.24× | 1.30‰/frame | SNAP +13% on "no" at 0:19.39 (f465) | So, how do you sell a billion dollars with no sales? Team. |
| 6 | 0:20.44–0:23.48 | f490–562 | 1.14× → 1.25× | 1.30‰/frame | no snap | Honestly, there are only about a dozen buyers on earth for this. |
| 7 | 0:23.48–0:25.82 | f563–618 | 1.06× → 1.14× | 1.30‰/frame | no snap | And they're all researchers that know each other. |
| 8 | 0:25.82–0:28.82 | f619–690 | 1.06× → 1.16× | 1.30‰/frame | no snap | When one moves to a new lab, they ask for Surge to be there too. |
| 9 | 0:28.82–0:34.66 | f691–830 | 1.00× → 1.35× | 1.30‰/frame | SNAP +13% on "sales" at 0:30.53 (f732) | So his customers are the sales team. If your market is 10 buyers, don't hire 10 salespeople. |
| 10 | 0:34.66–0:38.08 | f831–912 | 1.08× → 1.36× | 1.30‰/frame | SNAP +13% on "fight" at 0:37.33 (f895) | Get so good that people inside those companies fight for you. |
| 11 | 0:38.08–0:39.58 | f913–948 | 1.06× → 1.11× | 1.30‰/frame | no snap | Epic did that with hospitals. |
| 12 | 0:39.58–0:43.84 | f949–1050 | 1.03× → 1.33× | 1.30‰/frame | SNAP +13% on "distribution" at 0:43.08 (f1033) | if you’re selling to a million customers that never talk to each other, you need distribution. |
| 13 | 0:43.84–0:50.34 | f1051–1206 | 1.00× → 1.36× | 1.19‰/frame | SNAP +13% on "$30" at 0:48.67 (f1167) | And now investors want in. Surge has reportedly been in talks to raise at up to a $30 billion valuation. |

Jump cuts were detected at frames 74, 178, 320, 419, 490, 563, 619, 691, 831, 913, 949 and 1051. Two micro-jumps (f603 and f809) are pushed straight through and not treated as cuts.

## Not carried over from Supercell
Captions, mood board, B-roll, graphics and sound are all new for this video.
