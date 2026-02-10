import os
import math
import random
import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_LIGHT,
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_ACCENT_LIGHT,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HOVER,
    COLOR_BUTTON_TEXT, COLOR_RULE_LINE, SPRITE_DIR
)
from src.data.accessories import ACCESSORIES, ACCESSORY_LOOKUP, ACCESSORIES_BY_SLOT
from src.entities.character import Character

SLOT_ORDER = ["hat", "glasses", "neck", "top", "bottoms"]
SLOT_LABELS = {
    "hat": "HATS", "glasses": "GLASSES", "neck": "NECKLACE",
    "top": "TOPS", "bottoms": "BOTTOMS",
}
SLOT_ICONS = {
    "hat": "\u2654", "glasses": "\u25ce", "neck": "\u2661",
    "top": "\u2605", "bottoms": "\u2666",
}

# Body-fitted slots get per-animal overlays; standalone slots use universal sprites + anchors
BODY_FITTED_SLOTS = {"top", "bottoms"}
STANDALONE_SLOTS = {"hat", "glasses", "neck"}

# Per-animal anchor data (pixel coords in the raw base sprite).
ANCHORS = {
    "fox":  {"eye_cx": 307, "eye_cy": 235, "neck_y": 368, "crown_y": 85, "w": 522, "h": 609},
    "dog":  {"eye_cx": 227, "eye_cy": 190, "neck_y": 310, "crown_y": 1, "w": 447, "h": 548},
    "cat":  {"eye_cx": 176, "eye_cy": 222, "neck_y": 356, "crown_y": 65, "w": 365, "h": 587},
}

CHAR_PREVIEW_H = 560

# Item card dimensions (thumbnail + label)
CARD_W = 120
CARD_H = 130
THUMB_SIZE = 88

# ── Cute Pastel Color Palette ──
COLOR_DRESS_BG = (252, 245, 242)         # soft warm white
COLOR_DRESS_BG2 = (248, 238, 235)        # subtle stripe
COLOR_SHELF_PASTEL = (245, 230, 235)     # light pink shelf
COLOR_SHELF_BORDER = (220, 195, 205)     # muted rose border
COLOR_SHELF_LABEL_BG = (235, 210, 220)   # label badge bg
COLOR_CARD_BG = (255, 250, 248)          # card background
COLOR_CARD_HOVER = (255, 245, 240)       # card hover
COLOR_CARD_EQUIPPED = (255, 240, 235)    # card equipped bg
COLOR_CARD_BORDER = (225, 210, 215)      # card border
COLOR_EQUIPPED_RING = (230, 130, 130)    # equipped accent (warm rose)
COLOR_EQUIPPED_DOT = (240, 115, 120)     # equipped dot
COLOR_ITEM_NAME = (120, 90, 100)         # item name text
COLOR_MIRROR_FRAME = (210, 185, 160)     # gold-ish mirror frame
COLOR_MIRROR_INNER = (195, 170, 145)     # inner frame
COLOR_MIRROR_BG = (250, 245, 240)        # mirror backing
COLOR_BTN_CONFIRM = (210, 160, 155)      # warm rose button
COLOR_BTN_CONFIRM_HV = (195, 140, 135)   # hover
COLOR_BTN_RESET = (215, 210, 205)        # soft gray
COLOR_BTN_RESET_HV = (200, 195, 190)
COLOR_BTN_EXIT = (225, 218, 210)
COLOR_BTN_EXIT_HV = (210, 200, 192)
COLOR_TITLE = (140, 85, 95)              # warm rose title
COLOR_SPARKLE = (255, 220, 180)          # warm gold sparkle


