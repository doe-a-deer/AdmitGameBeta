"""
Generate pixel-art accessory sprites for the dress-up game.
Body-fitted clothing traces actual character silhouettes (excluding tails).
Smart width capping prevents clothing from covering tails on wide-body species.
Clothing has layered detail: collars, pockets, seams, buttons, vest underlayers.
"""
from PIL import Image, ImageDraw
import os, math

BASE_DIR = os.path.dirname(__file__)
OUT = os.path.join(BASE_DIR, "assets", "sprites", "accessories")
CHAR_DIR = os.path.join(BASE_DIR, "assets", "sprites", "characters")
os.makedirs(OUT, exist_ok=True)


def px(draw, x, y, color, size=1):
    if size == 1:
        draw.point((x, y), fill=color)
    else:
        draw.rectangle([x, y, x+size-1, y+size-1], fill=color)


# ═══════════════════════════════════════════════════════════════
#  Body region config per species (calibrated from segment analysis)
# ═══════════════════════════════════════════════════════════════

# Body center X for each species
BODY_CX = {"cat": 176, "dog": 222, "fox": 310}

# Reference body half-width at the narrow waist for each species.
# Used to cap width when tail merges with body into one segment.
# Measured from the narrowest torso row (around 60% Y).
BODY_HALF_W = {"cat": 48, "dog": 55, "fox": 65}

BODY_REGIONS = {
    "cat": {
        "torso_top": 0.56, "torso_bot": 0.73,
        "hip_top": 0.70, "leg_bot": 0.87,
    },
    "dog": {
        "torso_top": 0.53, "torso_bot": 0.72,
        "hip_top": 0.68, "leg_bot": 0.92,
    },
    "fox": {
        "torso_top": 0.57, "torso_bot": 0.73,
        "hip_top": 0.70, "leg_bot": 0.88,
    },
}

# Shoulder width multiplier: at the very top of the torso, shrink bounds
# to this fraction of the raw silhouette width, then lerp to 1.0 at waist.
# This prevents clothes from spreading across the full head-to-body transition.
SHOULDER_SHRINK = {"cat": 0.50, "dog": 0.42, "fox": 0.45}


def load_body_mask(species):
    """Load character base sprite, return per-row BODY bounds excluding tail.

    Uses multi-segment analysis to pick the body segment (closest to BODY_CX).
    When tail merges with body into a single wide segment, caps the width
    to a reasonable body-only range based on BODY_HALF_W.
    """
    path = os.path.join(CHAR_DIR, f"{species}_base.png")
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    pixels = img.load()
    body_cx = BODY_CX[species]
    body_hw = BODY_HALF_W[species]

    # First pass: get raw bounds per row
    raw_bounds = {}
    for y in range(h):
        segments = []
        in_seg = False
        seg_start = 0
        for x in range(w):
            if pixels[x, y][3] > 40:
                if not in_seg:
                    seg_start = x
                    in_seg = True
            else:
                if in_seg:
                    segments.append((seg_start, x - 1))
                    in_seg = False
        if in_seg:
            segments.append((seg_start, w - 1))

        if not segments:
            raw_bounds[y] = None
            continue

        if len(segments) == 1:
            raw_bounds[y] = segments[0]
        else:
            # Pick segment whose center is closest to body_cx, weighted by width
            best = None
            best_score = 999999
            for seg in segments:
                seg_cx = (seg[0] + seg[1]) / 2
                seg_w = seg[1] - seg[0]
                score = abs(seg_cx - body_cx) - seg_w * 0.3
                if score < best_score:
                    best_score = score
                    best = seg
            raw_bounds[y] = best

    # Second pass: find the reference body width from the clothing zones.
    # Look at rows where there are multiple segments (tail is separate)
    # to establish the true body width.
    ref_widths = []
    reg = BODY_REGIONS[species]
    y_start = int(h * reg["torso_top"])
    y_end = int(h * reg["leg_bot"])
    for y in range(y_start, y_end):
        # Re-scan for multi-segment rows
        segments = []
        in_seg = False
        seg_start = 0
        for x in range(w):
            if pixels[x, y][3] > 40:
                if not in_seg:
                    seg_start = x
                    in_seg = True
            else:
                if in_seg:
                    segments.append((seg_start, x - 1))
                    in_seg = False
        if in_seg:
            segments.append((seg_start, w - 1))

        if len(segments) >= 2:
            # Multi-segment = tail is separate, body width is trustworthy
            best = min(segments, key=lambda s: abs((s[0]+s[1])/2 - body_cx))
            ref_widths.append(best[1] - best[0])

    # Use the 85th percentile of multi-segment widths as max body width
    if ref_widths:
        ref_widths.sort()
        max_body_w = ref_widths[int(len(ref_widths) * 0.85)]
    else:
        max_body_w = body_hw * 2  # fallback

    # Allow some extra for hips/legs (body gets wider going down)
    max_body_w = int(max_body_w * 1.15)

    # Third pass: cap any row that's wider than max_body_w
    bounds = {}
    for y in range(h):
        b = raw_bounds[y]
        if b is None:
            bounds[y] = None
            continue

        seg_w = b[1] - b[0]
        if seg_w > max_body_w:
            # This row is too wide (tail merged with body)
            # Center the cap around body_cx
            new_left = body_cx - max_body_w // 2
            new_right = body_cx + max_body_w // 2
            # But don't go outside the actual opaque area
            new_left = max(new_left, b[0])
            new_right = min(new_right, b[1])
            bounds[y] = (new_left, new_right)
        else:
            bounds[y] = b

    return img, w, h, bounds


