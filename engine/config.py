"""Shared settings for the reel engine. Values come from design_system/CAPTION_STYLE_LOCK.md and FIRST_CUT_LOCK.md.
Change a lock there first, then mirror it here."""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, 'fonts')
FFMPEG_DIR = r'C:\Users\chord\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.1-full_build\bin'
FFMPEG = os.path.join(FFMPEG_DIR, 'ffmpeg.exe')
FFPROBE = os.path.join(FFMPEG_DIR, 'ffprobe.exe')

W, H = 1080, 1920

# Reels safe zone
SAFE = dict(left=70, top=250, bottom=1500, right_upper=1025, right_lower=887, split_y=1110)

# Fonts. Brand: GT Standard (primary) + HW Cigars (accent). Stand-ins until the real files are installed.
# Each entry: (file, variation axes in the font's own axis order)
FONT_PRIMARY = ('Inter-VF.ttf', [32, 500])            # Inter: [opsz, wght] -> Medium
FONT_ACCENT_ITALIC = ('Newsreader-Italic-VF.ttf', [400, 72])  # Newsreader: [wght, opsz]
FONT_NUMBER = ('Newsreader-VF.ttf', [400, 72])

# Caption lock v2 (23 Nov 2026)
SIZE = {'p': 84, 'k': 92, 'n': 132}
TRACK = {'p': -0.02, 'k': -0.02, 'n': -0.03}          # em
LINE_SPACING = 1.12                                    # x biggest word on the line
LEAD = 0.10                                            # captions lead the spoken word by this many seconds
ANIM_FPS = 30                                          # animation steps are defined at 30 fps (reference)
KEY_STEPS = [25, 25, 55, 75, 100]                      # option A reference sweep, % of word width per 30fps frame
NUM_ROLL = 16                                          # 30fps frames for the first digit; +4 per extra digit
TEXT_COLOR = (255, 255, 255)
SHADOW = dict(dy=0.03, blur=0.15, alpha=0.35)          # em-relative

# Placement
TH_ANCHOR = (90, 1160)        # talking head: left x, top y (chin ~1050, mic from x 620 / y 1040)
CENTER_Y = 1000               # B-roll default block centre (~52%)
UP_Y = 620                    # B-roll when the centre is busy
GLOW_BUDGET_PER_MIN = 7       # about 6 per 50-60 s reel
