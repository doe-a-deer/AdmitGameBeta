import pathlib

# Display — larger to fit the 1024x1024 character art
LOGICAL_WIDTH = 640
LOGICAL_HEIGHT = 480
SCALE_FACTOR = 2
WINDOW_WIDTH = LOGICAL_WIDTH * SCALE_FACTOR
WINDOW_HEIGHT = LOGICAL_HEIGHT * SCALE_FACTOR
FPS = 60

# Character sprite display size (scaled down from 1024x1024)
CHAR_DISPLAY_SIZE = 160  # pixels in logical space

# ─── Light Academia / Scroll Color Palette ───
# Backgrounds: warm parchment tones
COLOR_BG = (245, 235, 220)           # warm parchment
COLOR_BG_ALT = (235, 225, 208)       # slightly darker parchment
COLOR_BG_DARK = (225, 213, 195)      # panel backgrounds

# Text: dark ink tones
COLOR_TEXT = (55, 40, 30)             # dark brown ink
COLOR_TEXT_DIM = (130, 115, 95)       # faded ink
COLOR_TEXT_LIGHT = (170, 155, 135)    # very faded

# Accents: warm gold / library tones
COLOR_ACCENT = (160, 110, 50)        # gold / antique brass
COLOR_ACCENT_LIGHT = (195, 155, 90)  # lighter gold
COLOR_ACCENT_DARK = (120, 80, 35)    # deep amber

# Panels: soft cream with subtle borders
COLOR_PANEL_BG = (250, 242, 230)     # light cream
COLOR_PANEL_BORDER = (200, 185, 160) # warm tan border
COLOR_PANEL_HOVER = (255, 248, 238)  # hover highlight

# Buttons: warm toned
COLOR_BUTTON_IDLE = (220, 200, 170)
COLOR_BUTTON_HOVER = (200, 175, 140)
COLOR_BUTTON_PRESSED = (180, 155, 120)
COLOR_BUTTON_TEXT = (55, 40, 30)

# Status colors (muted, academic)
COLOR_ACCEPT = (90, 140, 80)         # muted sage green
COLOR_REJECT = (165, 70, 60)         # muted brick red
COLOR_WAITLIST = (180, 150, 60)      # muted ochre
COLOR_HIGHLIGHT = (100, 150, 120)    # soft teal

# Decorative
COLOR_RULE_LINE = (190, 175, 155)    # horizontal rules
COLOR_SHADOW = (180, 170, 155)       # subtle shadows

# Paths
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SAVES_DIR = PROJECT_ROOT / "saves"
EXPORTS_DIR = PROJECT_ROOT / "exports"
FONT_DIR = ASSETS_DIR / "fonts"
SPRITE_DIR = ASSETS_DIR / "sprites"

# Gameplay
STARTING_TOKENS = 5
ACCESSORY_COST = 1
MAX_COLLEGE_APPS = 2