def paint_clothing(img, bounds, h, w, y_start, y_end,
                   color_func, margin=0, species=None, is_top=False):
    """Paint clothing onto body pixels. color_func(x,y,L,R,progress) -> RGB or None.

    If species and is_top are set, applies shoulder shrink at the top of the
    torso to prevent clothes from spreading across the full head-body transition.
    """
    pixels = img.load()
    y0 = int(h * y_start)
    y1 = int(h * y_end)
    total = max(1, y1 - y0)

    shrink = SHOULDER_SHRINK.get(species, 1.0) if (species and is_top) else 1.0

    for y in range(y0, y1):
        b = bounds.get(y)
        if not b:
            continue
        left = max(0, b[0] - margin)
        right = min(w - 1, b[1] + margin)
        progress = (y - y0) / total

        # Shoulder shrink: narrow the bounds at the top of the region
        if shrink < 1.0 and progress < 0.4:
            # Lerp from shrink at progress=0 to 1.0 at progress=0.4
            t = progress / 0.4
            frac = shrink + (1.0 - shrink) * t
            mid = (left + right) / 2
            half = (right - left) / 2 * frac
            left = int(mid - half)
            right = int(mid + half)

        for x in range(left, right + 1):
            c = color_func(x, y, left, right, progress)
            if c:
                pixels[x, y] = (*c, 255)


# ═══════════════════════════════════════════════════════════════
#  TOP: Crimson Blazer — with vest underlayer, collar, gold details
# ═══════════════════════════════════════════════════════════════

