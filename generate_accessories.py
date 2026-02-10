#!/usr/bin/env python3
"""
Generate pixel art accessory sprites for the AdmitGame.
Produces 33 PNG files (9 standalone + 24 body-fitted with species variants).

All sprites use RGBA mode with transparent backgrounds.
Body-fitted items match character canvas sizes exactly.
Standalone items are compact sprites.
"""

from PIL import Image, ImageDraw
import os

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = "/Users/lucazislin/Desktop/AdmitGame/assets/sprites/accessories"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Pixel block size (approx game-pixel) ──────────────────────────────────────
PX = 12

# ── Character definitions ─────────────────────────────────────────────────────
# Based on actual pixel-by-pixel analysis of the base sprites.
#
# Cat (365x587):
#   Head takes up y=0..~355. Body from neck_y=356 down.
#   Upper torso (y356-375): x=[116,236], ~120px wide, center=176
#   Arms extend out y376-466: total width [66,364] but core torso is [130,225]
#   The cat's tail appears as a separate span on right side y460-520 around x=285-325
#   Legs clearly split at y=508: left=[117,170], right=[181,234]
#   Feet at y=548: left=[85,169], right=[182,269]
#
# Dog (447x548):
#   Head takes up y=0..~309. Body from neck_y=310 down.
#   Upper torso (y310-340): x=[159,280], ~120px wide, center=222
#   With arms (y340-415): [115,329] w=215
#   Hips narrow (y428-454): [151,291] w=141
#   Legs (y456-507): [165,279] w=115, never visually separate
#   Feet (y508-548): [131,313] w=183
#
# Fox (522x609):
#   Head takes up y=0..~367. Body from neck_y=368 down.
#   Upper torso (y368-378): x=[251,370], center=310
#   With tail (y383+): left side extends to x=1 (big tail+arm region)
#   Core body excluding tail: roughly x=[250,405]
#   Legs (y490-538): one block [37,374] includes tail
#   Legs split at ~y=540: body parts [48,302] and [313,374]
#   Feet (y=584+): left=[227,302], right=[313,390]
#
CHARS = {
    "cat": {
        "canvas": (365, 587),
        "eye_cx": 176, "eye_cy": 222, "neck_y": 356,
        "body": {
            # Torso region
            "torso_top_y": 356,
            "torso_core_x": (116, 236),     # upper torso without arms
            "torso_arm_y": 376,              # where arms/wider body begins
            "torso_with_arms_x": (66, 364),  # widest extent with arms+tail
            "core_body_x": (103, 250),       # core body inside the arms
            # Waist / hip transition
            "waist_y": 466,
            # Legs
            "upper_leg_x": (103, 325),       # before split, includes tail span
            "leg_split_y": 508,              # where legs visibly separate
            "left_leg_x": (117, 170),
            "right_leg_x": (181, 234),
            # Feet
            "feet_y": 548,
            "left_foot_x": (85, 169),
            "right_foot_x": (182, 269),
            "bottom_y": 587,
        },
    },
    "dog": {
        "canvas": (447, 548),
        "eye_cx": 227, "eye_cy": 190, "neck_y": 310,
        "body": {
            "torso_top_y": 310,
            "torso_core_x": (159, 280),
            "torso_arm_y": 340,
            "torso_with_arms_x": (115, 329),
            "core_body_x": (151, 291),
            "waist_y": 428,
            "upper_leg_x": (151, 291),
            "leg_split_y": 456,             # narrows but doesn't fully split
            "left_leg_x": (165, 215),       # approximate left half
            "right_leg_x": (230, 279),      # approximate right half
            "feet_y": 508,
            "left_foot_x": (131, 215),
            "right_foot_x": (230, 313),
            "bottom_y": 548,
        },
    },
    "fox": {
        "canvas": (522, 609),
        "eye_cx": 307, "eye_cy": 235, "neck_y": 368,
        "body": {
            "torso_top_y": 368,
            "torso_core_x": (251, 370),
            "torso_arm_y": 383,
            "torso_with_arms_x": (25, 405),  # includes tail on left
            "core_body_x": (250, 405),        # body excluding tail
            "waist_y": 490,
            "upper_leg_x": (227, 390),
            "leg_split_y": 540,
            "left_leg_x": (227, 302),
            "right_leg_x": (313, 374),
            "feet_y": 584,
            "left_foot_x": (227, 302),
            "right_foot_x": (313, 390),
            "bottom_y": 609,
        },
    },
}

# ── Helper drawing functions ──────────────────────────────────────────────────

def px_rect(draw, x, y, w, h, color):
    """Draw a rectangle at actual pixel coordinates. Skips if w or h <= 0."""
    if w <= 0 or h <= 0:
        return
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


# ══════════════════════════════════════════════════════════════════════════════
# STANDALONE ITEMS
# ══════════════════════════════════════════════════════════════════════════════