class DressUpScene(Scene):
    def __init__(self):
        super().__init__()
        self.character = None
        self.font = None
        self.small_font = None
        self.title_font = None
        self.label_font = None
        self.name_font = None
        self.slot_row_rects = {}
        self.item_btn_rects = {}
        self.confirm_rect = None
        self.reset_rect = None
        self.exit_rect = None
        self.tooltip_text = ""
        self.tooltip_timer = 0
        self.hover_item = None
        self.mouse_logical = (0, 0)
        self.anim_time = 0.0

        # Sparkle particles
        self.sparkles = []

        # Sprite caches
        self.base_surface = None
        self.preview_base = None
        self.overlay_cache = {}
        self.standalone_cache = {}
        self.thumb_surfaces = {}
        self.preview_scale = 1.0
        self.preview_w = 0
        self.preview_h = 0

    def startup(self, persistent):
        super().startup(persistent)
        species = persistent.get("species", "cat")
        self.character = Character(species)
        self.font = get_font(28, bold=True)
        self.small_font = get_font(22)
        self.title_font = get_font(44, bold=True)
        self.label_font = get_font(22, bold=True)
        self.name_font = get_font(16)
        self.tooltip_text = ""
        self.tooltip_timer = 0
        self.hover_item = None
        self.anim_time = 0.0
        self.sparkles = []
        self._load_sprites()
        self._build_layout()

    # ── Sprite Loading ──────────────────────────────────────────────

    def _load_sprites(self):
        species = self.character.species
        anch = ANCHORS[species]

        base_path = os.path.join(SPRITE_DIR, "characters", f"{species}_base.png")
        try:
            self.base_surface = pygame.image.load(base_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.base_surface = pygame.Surface((anch["w"], anch["h"]), pygame.SRCALPHA)

        raw_w, raw_h = self.base_surface.get_size()
        self.preview_scale = CHAR_PREVIEW_H / raw_h
        self.preview_w = max(1, int(raw_w * self.preview_scale))
        self.preview_h = CHAR_PREVIEW_H
        self.preview_base = pygame.transform.scale(
            self.base_surface, (self.preview_w, self.preview_h))

        self.overlay_cache = {}
        for slot in BODY_FITTED_SLOTS:
            for acc in ACCESSORIES_BY_SLOT.get(slot, []):
                per_animal_path = os.path.join(SPRITE_DIR, "accessories", f"{acc.sprite_key}_{species}.png")
                universal_path = os.path.join(SPRITE_DIR, "accessories", f"{acc.sprite_key}.png")
                raw = None
                for try_path in (per_animal_path, universal_path):
                    try:
                        raw = pygame.image.load(try_path).convert_alpha()
                        break
                    except (pygame.error, FileNotFoundError):
                        continue
                if raw:
                    self.overlay_cache[acc.id] = raw
                else:
                    self.overlay_cache[acc.id] = pygame.Surface(
                        (anch["w"], anch["h"]), pygame.SRCALPHA)

        self.standalone_cache = {}
        for slot in STANDALONE_SLOTS:
            for acc in ACCESSORIES_BY_SLOT.get(slot, []):
                path = os.path.join(SPRITE_DIR, "accessories", f"{acc.sprite_key}.png")
                try:
                    raw = pygame.image.load(path).convert_alpha()
                    self.standalone_cache[acc.id] = raw
                except (pygame.error, FileNotFoundError):
                    self.standalone_cache[acc.id] = pygame.Surface((1, 1), pygame.SRCALPHA)

        self._build_thumbnails()

    def _build_thumbnails(self):
        """Auto-crop each sprite and scale to thumbnail size.
        For body-fitted overlays, compose them ON the base character for a better preview."""
        self.thumb_surfaces = {}
        pad = 6
        max_dim = THUMB_SIZE - pad * 2

        for acc in ACCESSORIES:
            is_body = acc.slot in BODY_FITTED_SLOTS
            if is_body and acc.id in self.overlay_cache:
                # For clothing, show it ON the character for a better preview
                preview = self.base_surface.copy()
                preview.blit(self.overlay_cache[acc.id], (0, 0))
                raw = preview
            elif acc.id in self.standalone_cache:
                raw = self.standalone_cache[acc.id]
            elif acc.id in self.overlay_cache:
                raw = self.overlay_cache[acc.id]
            else:
                self.thumb_surfaces[acc.id] = pygame.Surface(
                    (max_dim, max_dim), pygame.SRCALPHA)
                continue

            bbox = self._find_opaque_bbox(raw)
            if not bbox:
                self.thumb_surfaces[acc.id] = pygame.Surface(
                    (max_dim, max_dim), pygame.SRCALPHA)
                continue

            l, t, r, b = bbox
            cw, ch = r - l, b - t

            cropped = pygame.Surface((cw, ch), pygame.SRCALPHA)
            cropped.blit(raw, (-l, -t))

            if cw >= ch:
                new_w = max_dim
                new_h = max(1, int(ch * max_dim / cw))
            else:
                new_h = max_dim
                new_w = max(1, int(cw * max_dim / ch))

            self.thumb_surfaces[acc.id] = pygame.transform.scale(cropped, (new_w, new_h))

    @staticmethod
    def _find_opaque_bbox(surface):
        try:
            rect = surface.get_bounding_rect()
            if rect.width == 0 or rect.height == 0:
                return None
            return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception:
            return None

    # ── Layout ──────────────────────────────────────────────────────

    def _build_layout(self):
        self.slot_row_rects = {}
        self.item_btn_rects = {}

        left_margin = 28
        row_w = 560
        row_h = 135
        start_y = 88
        row_gap = 6

        for i, slot in enumerate(SLOT_ORDER):
            ry = start_y + i * (row_h + row_gap)
            self.slot_row_rects[slot] = pygame.Rect(left_margin, ry, row_w, row_h)

            items = ACCESSORIES_BY_SLOT.get(slot, [])
            label_w = 100
            btn_area_x = left_margin + label_w
            btn_area_w = row_w - label_w - 12
            total_cards_w = len(items) * CARD_W + (len(items) - 1) * 10
            btn_start_x = btn_area_x + (btn_area_w - total_cards_w) // 2

            for j, acc in enumerate(items):
                bx = btn_start_x + j * (CARD_W + 10)
                by = ry + (row_h - CARD_H) // 2
                self.item_btn_rects[acc.id] = pygame.Rect(bx, by, CARD_W, CARD_H)

        # Buttons below shelf rows
        btn_w = 180
        btn_h = 48
        btn_gap = 10
        last_row_bottom = start_y + len(SLOT_ORDER) * (row_h + row_gap)
        buttons_y = last_row_bottom + 12

        total_btns = btn_w * 3 + btn_gap * 2
        btns_start = left_margin + (row_w - total_btns) // 2

        self.reset_rect = pygame.Rect(btns_start, buttons_y, btn_w, btn_h)
        self.confirm_rect = pygame.Rect(btns_start + btn_w + btn_gap, buttons_y, btn_w, btn_h)
        self.exit_rect = pygame.Rect(btns_start + (btn_w + btn_gap) * 2, buttons_y, btn_w, btn_h)

    # ── Events ──────────────────────────────────────────────────────

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.confirm_rect.collidepoint(pos):
                    self._confirm()
                    return
                if self.reset_rect.collidepoint(pos):
                    self._reset()
                    return
                if self.exit_rect.collidepoint(pos):
                    self.next_scene = "MAIN_MENU"
                    self.done = True
                    return
                for acc_id, rect in self.item_btn_rects.items():
                    if rect.collidepoint(pos):
                        acc = ACCESSORY_LOOKUP[acc_id]
                        if self.character.equipped[acc.slot] == acc_id:
                            self.character.unequip(acc.slot)
                            self.tooltip_text = f"Removed {acc.display_name}"
                        else:
                            self.character.equip(acc)
                            self.tooltip_text = f"\u201c{acc.flavor_text}\u201d"
                            self._spawn_sparkles(rect.centerx, rect.centery, 6)
                        self.tooltip_timer = 2.5
                        return

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                self.mouse_logical = pos
                self.hover_item = None
                for acc_id, rect in self.item_btn_rects.items():
                    if rect.collidepoint(pos):
                        self.hover_item = acc_id
                        break

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._confirm()

    def _confirm(self):
        self.persistent["species"] = self.character.species
        self.persistent["equipped_accessories"] = dict(self.character.equipped)
        self.persistent["owned_accessories"] = list(self.character.owned_accessories)
        self.persistent["cosmetic_tags"] = self.character.get_cosmetic_tags(ACCESSORY_LOOKUP)
        self.next_scene = "COLLEGE_APP"
        self.done = True

    def _reset(self):
        for slot in SLOT_ORDER:
            self.character.unequip(slot)
        self.tooltip_text = "Outfit reset!"
        self.tooltip_timer = 1.5

    def _spawn_sparkles(self, x, y, count):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 80)
            life = random.uniform(0.4, 0.9)
            size = random.randint(2, 5)
            self.sparkles.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 30,
                "life": life, "max_life": life,
                "size": size,
            })

    def update(self, dt):
        self.anim_time += dt

        if self.tooltip_timer > 0:
            self.tooltip_timer -= dt
            if self.tooltip_timer <= 0:
                self.tooltip_text = ""

        # Update sparkles
        alive = []
        for s in self.sparkles:
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["vy"] += 60 * dt  # gravity
            s["life"] -= dt
            if s["life"] > 0:
                alive.append(s)
        self.sparkles = alive

    # ── Drawing ─────────────────────────────────────────────────────

    def draw(self, surface):
        # Background with subtle horizontal stripes
        surface.fill(COLOR_DRESS_BG)
        for y in range(0, LOGICAL_HEIGHT, 6):
            if (y // 6) % 2 == 0:
                pygame.draw.line(surface, COLOR_DRESS_BG2, (0, y), (LOGICAL_WIDTH, y))

        # Soft decorative border
        border = pygame.Rect(8, 8, LOGICAL_WIDTH - 16, LOGICAL_HEIGHT - 16)
        pygame.draw.rect(surface, COLOR_SHELF_BORDER, border, 2, border_radius=12)
        inner_border = pygame.Rect(12, 12, LOGICAL_WIDTH - 24, LOGICAL_HEIGHT - 24)
        pygame.draw.rect(surface, (240, 225, 230), inner_border, 1, border_radius=10)

        # Title
        species_name = self.character.species.capitalize()
        title_text = f"Dress Up Your {species_name}!"
        title = self.title_font.render(title_text, True, COLOR_TITLE)
        tx = LOGICAL_WIDTH // 2 - title.get_width() // 2
        ty = 22

        # Title decorative line with dots
        line_y = ty + title.get_height() + 6
        pygame.draw.line(surface, COLOR_SHELF_BORDER,
                         (50, line_y), (LOGICAL_WIDTH - 50, line_y), 1)
        # Small decorative diamonds flanking title
        for offset in [-1, 1]:
            dx = tx + (0 if offset == -1 else title.get_width()) + offset * 18
            dy = ty + title.get_height() // 2
            pts = [(dx, dy - 5), (dx + 5, dy), (dx, dy + 5), (dx - 5, dy)]
            pygame.draw.polygon(surface, COLOR_EQUIPPED_RING, pts)

        surface.blit(title, (tx, ty))

        # Wardrobe (left side)
        self._draw_wardrobe(surface)

        # Character preview (right side) with decorative mirror frame
        self._draw_character_panel(surface, line_y)

        # Bottom buttons
        ml = self.mouse_logical
        self._draw_pill_button(surface, self.reset_rect, "Reset", ml,
                               COLOR_BTN_RESET, COLOR_BTN_RESET_HV)
        self._draw_pill_button(surface, self.confirm_rect, "Save & Continue", ml,
                               COLOR_BTN_CONFIRM, COLOR_BTN_CONFIRM_HV, bold=True)
        self._draw_pill_button(surface, self.exit_rect, "Exit", ml,
                               COLOR_BTN_EXIT, COLOR_BTN_EXIT_HV)

        # Tooltip as floating pill
        if self.tooltip_text:
            tt_font = self.small_font
            tt = tt_font.render(self.tooltip_text, True, COLOR_TITLE)
            tw = tt.get_width() + 28
            th = 32
            tx_pos = 40
            ty_pos = LOGICAL_HEIGHT - 44
            pill = pygame.Rect(tx_pos, ty_pos, tw, th)
            pygame.draw.rect(surface, (255, 245, 242), pill, border_radius=16)
            pygame.draw.rect(surface, COLOR_SHELF_BORDER, pill, 1, border_radius=16)
            surface.blit(tt, (tx_pos + 14, ty_pos + th // 2 - tt.get_height() // 2))

        # Sparkle particles
        for s in self.sparkles:
            alpha = int(255 * (s["life"] / s["max_life"]))
            sz = s["size"]
            sparkle_surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            color = (*COLOR_SPARKLE, alpha)
            pygame.draw.circle(sparkle_surf, color, (sz, sz), sz)
            surface.blit(sparkle_surf, (int(s["x"]) - sz, int(s["y"]) - sz))

    def _draw_wardrobe(self, surface):
        for slot in SLOT_ORDER:
            row_rect = self.slot_row_rects[slot]

            # Shelf row background
            pygame.draw.rect(surface, COLOR_SHELF_PASTEL, row_rect, border_radius=12)
            # Top highlight edge
            highlight = pygame.Rect(row_rect.x + 4, row_rect.y + 2, row_rect.w - 8, 2)
            pygame.draw.rect(surface, (252, 244, 247), highlight, border_radius=1)
            # Bottom subtle shadow edge
            shadow_edge = pygame.Rect(row_rect.x + 4, row_rect.bottom - 3, row_rect.w - 8, 2)
            shadow_surf = pygame.Surface((shadow_edge.w, shadow_edge.h), pygame.SRCALPHA)
            shadow_surf.fill((180, 160, 170, 40))
            surface.blit(shadow_surf, shadow_edge)
            # Border
            pygame.draw.rect(surface, COLOR_SHELF_BORDER, row_rect, 1, border_radius=12)

            # Slot label badge (left side, vertically centered)
            label_text = SLOT_LABELS[slot]
            badge_w = 88
            badge_h = 30
            badge_x = row_rect.x + 6
            badge_y = row_rect.centery - badge_h // 2
            badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
            pygame.draw.rect(surface, COLOR_SHELF_LABEL_BG, badge_rect, border_radius=15)
            pygame.draw.rect(surface, COLOR_SHELF_BORDER, badge_rect, 1, border_radius=15)

            label = self.label_font.render(label_text, True, COLOR_TITLE)
            surface.blit(label, (badge_x + badge_w // 2 - label.get_width() // 2,
                                 badge_y + badge_h // 2 - label.get_height() // 2))

            # Item cards with thumbnails and names
            items = ACCESSORIES_BY_SLOT.get(slot, [])
            for acc in items:
                rect = self.item_btn_rects[acc.id]
                is_equipped = (self.character.equipped[slot] == acc.id)
                is_hover = (self.hover_item == acc.id)

                # Card styling
                if is_equipped:
                    bg = COLOR_CARD_EQUIPPED
                    bc = COLOR_EQUIPPED_RING
                    bw = 3
                elif is_hover:
                    bg = COLOR_CARD_HOVER
                    bc = (210, 170, 185)
                    bw = 2
                else:
                    bg = COLOR_CARD_BG
                    bc = COLOR_CARD_BORDER
                    bw = 1

                draw_rect = rect.copy()
                if is_hover and not is_equipped:
                    draw_rect.y -= 3

                # Card drop shadow
                if is_equipped or is_hover:
                    shadow = pygame.Surface((draw_rect.w + 4, draw_rect.h + 4), pygame.SRCALPHA)
                    pygame.draw.rect(shadow, (160, 130, 145, 30),
                                     (2, 3, draw_rect.w, draw_rect.h), border_radius=10)
                    surface.blit(shadow, (draw_rect.x - 2, draw_rect.y - 1))

                # Card fill
                pygame.draw.rect(surface, bg, draw_rect, border_radius=10)

                # Inner thumbnail area background (subtle cream)
                thumb_area_h = CARD_H - 30
                thumb_bg = pygame.Rect(draw_rect.x + 4, draw_rect.y + 4,
                                       draw_rect.w - 8, thumb_area_h - 4)
                pygame.draw.rect(surface, (248, 243, 240), thumb_bg, border_radius=7)

                # Card border
                pygame.draw.rect(surface, bc, draw_rect, bw, border_radius=10)

                # Thumbnail centered in upper part of card
                thumb = self.thumb_surfaces.get(acc.id)
                if thumb:
                    thx = draw_rect.centerx - thumb.get_width() // 2
                    thy = draw_rect.y + 4 + thumb_area_h // 2 - thumb.get_height() // 2
                    surface.blit(thumb, (thx, thy))

                # Item name label at bottom of card
                name = self.name_font.render(acc.display_name, True,
                                             COLOR_TITLE if is_equipped else COLOR_ITEM_NAME)
                name_x = draw_rect.centerx - name.get_width() // 2
                name_y = draw_rect.bottom - 22
                surface.blit(name, (name_x, name_y))

                # Equipped indicator
                if is_equipped:
                    dot_x = draw_rect.right - 14
                    dot_y = draw_rect.top + 14
                    # Outer glow
                    glow = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (240, 115, 120, 80), (10, 10), 10)
                    surface.blit(glow, (dot_x - 10, dot_y - 10))
                    # Filled dot with white ring
                    pygame.draw.circle(surface, COLOR_EQUIPPED_DOT, (dot_x, dot_y), 7)
                    pygame.draw.circle(surface, (255, 255, 255), (dot_x, dot_y), 5)
                    pygame.draw.circle(surface, COLOR_EQUIPPED_DOT, (dot_x, dot_y), 3)

    def _draw_character_panel(self, surface, top_y):
        """Draw the character preview in a decorative mirror-like frame."""
        panel_x = 608
        panel_y = top_y + 8
        panel_w = LOGICAL_WIDTH - panel_x - 20
        panel_h = LOGICAL_HEIGHT - panel_y - 60

        # Mirror frame (outer)
        frame_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, COLOR_MIRROR_FRAME, frame_rect, border_radius=16)

        # Inner frame border
        inner = pygame.Rect(panel_x + 6, panel_y + 6, panel_w - 12, panel_h - 12)
        pygame.draw.rect(surface, COLOR_MIRROR_INNER, inner, border_radius=12)

        # Mirror surface (light bg)
        mirror = pygame.Rect(panel_x + 10, panel_y + 10, panel_w - 20, panel_h - 20)
        pygame.draw.rect(surface, COLOR_MIRROR_BG, mirror, border_radius=10)

        # Decorative corner ornaments on frame
        ornament_size = 8
        for corner in [(frame_rect.left + 14, frame_rect.top + 14),
                       (frame_rect.right - 14, frame_rect.top + 14),
                       (frame_rect.left + 14, frame_rect.bottom - 14),
                       (frame_rect.right - 14, frame_rect.bottom - 14)]:
            pts = [(corner[0], corner[1] - ornament_size),
                   (corner[0] + ornament_size, corner[1]),
                   (corner[0], corner[1] + ornament_size),
                   (corner[0] - ornament_size, corner[1])]
            pygame.draw.polygon(surface, COLOR_ACCENT_LIGHT, pts)

        # Compose and draw the character
        comp = self._compose_character()
        cx = mirror.x + mirror.w // 2 - self.preview_w // 2
        cy = mirror.y + (mirror.h - 40) // 2 - self.preview_h // 2 + 5
        surface.blit(comp, (cx, cy))

        # Equipped count label below character
        equipped_count = sum(1 for v in self.character.equipped.values() if v)
        eq_text = self.small_font.render(
            f"{equipped_count}/5 items equipped", True, COLOR_TEXT_DIM)
        surface.blit(eq_text, (mirror.x + mirror.w // 2 - eq_text.get_width() // 2,
                               mirror.bottom - 32))

        # Animated sparkle accents on frame (subtle floating dots)
        t = self.anim_time
        for i in range(4):
            angle = t * 0.5 + i * math.pi / 2
            sx = frame_rect.centerx + int(math.cos(angle) * (panel_w // 2 - 8))
            sy = frame_rect.centery + int(math.sin(angle) * (panel_h // 2 - 8))
            alpha = int(128 + 127 * math.sin(t * 2 + i))
            sparkle = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(sparkle, (*COLOR_SPARKLE, alpha), (3, 3), 3)
            surface.blit(sparkle, (sx - 3, sy - 3))

    def _draw_pill_button(self, surface, rect, text, mouse_logical,
                          idle_color, hover_color, bold=False):
        is_hover = rect.collidepoint(mouse_logical)
        bg = hover_color if is_hover else idle_color

        # Pill shape (fully rounded)
        pygame.draw.rect(surface, bg, rect, border_radius=rect.height // 2)
        pygame.draw.rect(surface, COLOR_SHELF_BORDER, rect, 1, border_radius=rect.height // 2)

        # Subtle top highlight
        if not is_hover:
            hl = pygame.Rect(rect.x + 4, rect.y + 2, rect.w - 8, rect.h // 3)
            hl_surf = pygame.Surface((hl.w, hl.h), pygame.SRCALPHA)
            pygame.draw.rect(hl_surf, (255, 255, 255, 35), (0, 0, hl.w, hl.h),
                             border_radius=rect.height // 4)
            surface.blit(hl_surf, hl)

        font = self.font if bold else self.small_font
        t = font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(t, t.get_rect(center=rect.center))

    def _compose_character(self):
        species = self.character.species
        anch = ANCHORS[species]

        comp = self.base_surface.copy()

        for slot in ["bottoms", "top"]:
            aid = self.character.equipped[slot]
            if aid and aid in self.overlay_cache:
                overlay = self.overlay_cache[aid]
                comp.blit(overlay, (0, 0))

        for slot in ["neck", "glasses", "hat"]:
            aid = self.character.equipped[slot]
            if aid and aid in self.standalone_cache:
                standalone = self.standalone_cache[aid]
                pos = self._anchor_position(slot, standalone, anch)
                comp.blit(standalone, pos)

        preview = pygame.transform.scale(comp, (self.preview_w, self.preview_h))
        return preview

    def _anchor_position(self, slot, sprite_surface, anchors):
        sw, sh = sprite_surface.get_size()
        eye_cx = anchors["eye_cx"]
        eye_cy = anchors["eye_cy"]
        neck_y = anchors["neck_y"]

        if slot == "hat":
            x = eye_cx - sw // 2
            crown_y = anchors.get("crown_y", eye_cy - 60)
            y = max(0, crown_y - int(sh * 0.55))
        elif slot == "glasses":
            x = eye_cx - sw // 2
            y = eye_cy - sh // 2
        elif slot == "neck":
            x = eye_cx - sw // 2
            y = neck_y - sh // 4
        else:
            x, y = 0, 0

        return (x, y)