def draw_top_blazer(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Rich color palette
    blz_dark = (100, 18, 22)
    blz_mid = (138, 30, 35)
    blz_main = (158, 40, 45)
    blz_light = (178, 55, 58)
    blz_hl = (195, 70, 72)
    gold = (200, 168, 48)
    gold_light = (232, 202, 78)
    gold_dark = (165, 135, 35)
    vest_dark = (52, 50, 58)
    vest_mid = (68, 65, 75)
    vest_light = (82, 78, 88)
    collar = (235, 230, 220)
    collar_sh = (212, 208, 198)
    outline = (70, 14, 18)

    def blazer_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw       # 0=center 1=edge
        dx = (x - mid) / hw          # signed: negative=left, positive=right

        # ── Outer edge outline ──
        if x <= left + 1 or x >= right - 1:
            return outline

        # ── Gold edge trim (both sides) ──
        if x < left + 4 or x > right - 4:
            return gold

        # ── White collar at very top ──
        if progress < 0.14:
            collar_w = 0.50 - progress * 2.0
            if collar_w > 0 and d < collar_w:
                if d < collar_w * 0.5:
                    return collar
                return collar_sh

        # ── Vest/tie underlayer in center ──
        vest_width = 0.30 - progress * 0.04
        if d < vest_width and progress > 0.06:
            # Tie stripe down center
            if d < 0.035:
                return gold_dark if int(y) % 6 < 3 else gold
            # Vest body
            if d < vest_width * 0.5:
                return vest_mid
            if d < vest_width * 0.8:
                return vest_dark
            # vest edge / blazer lapel line
            return gold_dark

        # ── Gold lapel lines running from collar to mid-torso ──
        lapel_pos = 0.28 + progress * 0.06
        if progress < 0.60 and abs(d - lapel_pos) < 0.035:
            return gold_light

        # ── Main blazer body shading ──
        if d < 0.32:
            base = blz_hl
        elif d < 0.50:
            base = blz_light
        elif d < 0.68:
            base = blz_main
        elif d < 0.85:
            base = blz_mid
        else:
            base = blz_dark

        # ── Buttons (3 gold buttons down vest edge) ──
        for bp in [0.22, 0.42, 0.62]:
            if abs(progress - bp) < 0.025 and abs(d - vest_width) < 0.05:
                return gold_light

        # ── Breast pocket on left side ──
        if 0.32 < progress < 0.50 and -0.68 < dx < -0.42:
            if abs(progress - 0.32) < 0.018:
                return gold_dark
            if abs(dx + 0.42) < 0.025 or abs(dx + 0.68) < 0.025:
                return blz_dark

        # ── Fabric fold lines ──
        if 0.25 < progress < 0.85:
            for fold_x in [-0.58, 0.58]:
                if abs(dx - fold_x) < 0.022:
                    return blz_dark

        # ── Bottom hem ──
        if progress > 0.92:
            return outline

        return base

    paint_clothing(img, bounds, h, w, reg["torso_top"], reg["torso_bot"],
                   blazer_color, margin=4, species=species, is_top=True)
    img.save(os.path.join(OUT, f"top_blazer_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "top_blazer.png"))


# ═══════════════════════════════════════════════════════════════
#  TOP: Grey Hoodie — with zipper, hood outline, pocket, cuffs
# ═══════════════════════════════════════════════════════════════

def draw_top_hoodie(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    hd_dark = (108, 108, 118)
    hd_mid = (138, 138, 148)
    hd_main = (155, 155, 165)
    hd_light = (172, 172, 182)
    hd_hl = (188, 188, 198)
    zip_metal = (205, 205, 215)
    zip_dark = (155, 155, 165)
    drawstr = (220, 220, 228)
    drawstr_tip = (180, 180, 190)
    pocket_line = (118, 118, 130)
    cuff = (95, 95, 108)
    hood = (115, 115, 128)
    hood_inner = (135, 135, 148)
    outline = (78, 78, 90)
    brand_color = (90, 140, 185)

    def hoodie_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw
        dx = (x - mid) / hw

        # ── Edge outline ──
        if x <= left + 1 or x >= right - 1:
            return outline

        # ── Hood neckline at top ──
        if progress < 0.12:
            if d > 0.42:
                return hood
            elif d > 0.32:
                return hood_inner
            elif d > 0.28:
                return outline

        # ── Center zipper track ──
        if d < 0.04:
            if int(y) % 4 < 2:
                return zip_metal
            else:
                return zip_dark

        # ── Zipper pull tab near top ──
        if progress < 0.08 and d < 0.06:
            return zip_metal

        # ── Drawstrings hanging from neckline ──
        if progress < 0.35:
            for ds_x in [-0.12, 0.12]:
                if abs(dx - ds_x) < 0.018:
                    return drawstr
            # Drawstring aglets (metal tips)
            if 0.28 < progress < 0.35:
                for ds_x in [-0.12, 0.12]:
                    if abs(dx - ds_x) < 0.028:
                        return drawstr_tip

        # ── Small brand logo on left chest ──
        if 0.18 < progress < 0.30 and -0.45 < dx < -0.25:
            logo_cx = -0.35
            logo_cy = 0.24
            logo_dx = abs(dx - logo_cx) * 12
            logo_dy = abs(progress - logo_cy) * 12
            if logo_dx * logo_dx + logo_dy * logo_dy < 2.5:
                return brand_color

        # ── Kangaroo pocket ──
        pocket_top = 0.52
        pocket_bot = 0.85
        pocket_w = 0.50
        if pocket_top < progress < pocket_bot and d < pocket_w:
            # Pocket opening at top
            if abs(progress - pocket_top) < 0.025:
                return pocket_line
            # Pocket side edges
            if abs(d - pocket_w) < 0.035:
                return pocket_line
            # Pocket divider in middle
            if d < 0.035 and progress > pocket_top + 0.06:
                return pocket_line

        # ── Main body shading ──
        if d < 0.15:
            base = hd_hl
        elif d < 0.32:
            base = hd_light
        elif d < 0.52:
            base = hd_main
        elif d < 0.72:
            base = hd_mid
        else:
            base = hd_dark

        # ── Ribbed hem at bottom ──
        if progress > 0.88:
            return cuff if int(x) % 3 == 0 else hd_dark

        # ── Sleeve crease lines ──
        if 0.15 < progress < 0.75:
            for fold in [-0.62, 0.62]:
                if abs(dx - fold) < 0.022:
                    return hd_dark

        return base

    paint_clothing(img, bounds, h, w, reg["torso_top"], reg["torso_bot"],
                   hoodie_color, margin=3, species=species, is_top=True)
    img.save(os.path.join(OUT, f"top_hoodie_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "top_hoodie.png"))


# ═══════════════════════════════════════════════════════════════
#  TOP: Band Tee — with graphic print, visible neckline, short sleeves
# ═══════════════════════════════════════════════════════════════

def draw_top_band(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    tee_dark = (22, 20, 25)
    tee_mid = (35, 32, 38)
    tee_main = (45, 42, 50)
    tee_light = (58, 54, 62)
    tee_hl = (68, 64, 72)
    red = (195, 50, 45)
    red_dk = (155, 35, 32)
    red_bright = (220, 65, 58)
    white = (210, 205, 195)
    outline = (12, 10, 15)
    neck_line = (15, 14, 18)

    y0_abs = int(h * reg["torso_top"])
    y1_abs = int(h * reg["torso_bot"])
    graphic_cy = y0_abs + (y1_abs - y0_abs) * 0.40

    def tee_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw
        dx = (x - mid) / hw
        body_w = right - left

        # ── Edge outline ──
        if x <= left + 1 or x >= right - 1:
            return outline

        # ── Round neckline cutout ──
        if progress < 0.08:
            neck_r = (1 - progress * 10) * 0.28
            if d < neck_r:
                return None  # show skin

        # ── Neckline ring ──
        if progress < 0.12:
            neck_r = max(0, (1 - progress * 7) * 0.28)
            if abs(d - neck_r) < 0.045:
                return neck_line

        # ── Main body ──
        if d < 0.12:
            base = tee_hl
        elif d < 0.28:
            base = tee_light
        elif d < 0.52:
            base = tee_main
        elif d < 0.75:
            base = tee_mid
        else:
            base = tee_dark

        # ── Band graphic: skull/star circle design ──
        gdx = x - mid
        gdy = y - graphic_cy
        gr = math.sqrt(gdx*gdx + gdy*gdy)
        graphic_r = body_w * 0.22

        # Outer circle
        if abs(gr - graphic_r) < 3:
            return red
        # Inner circle
        if abs(gr - graphic_r * 0.65) < 2:
            return red_dk

        # Star shape inside
        if gr < graphic_r * 0.55:
            angle = math.atan2(gdy, gdx)
            star = math.cos(angle * 5) * 0.5 + 0.5
            star_r = graphic_r * (0.25 + star * 0.28)
            if gr < star_r:
                return red_bright if gr < star_r * 0.5 else red

        # ── Small text under graphic ──
        if 0.55 < progress < 0.62 and d < 0.25:
            text_row = int((progress - 0.55) * 200)
            text_col = int((dx + 0.25) * 30)
            if text_row % 3 == 0 and text_col % 2 == 0:
                return white

        # ── Sleeve seam lines ──
        for fold in [-0.68, 0.68]:
            if abs(dx - fold) < 0.025 and progress > 0.04:
                return outline

        # ── Hem at bottom ──
        if progress > 0.92:
            return outline

        return base

    paint_clothing(img, bounds, h, w, reg["torso_top"], reg["torso_bot"],
                   tee_color, margin=2, species=species, is_top=True)
    img.save(os.path.join(OUT, f"top_band_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "top_band.png"))


# ═══════════════════════════════════════════════════════════════
#  BOTTOMS: Pressed Trousers — with belt, creases, cuffs, pockets
# ═══════════════════════════════════════════════════════════════

def draw_bottoms_trousers(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    kh = (188, 172, 142)
    kh_light = (202, 188, 158)
    kh_dark = (162, 148, 118)
    kh_shadow = (142, 128, 100)
    kh_hl = (215, 200, 170)
    crease = (172, 158, 130)
    belt_dk = (72, 48, 25)
    belt = (98, 68, 38)
    belt_lt = (128, 95, 55)
    buckle = (215, 185, 60)
    buckle_lt = (240, 215, 90)
    outline = (100, 85, 65)
    pocket = (175, 160, 132)

    def trouser_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw
        dx = (x - mid) / hw

        # ── Outline ──
        if x <= left or x >= right:
            return outline

        # ── Belt ──
        if progress < 0.08:
            if abs(dx) < 0.09:
                return buckle_lt if progress < 0.04 else buckle
            if progress < 0.025:
                return belt_lt
            if progress < 0.055:
                return belt
            return belt_dk

        # ── Belt loops ──
        if 0.0 < progress < 0.10:
            for lp in [-0.38, 0.38, -0.65, 0.65]:
                if abs(dx - lp) < 0.03:
                    return belt_dk

        # ── Front pockets (diagonal slash pockets) ──
        if 0.09 < progress < 0.28:
            for side in [-1, 1]:
                pocket_x = side * (0.48 - progress * 0.5)
                if abs(dx - pocket_x) < 0.035:
                    return pocket

        # ── Center crease ──
        if d < 0.045 and progress > 0.08:
            return crease

        # ── Main fabric shading ──
        if d < 0.15:
            base = kh_hl
        elif d < 0.32:
            base = kh_light
        elif d < 0.55:
            base = kh
        elif d < 0.78:
            base = kh_dark
        else:
            base = kh_shadow

        # ── Side seam ──
        if d > 0.85 and progress > 0.08:
            return outline

        # ── Cuff at bottom ──
        if progress > 0.88:
            if progress > 0.94:
                return kh_shadow
            return kh_dark

        return base

    paint_clothing(img, bounds, h, w, reg["hip_top"], reg["leg_bot"],
                   trouser_color, margin=2)
    img.save(os.path.join(OUT, f"bottoms_trousers_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "bottoms_trousers.png"))


# ═══════════════════════════════════════════════════════════════
#  BOTTOMS: Jeans — with denim texture, stitching, rivets
# ═══════════════════════════════════════════════════════════════

def draw_bottoms_jeans(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    den = (78, 98, 148)
    den_lt = (92, 112, 162)
    den_dk = (62, 80, 125)
    den_sh = (48, 62, 105)
    den_hl = (105, 125, 175)
    seam = (98, 115, 165)
    stitch = (168, 158, 115)
    waist = (55, 68, 112)
    waist_dk = (40, 52, 90)
    button = (185, 172, 132)
    rivet = (200, 175, 60)
    outline = (32, 45, 78)

    def jeans_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw
        dx = (x - mid) / hw

        # Denim texture hash
        noise = ((x * 7 + y * 13) % 7)

        # ── Outline ──
        if x <= left or x >= right:
            return outline

        # ── Waistband ──
        if progress < 0.07:
            if abs(dx) < 0.06:
                return button
            return waist if progress < 0.035 else waist_dk

        # ── Fly front ──
        if 0.07 < progress < 0.28 and d < 0.08:
            if int(y) % 3 == 0:
                return stitch  # visible stitching on fly
            return den_dk

        # ── Front pocket rivets ──
        if 0.09 < progress < 0.13:
            for rx in [-0.42, 0.42]:
                if abs(dx - rx) < 0.028:
                    return rivet

        # ── Front pocket arcs ──
        if 0.10 < progress < 0.30:
            for side in [-1, 1]:
                pocket_cx = side * 0.42
                pocket_r = 0.22
                pdist = math.sqrt((dx - pocket_cx)**2 + (progress - 0.18)**2 * 4)
                if abs(pdist - pocket_r) < 0.03:
                    return stitch

        # ── Side seams with stitch ──
        if d > 0.80:
            if int(y) % 4 == 0:
                return stitch
            return seam

        # ── Main denim ──
        if d < 0.12:
            base = den_hl
        elif d < 0.28:
            base = den_lt
        elif d < 0.52:
            base = den
        elif d < 0.72:
            base = den_dk
        else:
            base = den_sh

        # Denim noise texture
        if noise < 2:
            base = tuple(min(255, c + 6) for c in base)
        elif noise == 6:
            base = tuple(max(0, c - 4) for c in base)

        # ── Knee wear area (lighter) ──
        if 0.52 < progress < 0.72 and d < 0.38:
            base = tuple(min(255, c + 10) for c in base)

        # ── Hem ──
        if progress > 0.91:
            return waist_dk

        return base

    paint_clothing(img, bounds, h, w, reg["hip_top"], reg["leg_bot"],
                   jeans_color, margin=2)
    img.save(os.path.join(OUT, f"bottoms_jeans_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "bottoms_jeans.png"))


# ═══════════════════════════════════════════════════════════════
#  BOTTOMS: Plaid Skirt — tartan with flare, pleats, waistband
# ═══════════════════════════════════════════════════════════════

def draw_bottoms_punk(species):
    reg = BODY_REGIONS[species]
    _, w, h, bounds = load_body_mask(species)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    red = (172, 40, 44)
    red_lt = (195, 55, 58)
    red_dk = (138, 28, 32)
    navy = (38, 38, 72)
    navy_lt = (55, 55, 95)
    green = (42, 85, 52)
    gold = (208, 188, 55)
    waist_color = (32, 32, 58)
    waist_buckle = (185, 165, 45)
    outline = (25, 22, 42)
    hem = (28, 28, 52)

    # Skirt goes from hip_top to about 65% of the way to leg_bot
    skirt_end_frac = reg["hip_top"] + (reg["leg_bot"] - reg["hip_top"]) * 0.65

    # Build flared bounds — flare scales with body width
    y0 = int(h * reg["hip_top"])
    y1 = int(h * skirt_end_frac)
    flared = dict(bounds)
    for y in range(y0, y1):
        b = bounds.get(y)
        if b:
            prog = (y - y0) / max(1, y1 - y0)
            body_w = b[1] - b[0]
            flare = int(prog * body_w * 0.18)  # 18% of body width at max
            flared[y] = (max(0, b[0] - flare), min(w-1, b[1] + flare))

    def skirt_color(x, y, left, right, progress):
        mid = (left + right) / 2
        hw = max(1, (right - left) / 2)
        d = abs(x - mid) / hw
        dx = (x - mid) / hw

        # ── Outline ──
        if x <= left + 1 or x >= right - 1:
            return outline

        # ── Waistband ──
        if progress < 0.12:
            if abs(dx) < 0.06:
                return waist_buckle
            return waist_color

        # ── Tartan plaid ──
        gx = x % 16
        gy = y % 16

        # Base is red
        c = red
        # Navy grid lines
        if gx < 3 or gy < 3:
            c = navy
        elif gx < 4 or gy < 4:
            c = navy_lt
        # Gold accent stripe
        if gx == 8 or gy == 8:
            c = gold
        # Green accent at intersections
        if 6 <= gx <= 10 and 6 <= gy <= 10 and c == red:
            c = green
        # Dark square at navy intersections
        if gx < 3 and gy < 3:
            c = (28, 28, 52)

        # ── Pleat fold shading ──
        pleat = (x - left) % 20
        if pleat < 2:
            c = tuple(max(0, v - 40) for v in c)
        elif pleat == 2:
            c = tuple(max(0, v - 18) for v in c)
        elif pleat == 18:
            c = tuple(min(255, v + 18) for v in c)
        elif pleat == 19:
            c = tuple(min(255, v + 10) for v in c)

        # ── Hem at bottom ──
        if progress > 0.88:
            return hem

        return c

    paint_clothing(img, flared, h, w, reg["hip_top"], skirt_end_frac,
                   skirt_color, margin=3)
    img.save(os.path.join(OUT, f"bottoms_punk_{species}.png"))
    if species == "cat":
        img.save(os.path.join(OUT, "bottoms_punk.png"))


# ═══════════════════════════════════════════════════════════════
#  STANDALONE ACCESSORIES (hats, glasses, neck)
# ═══════════════════════════════════════════════════════════════

def make_graduation_hat():
    w, h = 64, 40
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    cx = 32
    board_hl, board_mid, board_dk = (70,70,110),(40,40,70),(30,30,55)
    for row in range(8):
        hw = 8 + row * 3; y = 2 + row
        for x in range(cx-hw, cx+hw):
            if 0 <= x < w:
                px(d, x, y, board_hl if row < 2 else (board_mid if row < 5 else board_dk))
    for x in range(cx-28,cx+28): px(d,x,10,(25,25,45)); px(d,x,11,(25,25,45))
    for row in range(12):
        y = 12+row; hw = 20-abs(row-4) if row <= 8 else 20-(row-8)*2
        for x in range(cx-hw,cx+hw):
            dist = abs(x-cx)
            px(d,x,y,(60,60,95) if dist < 6 else ((45,45,75) if dist < 12 else (35,35,60)))
    for x in range(cx-18,cx+18): px(d,x,24,(50,50,80))
    for dy in range(3):
        for dx in range(3): px(d,cx-1+dx,1+dy,(240,210,80) if dx==1 and dy==0 else (200,170,50))
    for i in range(10): px(d,cx+14+i//3,3+i,(160,130,30))
    for dy in range(6):
        for dx in range(4): px(d,cx+16+dx,12+dy,(240,210,80) if dx<2 and dy<4 else (160,130,30))
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"hat_graduation.png"))

def make_baseball_cap():
    w, h = 58, 38
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    cx = 29
    for row in range(16):
        y = 4+row; hw = 6+row*3 if row < 4 else (18+(row-4) if row < 12 else 26-(row-12))
        for x in range(cx-hw,cx+hw):
            if 0<=x<w:
                dist = abs(x-cx)
                px(d,x,y,(170,185,200) if (row<3 or dist<5) else ((140,155,175) if dist<12 else (110,125,145)))
    for y in range(5,18): px(d,cx,y,(200,210,225))
    for dy in range(2):
        for dx in range(2): px(d,cx-1+dx,4+dy,(200,210,225))
    for row in range(5):
        y = 20+row
        for x in range(cx-24+row,cx+8):
            if 0<=x<w: px(d,x,y,(100,120,160) if row<2 else ((80,100,140) if row<4 else (60,80,115)))
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"hat_cap.png"))

def make_beanie():
    w, h = 54, 38
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    cx = 27
    for dy in range(5):
        for dx in range(5):
            if abs(dx-2)+abs(dy-2)<=3:
                px(d,cx-2+dx,1+dy,(100,93,103) if abs(dx-2)+abs(dy-2)<=1 else (75,68,78))
    for row in range(18):
        y=6+row; hw=8+row*3 if row<4 else (20+(row-4) if row<14 else 24)
        for x in range(cx-hw,cx+hw):
            if 0<=x<w:
                c=x%3; px(d,x,y,(95,87,97) if row<3 else ((50,45,55) if c==0 else ((65,58,68) if c==1 else (80,72,82))))
    for row in range(3):
        for x in range(cx-24,cx+24):
            if 0<=x<w: px(d,x,21+row,(165,55,50) if row<2 else (135,40,35))
    for row in range(5):
        for x in range(cx-24,cx+24):
            if 0<=x<w:
                c=x%3; px(d,x,24+row,(50,45,55) if c==0 else ((65,58,68) if c==1 else ((80,72,82) if row<3 else (50,45,55))))
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"hat_beanie.png"))

def make_gold_rounds():
    w, h = 48, 18
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    g,gl,gd = (195,165,55),(230,200,90),(155,125,35)
    lt,ls = (220,230,245,80),(255,255,255,120)
    for cy,cxp in [(9,12),(9,36)]:
        for ay in range(-6,7):
            for ax in range(-6,7):
                dist=(ax**2+ay**2)**0.5
                if 4.5<=dist<=6.5: px(d,cxp+ax,cy+ay,gl if ay<-2 else (g if ay<2 else gd))
                elif dist<4.5: px(d,cxp+ax,cy+ay,lt)
    for x in range(18,30): px(d,x,8,g); px(d,x,9,gd)
    for x in range(0,6): px(d,x,9,g); px(d,x,10,gd)
    for x in range(42,48): px(d,x,9,g); px(d,x,10,gd)
    px(d,10,7,ls); px(d,11,7,ls); px(d,34,7,ls); px(d,35,7,ls)
    img.resize((w*4,h*4),Image.NEAREST).save(os.path.join(OUT,"glasses_wire.png"))

def make_square_frames():
    w, h = 48, 16
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    f,fl,fd = (55,55,65),(80,80,95),(35,35,45)
    ln,ls = (200,210,230,60),(255,255,255,100)
    for y in range(3,13):
        for x in range(4,18):
            px(d,x,y,(fl if y==3 else (f if x==4 else fd)) if (y in(3,12) or x in(4,17)) else ln)
        for x in range(30,44):
            px(d,x,y,(fl if y==3 else (f if x==30 else fd)) if (y in(3,12) or x in(30,43)) else ln)
    for x in range(18,30): px(d,x,6,f); px(d,x,7,fd)
    for x in range(0,5): px(d,x,7,f)
    for x in range(43,48): px(d,x,7,f)
    px(d,6,5,ls); px(d,7,5,ls); px(d,32,5,ls); px(d,33,5,ls)
    for x in range(5,17): px(d,x,3,f); px(d,x,4,fl)
    for x in range(31,43): px(d,x,3,f); px(d,x,4,fl)
    img.resize((w*4,h*4),Image.NEAREST).save(os.path.join(OUT,"glasses_rect.png"))

def make_dark_shades():
    w, h = 50, 16
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    f,fl,fd = (30,28,35),(50,48,55),(18,16,22)
    ln = (25,22,30); ls1,ls2 = (90,88,100,180),(60,58,70,150)
    for y in range(3,13):
        row=y-3
        lx = 5+(2-row) if row<2 else (4 if row<8 else 4+(row-8)*2)
        rx = 19 if row<2 else (20 if row<8 else 20-(row-8))
        for x in range(lx,rx): px(d,x,y,fl if y==3 else f) if (y in(3,12) or x in(lx,rx-1)) else px(d,x,y,ln)
        lx2 = 30 if row<2 else (29 if row<8 else 29+(row-8))
        rx2 = 44-(2-row) if row<2 else (45 if row<8 else 45-(row-8)*2)
        for x in range(lx2,rx2): px(d,x,y,fl if y==3 else f) if (y in(3,12) or x in(lx2,rx2-1)) else px(d,x,y,ln)
    for x in range(19,30): px(d,x,5,f); px(d,x,6,fd)
    for x in range(0,5): px(d,x,6,f); px(d,x,7,fd)
    for x in range(44,50): px(d,x,6,f); px(d,x,7,fd)
    for i in range(4): px(d,7+i,5+i,ls1); px(d,8+i,5+i,ls2); px(d,32+i,5+i,ls1); px(d,33+i,5+i,ls2)
    img.resize((w*4,h*4),Image.NEAREST).save(os.path.join(OUT,"glasses_dark.png"))

def make_gold_medallion():
    w, h = 44, 36
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    cg,cl,cd = (200,170,50),(235,205,80),(160,130,30)
    mg,ml,md,mi = (210,180,60),(245,215,95),(170,140,35),(190,160,45)
    cx = 22
    for i in range(10):
        x=cx-18+i*2; y=1+i; c=cl if i%2==0 else cg
        px(d,x,y,c); px(d,x+1,y,cd); x2=cx+18-i*2; px(d,x2,y,c); px(d,x2-1,y,cd)
    px(d,cx,11,cg); px(d,cx-1,10,cg); px(d,cx+1,10,cg)
    for dy in range(-8,9):
        for dx in range(-8,9):
            dist=(dx**2+dy**2)**0.5
            if dist<=8:
                c = md if dy>2 else mg if dist>6.5 else (ml if dy<-1 else mg) if dist>5.5 else mi if dist>4 else (md if dy>0 else ml) if dist>2.5 else (ml if (dx+dy)%2==0 else mg)
                px(d,cx+dx,20+dy,c)
    px(d,cx-3,15,(255,240,150)); px(d,cx-2,14,(255,240,150))
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"neck_medallion.png"))

def make_bowtie():
    w, h = 42, 22
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    bm,bl,bd,bs = (60,65,120),(85,90,150),(40,45,90),(30,35,70)
    kn,kl = (50,55,100),(75,80,135)
    cx,cy = 21,11
    for row in range(-7,8):
        y=cy+row; width=max(2,12-abs(row))
        for dx in range(-width,0):
            x=cx-4+dx
            if x>=0: px(d,x,y,bl if row<-3 else (bd if abs(dx)>width-2 else (bs if row>3 else bm)))
        for dx in range(0,width):
            x=cx+4+dx
            if x<w: px(d,x,y,bl if row<-3 else (bd if dx>width-3 else (bs if row>3 else bm)))
    for dy in range(-3,4):
        for dx in range(-3,4):
            if abs(dx)+abs(dy)<=4: px(d,cx+dx,cy+dy,kl if dy<0 else kn)
    for i in range(3): px(d,cx-8-i,cy-2+i,bl); px(d,cx-10-i,cy-1+i,bd); px(d,cx+8+i,cy-2+i,bl); px(d,cx+10+i,cy-1+i,bd)
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"neck_bowtie.png"))

def make_safety_pin():
    w, h = 14, 24
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    s,sl,sd = (190,195,205),(220,225,235),(140,145,155)
    for dy in range(-3,4):
        for dx in range(-3,4):
            dist=(dx**2+(dy*1.3)**2)**0.5
            if dist<=3: px(d,7+dx,4+dy,sl if dy<0 else (sd if dist>2 else s))
    for y in range(7,18): px(d,5,y,sl); px(d,6,y,s); px(d,7,y,sd)
    for dx in range(-1,4): px(d,5+dx,18,s); px(d,5+dx,19,sd)
    for y in range(10,18): px(d,8,y,sl); px(d,9,y,s)
    px(d,9,8,sl); px(d,9,9,s); px(d,9,10,s)
    px(d,5,9,(255,255,255,160)); px(d,5,10,(255,255,255,100))
    img.resize((w*3,h*3),Image.NEAREST).save(os.path.join(OUT,"neck_pin.png"))


if __name__ == "__main__":
    print("Generating standalone accessories...")
    make_graduation_hat(); make_baseball_cap(); make_beanie()
    make_gold_rounds(); make_square_frames(); make_dark_shades()
    make_gold_medallion(); make_bowtie(); make_safety_pin()
    print("  Done.")

    print("Generating body-fitted overlays (silhouette-traced)...")
    for sp in ["cat", "dog", "fox"]:
        print(f"  {sp}...")
        draw_top_blazer(sp); draw_top_hoodie(sp); draw_top_band(sp)
        draw_bottoms_trousers(sp); draw_bottoms_jeans(sp); draw_bottoms_punk(sp)
    print("  Done.")
    print("\nAll sprites generated!")