def make_hat_graduation():
    """Mortarboard graduation cap - dark navy square top with gold tassel."""
    w, h = 80, 55
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    navy_dark = (20, 25, 50, 255)
    navy_mid = (30, 35, 65, 255)
    navy_light = (45, 50, 80, 255)
    gold = (218, 175, 50, 255)
    gold_dark = (180, 140, 30, 255)
    black = (15, 15, 20, 255)

    # Flat board
    board_y = 8
    px_rect(d, 4, board_y, 72, 10, navy_dark)
    px_rect(d, 8, board_y + 2, 64, 6, navy_mid)
    px_rect(d, 12, board_y + 2, 56, 3, navy_light)

    # Cap base (skull cap)
    cap_top = board_y + 10
    px_rect(d, 18, cap_top, 44, 10, navy_dark)
    px_rect(d, 14, cap_top, 52, 6, navy_dark)
    px_rect(d, 22, cap_top, 36, 14, navy_mid)
    px_rect(d, 20, cap_top + 10, 40, 4, navy_dark)
    px_rect(d, 26, cap_top + 14, 28, 3, navy_dark)

    # Button on top center
    px_rect(d, 36, board_y - 2, 8, 4, black)

    # Tassel string from center to left
    tassel_x = 12
    px_rect(d, 28, board_y, 4, 3, gold_dark)
    px_rect(d, 20, board_y + 2, 12, 3, gold_dark)
    px_rect(d, tassel_x, board_y + 4, 10, 3, gold_dark)
    # Tassel hang
    px_rect(d, tassel_x, board_y + 6, 4, 20, gold_dark)
    px_rect(d, tassel_x + 1, board_y + 7, 3, 18, gold)
    # Tassel end (bushy)
    px_rect(d, tassel_x - 2, board_y + 25, 8, 10, gold)
    px_rect(d, tassel_x - 1, board_y + 26, 7, 8, gold_dark)
    px_rect(d, tassel_x, board_y + 27, 5, 6, gold)
    # Tassel fringe
    px_rect(d, tassel_x - 3, board_y + 34, 10, 4, gold)
    px_rect(d, tassel_x - 2, board_y + 37, 8, 3, gold_dark)

    return img


def make_hat_cap():
    """Baseball cap - gray with blue brim, curved shape."""
    w, h = 75, 45
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    gray_light = (190, 195, 200, 255)
    gray_mid = (155, 160, 165, 255)
    gray_dark = (120, 125, 130, 255)
    blue_brim = (55, 80, 140, 255)
    blue_brim_light = (70, 100, 165, 255)
    blue_brim_dark = (40, 60, 110, 255)

    # Cap dome
    px_rect(d, 22, 0, 30, 5, gray_mid)
    px_rect(d, 16, 4, 42, 5, gray_mid)
    px_rect(d, 12, 8, 50, 6, gray_mid)
    px_rect(d, 10, 13, 54, 6, gray_dark)
    px_rect(d, 10, 18, 54, 6, gray_dark)
    # Highlight
    px_rect(d, 24, 2, 24, 3, gray_light)
    px_rect(d, 18, 5, 34, 4, gray_light)
    px_rect(d, 14, 9, 40, 4, gray_light)
    # Panel seam
    px_rect(d, 36, 1, 2, 22, gray_dark)
    # Button on top
    px_rect(d, 34, 0, 6, 3, gray_dark)

    # Brim
    brim_y = 24
    px_rect(d, 8, brim_y, 60, 4, blue_brim)
    px_rect(d, 14, brim_y + 4, 55, 4, blue_brim)
    px_rect(d, 20, brim_y + 8, 48, 4, blue_brim)
    px_rect(d, 28, brim_y + 12, 36, 3, blue_brim_dark)
    px_rect(d, 10, brim_y, 56, 2, blue_brim_light)
    px_rect(d, 10, brim_y + 3, 58, 2, blue_brim_dark)

    return img


def make_hat_beanie():
    """Slouchy beanie - dark charcoal, ribbed texture."""
    w, h = 70, 50
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    char_dark = (40, 40, 45, 255)
    char_mid = (55, 55, 60, 255)
    char_light = (70, 70, 78, 255)
    char_highlight = (85, 85, 95, 255)

    # Top pom/gather (slightly right for slouch)
    px_rect(d, 38, 0, 8, 4, char_mid)
    px_rect(d, 36, 3, 12, 3, char_dark)
    # Upper dome
    px_rect(d, 28, 5, 22, 5, char_mid)
    px_rect(d, 20, 9, 32, 5, char_mid)
    px_rect(d, 14, 13, 40, 5, char_mid)
    px_rect(d, 10, 17, 48, 5, char_dark)
    px_rect(d, 8, 21, 52, 5, char_dark)
    px_rect(d, 8, 25, 52, 5, char_dark)
    # Ribbed band
    for i in range(5):
        y = 30 + i * 4
        px_rect(d, 6, y, 56, 4, char_dark if i % 2 == 0 else char_mid)
    # Ribbing texture lines
    for x_off in range(0, 56, 6):
        for i in range(5):
            y = 30 + i * 4
            px_rect(d, 6 + x_off, y, 2, 4, char_light if i % 2 == 0 else char_dark)
    # Slouch highlight
    px_rect(d, 30, 6, 16, 3, char_highlight)
    px_rect(d, 22, 10, 24, 3, char_highlight)
    px_rect(d, 16, 14, 32, 3, char_light)
    # Shadow on left
    px_rect(d, 8, 22, 10, 8, char_dark)

    return img


