import os

# Display
LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 960
SCALE_FACTOR = 1
WINDOW_WIDTH = LOGICAL_WIDTH
WINDOW_HEIGHT = LOGICAL_HEIGHT
FPS = 60

# Character sprite display size (scaled down from 1024x1024)
CHAR_DISPLAY_SIZE = 320  # pixels in logical space

# ─── Light Academia / Scroll Color Palette ───
# Backgrounds: warm parchment tones
COLOR_BG = (245, 235, 220)           # warm parchment
COLOR_BG_ALT = (235, 225, 208)       # slightly darker parchment
COLOR_BG_DARK = (225, 213, 195)      # panel backgrounds

# Text: dark ink tones
COLOR_TEXT = (35, 25, 15)             # dark brown ink
COLOR_TEXT_DIM = (85, 70, 55)         # medium ink
COLOR_TEXT_LIGHT = (120, 105, 85)     # lighter ink

# Accents: warm gold / library tones
COLOR_ACCENT = (140, 90, 30)         # gold / antique brass
COLOR_ACCENT_LIGHT = (175, 135, 70)  # lighter gold
COLOR_ACCENT_DARK = (100, 65, 20)    # deep amber

# Panels: soft cream with subtle borders
COLOR_PANEL_BG = (250, 242, 230)     # light cream
COLOR_PANEL_BORDER = (175, 155, 130) # warm tan border
COLOR_PANEL_HOVER = (255, 248, 238)  # hover highlight

# Buttons: warm toned
COLOR_BUTTON_IDLE = (210, 190, 155)
COLOR_BUTTON_HOVER = (190, 165, 130)
COLOR_BUTTON_PRESSED = (170, 145, 110)
COLOR_BUTTON_TEXT = (35, 25, 15)

# Status colors (muted, academic)
COLOR_ACCEPT = (90, 140, 80)         # muted sage green
COLOR_REJECT = (165, 70, 60)         # muted brick red
COLOR_WAITLIST = (180, 150, 60)      # muted ochre
COLOR_HIGHLIGHT = (100, 150, 120)    # soft teal

# Decorative
COLOR_RULE_LINE = (160, 140, 115)    # horizontal rules
COLOR_SHADOW = (150, 135, 115)       # subtle shadows

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SAVES_DIR = os.path.join(PROJECT_ROOT, "saves")
EXPORTS_DIR = os.path.join(PROJECT_ROOT, "exports")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
SPRITE_DIR = os.path.join(ASSETS_DIR, "sprites")

# Gameplay
STARTING_TOKENS = 5
ACCESSORY_COST = 1
MAX_COLLEGE_APPS = 2