def make_glasses_wire():
    """Round gold wire-frame glasses."""
    w, h = 70, 24
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    gold = (195, 165, 55, 255)
    gold_light = (220, 190, 80, 255)
    gold_dark = (160, 130, 40, 255)

    cx1, cx2 = 18, 52
    # Left lens (wire circle outline)
    px_rect(d, cx1 - 8, 2, 16, 2, gold)
    px_rect(d, cx1 - 10, 4, 2, 2, gold)
    px_rect(d, cx1 + 8, 4, 2, 2, gold)
    px_rect(d, cx1 - 11, 6, 2, 10, gold)
    px_rect(d, cx1 + 9, 6, 2, 10, gold)
    px_rect(d, cx1 - 10, 16, 2, 2, gold)
    px_rect(d, cx1 + 8, 16, 2, 2, gold)
    px_rect(d, cx1 - 8, 18, 16, 2, gold)
    # Right lens
    px_rect(d, cx2 - 8, 2, 16, 2, gold)
    px_rect(d, cx2 - 10, 4, 2, 2, gold)
    px_rect(d, cx2 + 8, 4, 2, 2, gold)
    px_rect(d, cx2 - 11, 6, 2, 10, gold)
    px_rect(d, cx2 + 9, 6, 2, 10, gold)
    px_rect(d, cx2 - 10, 16, 2, 2, gold)
    px_rect(d, cx2 + 8, 16, 2, 2, gold)
    px_rect(d, cx2 - 8, 18, 16, 2, gold)
    # Bridge
    px_rect(d, cx1 + 9, 8, cx2 - cx1 - 18, 2, gold_dark)
    # Highlight
    px_rect(d, cx1 - 6, 2, 12, 1, gold_light)
    px_rect(d, cx2 - 6, 2, 12, 1, gold_light)
    # Temple arms
    px_rect(d, 0, 8, 7, 2, gold_dark)
    px_rect(d, 63, 8, 7, 2, gold_dark)

    return img


def make_glasses_rect():
    """Rectangular frames - dark gray, professional."""
    w, h = 72, 22
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    frame = (50, 50, 55, 255)
    frame_light = (70, 70, 78, 255)
    lens = (180, 200, 220, 80)

    px_rect(d, 4, 2, 26, 16, frame)
    px_rect(d, 7, 5, 20, 10, lens)
    px_rect(d, 5, 2, 24, 2, frame_light)
    px_rect(d, 42, 2, 26, 16, frame)
    px_rect(d, 45, 5, 20, 10, lens)
    px_rect(d, 43, 2, 24, 2, frame_light)
    px_rect(d, 30, 6, 12, 3, frame)
    px_rect(d, 0, 6, 5, 3, frame)
    px_rect(d, 67, 6, 5, 3, frame)

    return img


def make_glasses_dark():
    """Dark sunglasses - solid dark lenses, slightly larger."""
    w, h = 78, 26
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    frame = (25, 25, 30, 255)
    lens_dark = (15, 15, 20, 255)
    lens_mid = (30, 30, 40, 255)
    highlight = (60, 60, 80, 255)

    # Left lens
    px_rect(d, 4, 3, 28, 18, frame)
    px_rect(d, 2, 5, 32, 14, frame)
    px_rect(d, 6, 5, 24, 14, lens_dark)
    px_rect(d, 4, 7, 28, 10, lens_dark)
    px_rect(d, 8, 6, 8, 3, highlight)
    px_rect(d, 10, 9, 4, 2, lens_mid)
    # Right lens
    px_rect(d, 46, 3, 28, 18, frame)
    px_rect(d, 44, 5, 32, 14, frame)
    px_rect(d, 48, 5, 24, 14, lens_dark)
    px_rect(d, 46, 7, 28, 10, lens_dark)
    px_rect(d, 50, 6, 8, 3, highlight)
    px_rect(d, 52, 9, 4, 2, lens_mid)
    # Bridge + arms
    px_rect(d, 32, 8, 14, 4, frame)
    px_rect(d, 0, 8, 4, 3, frame)
    px_rect(d, 74, 8, 4, 3, frame)

    return img


def make_neck_medallion():
    """Gold chain with medallion pendant."""
    w, h = 60, 45
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    gold = (218, 175, 50, 255)
    gold_dark = (170, 130, 30, 255)
    gold_light = (240, 200, 80, 255)
    chain = (185, 150, 40, 255)

    # Chain V-shape
    for i in range(8):
        px_rect(d, 6 + i * 2, 0 + i * 2, 4, 3, chain)
        px_rect(d, 50 - i * 2, 0 + i * 2, 4, 3, chain)
    for i in range(0, 8, 2):
        px_rect(d, 6 + i * 2, 0 + i * 2, 4, 3, gold_light)
        px_rect(d, 50 - i * 2, 0 + i * 2, 4, 3, gold_light)

    # Medallion
    medal_cx, medal_cy = 30, 30
    px_rect(d, medal_cx - 9, medal_cy - 6, 18, 2, gold_dark)
    px_rect(d, medal_cx - 11, medal_cy - 4, 22, 2, gold_dark)
    px_rect(d, medal_cx - 12, medal_cy - 2, 24, 10, gold_dark)
    px_rect(d, medal_cx - 11, medal_cy + 8, 22, 2, gold_dark)
    px_rect(d, medal_cx - 9, medal_cy + 10, 18, 2, gold_dark)
    px_rect(d, medal_cx - 8, medal_cy - 4, 16, 2, gold)
    px_rect(d, medal_cx - 10, medal_cy - 2, 20, 8, gold)
    px_rect(d, medal_cx - 8, medal_cy + 6, 16, 2, gold)
    # Star design
    px_rect(d, medal_cx - 3, medal_cy - 1, 6, 6, gold_light)
    px_rect(d, medal_cx - 1, medal_cy - 3, 2, 10, gold_light)
    px_rect(d, medal_cx - 5, medal_cy + 1, 10, 2, gold_light)
    # Chain connection
    px_rect(d, medal_cx - 2, medal_cy - 9, 4, 4, gold_dark)

    return img


def make_neck_bowtie():
    """Classic bowtie - navy blue, butterfly shape."""
    w, h = 56, 30
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    navy = (30, 40, 90, 255)
    navy_light = (45, 55, 115, 255)
    navy_dark = (20, 25, 65, 255)

    # Left wing
    px_rect(d, 0, 4, 8, 20, navy)
    px_rect(d, 8, 2, 6, 24, navy)
    px_rect(d, 14, 4, 6, 20, navy_light)
    px_rect(d, 20, 6, 4, 16, navy)
    px_rect(d, 2, 6, 6, 4, navy_light)
    px_rect(d, 2, 18, 8, 4, navy_dark)
    # Right wing
    px_rect(d, 48, 4, 8, 20, navy)
    px_rect(d, 42, 2, 6, 24, navy)
    px_rect(d, 36, 4, 6, 20, navy_light)
    px_rect(d, 32, 6, 4, 16, navy)
    px_rect(d, 48, 6, 6, 4, navy_light)
    px_rect(d, 46, 18, 8, 4, navy_dark)
    # Center knot
    px_rect(d, 24, 8, 8, 12, navy_dark)
    px_rect(d, 25, 9, 6, 10, navy_dark)
    px_rect(d, 26, 10, 4, 3, navy)

    return img


def make_neck_pin():
    """Safety pin - silver/gray, angled, punk style."""
    w, h = 45, 35
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    silver = (180, 185, 190, 255)
    silver_light = (210, 215, 220, 255)
    silver_dark = (140, 145, 150, 255)
    pin_tip = (160, 165, 170, 255)

    # Top bar (clasp)
    px_rect(d, 8, 4, 28, 3, silver)
    px_rect(d, 10, 4, 24, 2, silver_light)
    # Right curve (hinge)
    px_rect(d, 34, 4, 3, 4, silver_dark)
    px_rect(d, 36, 7, 3, 4, silver_dark)
    px_rect(d, 34, 10, 3, 4, silver)
    # Bottom bar
    px_rect(d, 8, 13, 28, 3, silver)
    px_rect(d, 10, 13, 24, 2, silver_dark)
    # Left clasp
    px_rect(d, 4, 3, 6, 5, silver_dark)
    px_rect(d, 5, 4, 4, 3, silver)
    # Pin point extending down
    px_rect(d, 4, 13, 3, 8, silver)
    px_rect(d, 2, 20, 3, 6, silver_dark)
    px_rect(d, 1, 25, 3, 4, pin_tip)
    px_rect(d, 2, 28, 2, 3, silver_dark)
    # Clasp head detail
    px_rect(d, 3, 7, 6, 3, silver_light)
    # Highlight
    px_rect(d, 12, 4, 18, 1, silver_light)

    return img


# ══════════════════════════════════════════════════════════════════════════════
# BODY-FITTED ITEMS (tops and bottoms)
# ══════════════════════════════════════════════════════════════════════════════

def draw_top_blazer(img, char_name, char_data):
    """Crimson blazer with gold buttons, V-neck collar, structured shoulders."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    crimson = (160, 30, 40, 255)
    crimson_light = (185, 45, 55, 255)
    crimson_dark = (120, 20, 30, 255)
    crimson_shadow = (95, 15, 22, 255)
    gold_btn = (218, 175, 50, 255)
    gold_btn_hi = (240, 200, 80, 255)
    lapel = (140, 25, 35, 255)
    white_shirt = (230, 230, 235, 255)

    cx = char_data["eye_cx"]
    neck_y = b["torso_top_y"]
    core_l, core_r = b["torso_core_x"]
    arm_l, arm_r = b["torso_with_arms_x"]
    waist_y = b["waist_y"]
    arm_start = b["torso_arm_y"]

    # For fox, avoid drawing over tail area - restrict left boundary
    if char_name == "fox":
        arm_l = max(arm_l, b["core_body_x"][0])

    torso_w = core_r - core_l
    collar_h = arm_start - neck_y
    full_w = arm_r - arm_l
    arm_h = waist_y - arm_start

    # Upper torso (collar to arm start)
    px_rect(d, core_l, neck_y, torso_w, collar_h, crimson)
    px_rect(d, core_l, neck_y, torso_w, max(collar_h // 3, PX), crimson_light)

    # Main body + arms
    px_rect(d, arm_l, arm_start, full_w, arm_h, crimson)

    # Structured shoulders
    px_rect(d, arm_l - PX, arm_start, full_w + PX * 2, min(PX * 2, arm_h), crimson_light)

    # Arm shading (darker outer edges)
    arm_shade_w = max((core_l - arm_l) // 2, PX)
    px_rect(d, arm_l, arm_start + PX, arm_shade_w, max(1, arm_h - PX), crimson_dark)
    px_rect(d, arm_r - arm_shade_w, arm_start + PX, arm_shade_w, max(1, arm_h - PX), crimson_dark)

    # Shadow under shoulders
    px_rect(d, arm_l, arm_start + min(PX * 2, arm_h - 1), full_w, min(PX, arm_h // 3), crimson_shadow)

    # V-neck opening (white shirt underneath)
    vneck_w = max(torso_w // 4, 10)
    vneck_depth = min(collar_h + arm_h // 3, waist_y - neck_y - PX * 2)
    for i in range(max(1, vneck_depth // PX)):
        vw = max(2, vneck_w - i * 2)
        vx = cx - vw // 2
        vy = neck_y + i * PX
        if vy < waist_y:
            px_rect(d, vx, vy, vw, PX, white_shirt)

    # Lapels
    lapel_w = max(PX, vneck_w // 2)
    for i in range(min(vneck_depth // PX, 6)):
        vw = max(2, vneck_w - i * 2)
        vx = cx - vw // 2
        vy = neck_y + i * PX
        if vy < waist_y:
            px_rect(d, vx - lapel_w, vy, lapel_w, PX, lapel)
            px_rect(d, vx + vw, vy, lapel_w, PX, lapel)

    # Gold buttons
    btn_x = cx - 3
    btn_start_y = neck_y + vneck_depth + PX
    btn_spacing = max(PX * 2, (waist_y - btn_start_y) // 3)
    for i in range(2):
        by = btn_start_y + btn_spacing * i
        if btn_start_y < waist_y and by < waist_y - PX:
            px_rect(d, btn_x, by, 6, 6, gold_btn)
            px_rect(d, btn_x + 1, by + 1, 3, 2, gold_btn_hi)

    # Bottom edge
    px_rect(d, arm_l + arm_shade_w, waist_y - PX, full_w - arm_shade_w * 2, PX, crimson_dark)

    # Side seam lines
    px_rect(d, core_l + PX, arm_start + PX * 3, 2, max(1, arm_h - PX * 4), crimson_shadow)
    px_rect(d, core_r - PX - 2, arm_start + PX * 3, 2, max(1, arm_h - PX * 4), crimson_shadow)


def draw_top_hoodie(img, char_name, char_data):
    """Gray hoodie with hood behind neck and kangaroo pocket."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    gray = (145, 150, 155, 255)
    gray_light = (170, 175, 180, 255)
    gray_dark = (115, 120, 125, 255)
    gray_shadow = (95, 98, 102, 255)
    pocket = (125, 130, 135, 255)
    string_color = (200, 205, 210, 255)

    cx = char_data["eye_cx"]
    neck_y = b["torso_top_y"]
    core_l, core_r = b["torso_core_x"]
    arm_l, arm_r = b["torso_with_arms_x"]
    waist_y = b["waist_y"]
    arm_start = b["torso_arm_y"]

    if char_name == "fox":
        arm_l = max(arm_l, b["core_body_x"][0])

    torso_w = core_r - core_l
    collar_h = arm_start - neck_y
    full_w = arm_r - arm_l
    arm_h = waist_y - arm_start

    # Hood (peeks behind head)
    hood_w = torso_w + PX * 4
    hood_h = PX * 3
    hood_x = cx - hood_w // 2
    hood_y = neck_y - hood_h
    px_rect(d, hood_x, hood_y, hood_w, hood_h, gray_dark)
    px_rect(d, hood_x + PX, hood_y, hood_w - PX * 2, PX, gray)
    px_rect(d, hood_x + PX * 2, hood_y - PX, hood_w - PX * 4, PX, gray_dark)

    # Upper torso
    px_rect(d, core_l, neck_y, torso_w, collar_h, gray)

    # Round collar
    collar_w = max(torso_w // 3, 10)
    collar_x = cx - collar_w // 2
    px_rect(d, collar_x, neck_y, collar_w, min(PX * 2, collar_h), gray_dark)
    px_rect(d, collar_x + 2, neck_y + 2, collar_w - 4, min(PX, collar_h - 2), gray_shadow)

    # Main body + arms
    px_rect(d, arm_l, arm_start, full_w, arm_h, gray)
    px_rect(d, arm_l, arm_start, full_w, PX, gray_light)

    # Arm shading
    arm_shade_w = max((core_l - arm_l) // 2, PX)
    px_rect(d, arm_l, arm_start + PX, arm_shade_w, max(1, arm_h - PX), gray_dark)
    px_rect(d, arm_r - arm_shade_w, arm_start + PX, arm_shade_w, max(1, arm_h - PX), gray_dark)

    # Center seam
    seam_h = max(1, waist_y - neck_y - PX * 3)
    px_rect(d, cx - 1, neck_y + PX * 2, 2, seam_h, gray_shadow)

    # Kangaroo pocket
    pocket_w = max(torso_w * 2 // 3, 20)
    pocket_h = max(arm_h // 3, PX * 2)
    pocket_x = cx - pocket_w // 2
    pocket_y = waist_y - pocket_h - PX * 2
    if pocket_y > arm_start + PX * 2:
        px_rect(d, pocket_x, pocket_y, pocket_w, pocket_h, pocket)
        px_rect(d, cx - pocket_w // 4, pocket_y, pocket_w // 2, 2, gray_shadow)
        px_rect(d, pocket_x, pocket_y, pocket_w, 2, gray_shadow)
        px_rect(d, pocket_x, pocket_y + pocket_h - 2, pocket_w, 2, gray_shadow)

    # Drawstrings
    string_len = min(collar_h + PX * 2, waist_y - neck_y - PX)
    px_rect(d, cx - PX, neck_y + PX, 2, string_len, string_color)
    px_rect(d, cx + PX - 2, neck_y + PX, 2, string_len, string_color)
    px_rect(d, cx - PX - 1, neck_y + PX + string_len, 4, 3, string_color)
    px_rect(d, cx + PX - 3, neck_y + PX + string_len, 4, 3, string_color)

    # Bottom hem
    px_rect(d, arm_l + arm_shade_w, waist_y - PX, full_w - arm_shade_w * 2, PX, gray_dark)
    px_rect(d, arm_l, waist_y - PX * 2, arm_shade_w + PX, PX, gray_dark)
    px_rect(d, arm_r - arm_shade_w - PX, waist_y - PX * 2, arm_shade_w + PX, PX, gray_dark)


def draw_top_band(img, char_name, char_data):
    """Black band tee - simple dark t-shirt with small red design in center."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    black = (25, 25, 30, 255)
    black_light = (40, 40, 48, 255)
    black_dark = (15, 15, 18, 255)
    red_design = (180, 35, 35, 255)
    red_dark = (140, 25, 25, 255)

    cx = char_data["eye_cx"]
    neck_y = b["torso_top_y"]
    core_l, core_r = b["torso_core_x"]
    arm_l, arm_r = b["torso_with_arms_x"]
    waist_y = b["waist_y"]
    arm_start = b["torso_arm_y"]

    if char_name == "fox":
        arm_l = max(arm_l, b["core_body_x"][0])

    torso_w = core_r - core_l
    collar_h = arm_start - neck_y
    full_w = arm_r - arm_l
    arm_h = waist_y - arm_start

    # Upper torso
    px_rect(d, core_l, neck_y, torso_w, collar_h, black)

    # Crew neck
    neck_w = max(torso_w // 3, 10)
    neck_x = cx - neck_w // 2
    px_rect(d, neck_x, neck_y, neck_w, PX, black_dark)

    # Full body with sleeves
    px_rect(d, arm_l, arm_start, full_w, arm_h, black)

    # Short sleeves (only top 1/3 of arm area)
    sleeve_h = max(arm_h // 3, PX)
    arm_shade_w = max(core_l - arm_l, PX)

    # Sleeve hems
    px_rect(d, arm_l, arm_start + sleeve_h, arm_shade_w, PX, black_light)
    px_rect(d, arm_r - arm_shade_w, arm_start + sleeve_h, arm_shade_w, PX, black_light)

    # Below sleeves: just core torso
    below_sleeve_y = arm_start + sleeve_h + PX
    below_sleeve_h = waist_y - below_sleeve_y
    if below_sleeve_h > 0:
        px_rect(d, core_l - PX, below_sleeve_y, torso_w + PX * 2, below_sleeve_h, black)

    # Arm shading on sleeves
    px_rect(d, arm_l, arm_start, max(PX, arm_shade_w // 2), sleeve_h, black_dark)
    px_rect(d, arm_r - max(PX, arm_shade_w // 2), arm_start, max(PX, arm_shade_w // 2), sleeve_h, black_dark)

    # Small red design (angular cross/star)
    design_y = neck_y + collar_h + max((waist_y - neck_y - collar_h) // 3, PX)
    design_size = min(PX * 3, torso_w // 4)
    design_x = cx - design_size // 2
    if design_y + design_size < waist_y:
        # Horizontal bar
        px_rect(d, design_x, design_y + design_size // 3, design_size, design_size // 3, red_design)
        # Vertical bar
        px_rect(d, design_x + design_size // 3, design_y, design_size // 3, design_size, red_design)
        # Center highlight
        px_rect(d, cx - 2, design_y + design_size // 3 + 1, 4, design_size // 3 - 2, red_dark)

    # Bottom hem
    hem_l = core_l - PX
    hem_w = torso_w + PX * 2
    px_rect(d, hem_l, waist_y - PX, hem_w, PX, black_light)

    # Shoulder seams
    px_rect(d, core_l - 2, arm_start, 3, sleeve_h, black_light)
    px_rect(d, core_r - 1, arm_start, 3, sleeve_h, black_light)


def draw_bottoms_trousers(img, char_name, char_data):
    """Pressed khaki trousers - clean lines, covers legs."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    khaki = (190, 175, 140, 255)
    khaki_light = (210, 195, 160, 255)
    khaki_dark = (160, 145, 110, 255)
    khaki_shadow = (135, 120, 90, 255)
    belt = (90, 60, 35, 255)
    belt_buckle = (195, 175, 55, 255)

    cx = char_data["eye_cx"]
    waist_y = b["waist_y"]
    split_y = b["leg_split_y"]
    feet_y = b["feet_y"]
    ul_l, ul_r = b["upper_leg_x"]
    ll_l, ll_r = b["left_leg_x"]
    rl_l, rl_r = b["right_leg_x"]

    waist_w = ul_r - ul_l

    # Waistband + belt
    px_rect(d, ul_l, waist_y, waist_w, PX * 2, khaki_dark)
    px_rect(d, ul_l, waist_y, waist_w, PX, belt)
    px_rect(d, cx - 4, waist_y + 1, 8, PX - 2, belt_buckle)

    # Upper legs (combined region)
    upper_h = split_y - waist_y - PX * 2
    if upper_h > 0:
        px_rect(d, ul_l, waist_y + PX * 2, waist_w, upper_h, khaki)
        # Center crease
        crease_h = max(1, upper_h - PX)
        px_rect(d, cx - 1, waist_y + PX * 3, 2, crease_h, khaki_shadow)
        # Side creases
        crease_inset = max(waist_w // 6, 4)
        px_rect(d, ul_l + crease_inset, waist_y + PX * 3, 2, crease_h, khaki_dark)
        px_rect(d, ul_r - crease_inset, waist_y + PX * 3, 2, crease_h, khaki_dark)

    # Lower legs (separated)
    lower_h = feet_y - split_y
    if lower_h > 0:
        ll_w = ll_r - ll_l
        rl_w = rl_r - rl_l

        # Left leg
        px_rect(d, ll_l, split_y, ll_w, lower_h, khaki)
        ll_cx = (ll_l + ll_r) // 2
        px_rect(d, ll_cx - 1, split_y, 2, lower_h, khaki_shadow)
        px_rect(d, ll_l, split_y, max(3, PX // 3), lower_h, khaki_dark)
        # Highlight
        px_rect(d, ll_cx + 2, split_y + PX, max(ll_w // 4, 3), max(1, lower_h - PX * 2), khaki_light)

        # Right leg
        px_rect(d, rl_l, split_y, rl_w, lower_h, khaki)
        rl_cx = (rl_l + rl_r) // 2
        px_rect(d, rl_cx - 1, split_y, 2, lower_h, khaki_shadow)
        px_rect(d, rl_r - max(3, PX // 3), split_y, max(3, PX // 3), lower_h, khaki_dark)
        px_rect(d, rl_cx + 2, split_y + PX, max(rl_w // 4, 3), max(1, lower_h - PX * 2), khaki_light)

        # Hems
        px_rect(d, ll_l, feet_y - PX, ll_w, PX, khaki_dark)
        px_rect(d, rl_l, feet_y - PX, rl_w, PX, khaki_dark)


def draw_bottoms_jeans(img, char_name, char_data):
    """Blue denim jeans - medium blue with texture shading."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    denim = (80, 110, 165, 255)
    denim_light = (100, 135, 190, 255)
    denim_dark = (55, 80, 130, 255)
    denim_shadow = (40, 60, 105, 255)
    stitch = (180, 160, 100, 255)
    rivet = (165, 140, 45, 255)

    cx = char_data["eye_cx"]
    waist_y = b["waist_y"]
    split_y = b["leg_split_y"]
    feet_y = b["feet_y"]
    ul_l, ul_r = b["upper_leg_x"]
    ll_l, ll_r = b["left_leg_x"]
    rl_l, rl_r = b["right_leg_x"]

    waist_w = ul_r - ul_l

    # Waistband
    px_rect(d, ul_l, waist_y, waist_w, PX * 2, denim_dark)
    # Belt loops
    for bx in [ul_l + waist_w // 5, cx - 3, cx + waist_w // 5]:
        px_rect(d, bx, waist_y, 4, PX * 2, denim_shadow)
    # Button
    px_rect(d, cx - 3, waist_y + 2, 6, 6, rivet)

    # Upper legs
    upper_h = split_y - waist_y - PX * 2
    if upper_h > 0:
        px_rect(d, ul_l, waist_y + PX * 2, waist_w, upper_h, denim)
        # Fly seam
        px_rect(d, cx - 1, waist_y + PX * 2, 2, min(upper_h // 2, PX * 4), stitch)
        # Pocket outlines
        pocket_w = waist_w // 5
        pocket_h = min(PX * 3, upper_h - PX)
        if pocket_h > 0:
            px_rect(d, ul_l + PX, waist_y + PX * 2, pocket_w, 2, stitch)
            px_rect(d, ul_l + PX, waist_y + PX * 2, 2, pocket_h, stitch)
            px_rect(d, ul_l + PX, waist_y + PX * 2 + pocket_h, pocket_w, 2, stitch)
            rp_x = ul_r - PX - pocket_w
            px_rect(d, rp_x, waist_y + PX * 2, pocket_w, 2, stitch)
            px_rect(d, rp_x + pocket_w - 2, waist_y + PX * 2, 2, pocket_h, stitch)
            px_rect(d, rp_x, waist_y + PX * 2 + pocket_h, pocket_w, 2, stitch)
        # Denim texture
        for ty in range(waist_y + PX * 4, split_y, PX * 2):
            px_rect(d, ul_l + 2, ty, waist_w - 4, 1, denim_light)

    # Lower legs
    lower_h = feet_y - split_y
    if lower_h > 0:
        ll_w = ll_r - ll_l
        rl_w = rl_r - rl_l

        px_rect(d, ll_l, split_y, ll_w, lower_h, denim)
        px_rect(d, ll_l + 2, split_y, 1, lower_h, stitch)
        px_rect(d, ll_r - 3, split_y, 1, lower_h, stitch)
        ll_cx = (ll_l + ll_r) // 2
        knee_y = split_y + lower_h // 3
        px_rect(d, ll_cx - ll_w // 4, knee_y, ll_w // 2, min(PX * 2, lower_h // 3), denim_light)
        px_rect(d, ll_l, split_y, max(3, PX // 3), lower_h, denim_dark)

        px_rect(d, rl_l, split_y, rl_w, lower_h, denim)
        px_rect(d, rl_l + 2, split_y, 1, lower_h, stitch)
        px_rect(d, rl_r - 3, split_y, 1, lower_h, stitch)
        rl_cx = (rl_l + rl_r) // 2
        px_rect(d, rl_cx - rl_w // 4, knee_y, rl_w // 2, min(PX * 2, lower_h // 3), denim_light)
        px_rect(d, rl_r - max(3, PX // 3), split_y, max(3, PX // 3), lower_h, denim_dark)

        # Texture lines
        for ty in range(split_y + PX, feet_y - PX, PX * 2):
            px_rect(d, ll_l + 3, ty, ll_w - 6, 1, denim_light)
            px_rect(d, rl_l + 3, ty, rl_w - 6, 1, denim_light)

        # Hems
        px_rect(d, ll_l, feet_y - PX, ll_w, PX, denim_dark)
        px_rect(d, rl_l, feet_y - PX, rl_w, PX, denim_dark)


def draw_bottoms_punk(img, char_name, char_data):
    """Red plaid skirt - tartan pattern, short, rebellious."""
    d = ImageDraw.Draw(img)
    b = char_data["body"]

    red = (180, 35, 35, 255)
    red_dark = (140, 25, 25, 255)
    plaid_dark = (60, 15, 15, 255)
    plaid_line = (220, 180, 40, 255)
    plaid_green = (30, 80, 30, 255)
    black_trim = (25, 25, 30, 255)
    chain_color = (180, 185, 190, 255)

    cx = char_data["eye_cx"]
    waist_y = b["waist_y"]
    ul_l, ul_r = b["upper_leg_x"]
    split_y = b["leg_split_y"]

    waist_w = ul_r - ul_l

    # Skirt is shorter - covers from waist to about mid-thigh
    skirt_h = max((split_y - waist_y) * 2 // 3, PX * 4)
    skirt_bottom = waist_y + PX * 2 + skirt_h
    flare = PX * 2

    # Waistband
    px_rect(d, ul_l, waist_y, waist_w, PX * 2, black_trim)

    # Main skirt body (A-line flare)
    for row in range(skirt_h // PX + 1):
        ry = waist_y + PX * 2 + row * PX
        t = row / max(1, skirt_h // PX)
        row_l = int(ul_l - flare * t)
        row_r = int(ul_r + flare * t)
        row_w = row_r - row_l
        if row_w > 0 and ry < skirt_bottom:
            px_rect(d, row_l, ry, row_w, PX, red)

    # Tartan horizontal lines
    for row in range(0, skirt_h, PX * 3):
        ry = waist_y + PX * 2 + row
        t = row / max(1, skirt_h)
        row_l = int(ul_l - flare * t)
        row_r = int(ul_r + flare * t)
        row_w = row_r - row_l
        if row_w > 0:
            px_rect(d, row_l, ry, row_w, 2, plaid_dark)
            if row + PX < skirt_h:
                t2 = (row + PX) / max(1, skirt_h)
                rl2 = int(ul_l - flare * t2)
                rr2 = int(ul_r + flare * t2)
                px_rect(d, rl2, ry + PX, rr2 - rl2, 2, plaid_green)

    # Tartan vertical lines
    for col_off in range(ul_l, ul_r, PX * 3):
        px_rect(d, col_off, waist_y + PX * 2, 2, skirt_h, plaid_dark)
    for col_off in range(ul_l + PX, ul_r, PX * 3):
        px_rect(d, col_off, waist_y + PX * 2, 1, skirt_h, plaid_line)

    # Thin gold accent lines
    for row in range(PX, skirt_h, PX * 3):
        ry = waist_y + PX * 2 + row
        t = row / max(1, skirt_h)
        row_l = int(ul_l - flare * t)
        row_r = int(ul_r + flare * t)
        if row_r - row_l > 0:
            px_rect(d, row_l, ry, row_r - row_l, 1, plaid_line)

    # Bottom hem
    hem_l = int(ul_l - flare)
    hem_r = int(ul_r + flare)
    px_rect(d, hem_l, skirt_bottom - PX, hem_r - hem_l, PX, black_trim)

    # Pleats (diagonal shading)
    for pleat in range(0, waist_w, PX * 4):
        px_start = ul_l + pleat
        for row in range(skirt_h // PX):
            ry = waist_y + PX * 2 + row * PX
            px_rect(d, px_start + row * 2, ry, 2, PX, red_dark)

    # Chain detail from waist
    chain_x = ul_l + waist_w // 5
    for i in range(5):
        cy = waist_y + PX + i * 4
        px_rect(d, chain_x + i * 2, cy, 3, 3, chain_color)
    for i in range(3):
        cy = waist_y + PX + 20 + i * 4
        px_rect(d, chain_x + 8 - i * 2, cy, 3, 3, chain_color)


# ══════════════════════════════════════════════════════════════════════════════
# GENERATION PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def save(img, name):
    path = os.path.join(OUT_DIR, f"{name}.png")
    img.save(path)
    print(f"  Saved: {path} ({img.size[0]}x{img.size[1]})")


def generate_standalone_items():
    print("\n=== Generating standalone items ===")
    items = {
        "hat_graduation": make_hat_graduation,
        "hat_cap": make_hat_cap,
        "hat_beanie": make_hat_beanie,
        "glasses_wire": make_glasses_wire,
        "glasses_rect": make_glasses_rect,
        "glasses_dark": make_glasses_dark,
        "neck_medallion": make_neck_medallion,
        "neck_bowtie": make_neck_bowtie,
        "neck_pin": make_neck_pin,
    }
    for name, func in items.items():
        img = func()
        save(img, name)


def generate_body_fitted_items():
    print("\n=== Generating body-fitted items ===")
    all_drawers = {
        "top_blazer": draw_top_blazer,
        "top_hoodie": draw_top_hoodie,
        "top_band": draw_top_band,
        "bottoms_trousers": draw_bottoms_trousers,
        "bottoms_jeans": draw_bottoms_jeans,
        "bottoms_punk": draw_bottoms_punk,
    }

    for item_name, draw_func in all_drawers.items():
        # Species variants
        for species_name, char_data in CHARS.items():
            cw, ch = char_data["canvas"]
            img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            draw_func(img, species_name, char_data)
            save(img, f"{item_name}_{species_name}")

        # Generic version (same as fox)
        fox_data = CHARS["fox"]
        cw, ch = fox_data["canvas"]
        img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        draw_func(img, "fox", fox_data)
        save(img, item_name)


if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}")
    generate_standalone_items()
    generate_body_fitted_items()
    print(f"\nDone! Generated all accessory sprites.")
