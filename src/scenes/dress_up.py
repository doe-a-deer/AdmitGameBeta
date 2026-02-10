import os
import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_BG_ALT,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_ACCENT_LIGHT, COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HOVER,
    COLOR_BUTTON_IDLE, COLOR_BUTTON_HOVER, COLOR_BUTTON_TEXT, COLOR_RULE_LINE,
    SPRITE_DIR
)
from src.data.accessories import ACCESSORIES, ACCESSORY_LOOKUP, ACCESSORIES_BY_SLOT
from src.entities.character import Character

SLOT_ORDER = ["hat", "glasses", "neck", "top", "bottoms"]
SLOT_LABELS = {
    "hat": "HATS", "glasses": "EYES", "neck": "NECK",
    "top": "SHIRTS", "bottoms": "BOTTOMS",
}

# Body-fitted slots get per-animal overlays; standalone slots use universal sprites + anchors
BODY_FITTED_SLOTS = {"top", "bottoms"}
STANDALONE_SLOTS = {"hat", "glasses", "neck"}

# Per-animal anchor data (pixel coords in the raw base sprite).
# eye_cx, eye_cy = center of eye region; neck_y = base of neck; head_top = top of head
ANCHORS = {
    "fox":  {"eye_cx": 307, "eye_cy": 235, "neck_y": 368, "head_top": 0, "w": 522, "h": 609},
    "dog":  {"eye_cx": 227, "eye_cy": 190, "neck_y": 310, "head_top": 0, "w": 447, "h": 548},
    "cat":  {"eye_cx": 176, "eye_cy": 222, "neck_y": 356, "head_top": 0, "w": 365, "h": 587},
}

# Character preview height in logical pixels (width computed to keep aspect ratio)
CHAR_PREVIEW_H = 520

# Thumbnail button size
THUMB_BTN_SIZE = 96

# Wardrobe shelf colors (warm wood tones)
COLOR_SHELF_BG = (185, 145, 105)
COLOR_SHELF_DARK = (145, 110, 75)
COLOR_SHELF_LIGHT = (210, 175, 135)
COLOR_SHELF_EDGE = (120, 85, 55)


class DressUpScene(Scene):
    def __init__(self):
        super().__init__()
        self.character = None
        self.font = None
        self.small_font = None
        self.title_font = None
        self.label_font = None
        self.slot_row_rects = {}      # slot -> Rect of full row
        self.item_btn_rects = {}      # acc_id -> Rect of thumbnail button
        self.confirm_rect = None
        self.reset_rect = None
        self.exit_rect = None
        self.tooltip_text = ""
        self.tooltip_timer = 0
        self.hover_item = None        # acc_id being hovered
        self.mouse_logical = (0, 0)   # last known logical mouse pos

        # Sprite caches
        self.base_surface = None      # raw base sprite (RGBA, original size)
        self.preview_base = None      # scaled base for preview area
        self.overlay_cache = {}       # (acc_id, species) -> raw overlay surface
        self.standalone_cache = {}    # acc_id -> raw standalone surface
        self.thumb_surfaces = {}      # acc_id -> small thumbnail for UI buttons
        self.preview_scale = 1.0      # scale factor from raw to preview
        self.preview_w = 0
        self.preview_h = 0

    def startup(self, persistent):
        super().startup(persistent)
        species = persistent.get("species", "cat")
        self.character = Character(species)
        self.font = get_font(32, bold=True)
        self.small_font = get_font(26)
        self.title_font = get_font(48, bold=True)
        self.label_font = get_font(26, bold=True)
        self.tooltip_text = ""
        self.tooltip_timer = 0
        self.hover_item = None
        self._load_sprites()
        self._build_layout()

    # ── Sprite Loading ──────────────────────────────────────────────

    def _load_sprites(self):
        species = self.character.species
        anch = ANCHORS[species]

        # --- Base character ---
        base_path = os.path.join(SPRITE_DIR, "characters", f"{species}_base.png")
        try:
            self.base_surface = pygame.image.load(base_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.base_surface = pygame.Surface((anch["w"], anch["h"]), pygame.SRCALPHA)

        # Compute preview scale (fit height to CHAR_PREVIEW_H, keep aspect ratio)
        raw_w, raw_h = self.base_surface.get_size()
        self.preview_scale = CHAR_PREVIEW_H / raw_h
        self.preview_w = max(1, int(raw_w * self.preview_scale))
        self.preview_h = CHAR_PREVIEW_H
        self.preview_base = pygame.transform.scale(
            self.base_surface, (self.preview_w, self.preview_h))

        # --- Per-animal body overlays (top & bottoms) ---
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

        # --- Universal standalone sprites (hat, glasses, neck) ---
        self.standalone_cache = {}
        for slot in STANDALONE_SLOTS:
            for acc in ACCESSORIES_BY_SLOT.get(slot, []):
                path = os.path.join(SPRITE_DIR, "accessories", f"{acc.sprite_key}.png")
                try:
                    raw = pygame.image.load(path).convert_alpha()
                    self.standalone_cache[acc.id] = raw
                except (pygame.error, FileNotFoundError):
                    self.standalone_cache[acc.id] = pygame.Surface((1, 1), pygame.SRCALPHA)

        # --- Build thumbnails ---
        self._build_thumbnails()

    def _build_thumbnails(self):
        """Auto-crop each sprite to its opaque bounding box and scale to thumbnail size."""
        self.thumb_surfaces = {}
        pad = 8  # padding inside button
        max_dim = THUMB_BTN_SIZE - pad * 2

        for acc in ACCESSORIES:
            # Get the raw surface
            if acc.id in self.overlay_cache:
                raw = self.overlay_cache[acc.id]
            elif acc.id in self.standalone_cache:
                raw = self.standalone_cache[acc.id]
            else:
                self.thumb_surfaces[acc.id] = pygame.Surface(
                    (max_dim, max_dim), pygame.SRCALPHA)
                continue

            # Find opaque bounding box
            bbox = self._find_opaque_bbox(raw)
            if not bbox:
                self.thumb_surfaces[acc.id] = pygame.Surface(
                    (max_dim, max_dim), pygame.SRCALPHA)
                continue

            l, t, r, b = bbox
            cw, ch = r - l, b - t

            # Crop
            cropped = pygame.Surface((cw, ch), pygame.SRCALPHA)
            cropped.blit(raw, (-l, -t))

            # Scale to fit
            if cw >= ch:
                new_w = max_dim
                new_h = max(1, int(ch * max_dim / cw))
            else:
                new_h = max_dim
                new_w = max(1, int(cw * max_dim / ch))

            self.thumb_surfaces[acc.id] = pygame.transform.scale(cropped, (new_w, new_h))

    @staticmethod
    def _find_opaque_bbox(surface):
        """Return (left, top, right, bottom) of opaque pixels, or None."""
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

        # Left panel: wardrobe shelf rows
        left_margin = 40
        row_w = 520
        row_h = 104
        start_y = 100
        row_gap = 8

        for i, slot in enumerate(SLOT_ORDER):
            ry = start_y + i * (row_h + row_gap)
            self.slot_row_rects[slot] = pygame.Rect(left_margin, ry, row_w, row_h)

            items = ACCESSORIES_BY_SLOT.get(slot, [])
            # Label takes ~140px, buttons are centered in the remaining space
            btn_area_x = left_margin + 140
            btn_area_w = row_w - 140 - 16
            total_btns_w = len(items) * THUMB_BTN_SIZE + (len(items) - 1) * 12
            btn_start_x = btn_area_x + (btn_area_w - total_btns_w) // 2

            for j, acc in enumerate(items):
                bx = btn_start_x + j * (THUMB_BTN_SIZE + 12)
                by = ry + (row_h - THUMB_BTN_SIZE) // 2
                self.item_btn_rects[acc.id] = pygame.Rect(bx, by, THUMB_BTN_SIZE, THUMB_BTN_SIZE)

        # Bottom buttons — placed right after the last shelf row
        btn_w = 240
        btn_h = 56
        btn_gap = 12
        last_row_bottom = start_y + len(SLOT_ORDER) * (row_h + row_gap)
        buttons_y = last_row_bottom + 20

        # Row 1: RESET + SAVE OUTFIT side by side
        self.reset_rect = pygame.Rect(left_margin, buttons_y, btn_w, btn_h)
        self.confirm_rect = pygame.Rect(left_margin + btn_w + btn_gap, buttons_y, btn_w, btn_h)
        # Row 2: Exit to Menu full width
        self.exit_rect = pygame.Rect(left_margin, buttons_y + btn_h + btn_gap, btn_w * 2 + btn_gap, btn_h)

    # ── Events ──────────────────────────────────────────────────────

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                # Check confirm
                if self.confirm_rect.collidepoint(pos):
                    self._confirm()
                    return
                # Check reset
                if self.reset_rect.collidepoint(pos):
                    self._reset()
                    return
                # Check exit
                if self.exit_rect.collidepoint(pos):
                    self.next_scene = "MAIN_MENU"
                    self.done = True
                    return
                # Check item buttons
                for acc_id, rect in self.item_btn_rects.items():
                    if rect.collidepoint(pos):
                        acc = ACCESSORY_LOOKUP[acc_id]
                        if self.character.equipped[acc.slot] == acc_id:
                            self.character.unequip(acc.slot)
                            self.tooltip_text = f"Removed {acc.display_name}"
                        else:
                            self.character.equip(acc)
                            self.tooltip_text = f"\u201c{acc.flavor_text}\u201d"
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
        self.tooltip_text = "Outfit reset"
        self.tooltip_timer = 1.5

    def update(self, dt):
        if self.tooltip_timer > 0:
            self.tooltip_timer -= dt
            if self.tooltip_timer <= 0:
                self.tooltip_text = ""

    # ── Drawing ─────────────────────────────────────────────────────

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # Decorative border frame
        border = pygame.Rect(12, 12, LOGICAL_WIDTH - 24, LOGICAL_HEIGHT - 24)
        pygame.draw.rect(surface, COLOR_RULE_LINE, border, 2, border_radius=8)

        # Title
        species_name = self.character.species.capitalize()
        title = self.title_font.render(f"Dress Up — {species_name}", True, COLOR_TEXT)
        tx = LOGICAL_WIDTH // 2 - title.get_width() // 2
        ty = 28
        surface.blit(title, (tx, ty))

        # Decorative squares flanking title
        sq = 10
        sq_y = ty + title.get_height() // 2 - sq // 2
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, (tx - 28, sq_y, sq, sq))
        pygame.draw.rect(surface, COLOR_PANEL_BORDER,
                         (tx + title.get_width() + 16, sq_y, sq, sq))

        # Rule line under title
        rule_y = ty + title.get_height() + 8
        pygame.draw.line(surface, COLOR_RULE_LINE,
                         (32, rule_y), (LOGICAL_WIDTH - 32, rule_y), 2)

        # ── Wardrobe shelf (left side) ──
        self._draw_wardrobe(surface)

        # ── Character preview (right side) ──
        char_x = 620
        char_y = rule_y + 16
        comp = self._compose_character()
        # Center the character in the available space
        avail_w = LOGICAL_WIDTH - char_x - 32
        cx = char_x + (avail_w - self.preview_w) // 2
        surface.blit(comp, (cx, char_y))

        # ── Equipped label under character ──
        equipped_count = sum(1 for v in self.character.equipped.values() if v)
        eq_text = self.small_font.render(
            f"{equipped_count}/5 items equipped", True, COLOR_TEXT_DIM)
        surface.blit(eq_text, (cx + self.preview_w // 2 - eq_text.get_width() // 2,
                               char_y + self.preview_h + 8))

        # ── Bottom buttons ──
        ml = self.mouse_logical

        # RESET button
        self._draw_button(surface, self.reset_rect, "RESET", ml,
                          idle_color=(200, 180, 155), hover_color=(180, 155, 125))
        # Continue
        self._draw_button(surface, self.confirm_rect, "Continue", ml,
                          idle_color=COLOR_BUTTON_IDLE, hover_color=COLOR_BUTTON_HOVER)
        # Exit (smaller text)
        self._draw_button(surface, self.exit_rect, "Exit to Menu", ml,
                          idle_color=(210, 195, 172), hover_color=(190, 170, 145))

        # ── Tooltip ──
        if self.tooltip_text:
            tt = self.small_font.render(self.tooltip_text, True, COLOR_ACCENT_DARK)
            surface.blit(tt, (40, LOGICAL_HEIGHT - 36))

    def _draw_wardrobe(self, surface):
        """Draw the wardrobe shelf with slot rows and item buttons."""
        for slot in SLOT_ORDER:
            row_rect = self.slot_row_rects[slot]

            # Shelf background (warm wood)
            pygame.draw.rect(surface, COLOR_SHELF_BG, row_rect, border_radius=8)
            # Shelf edge highlights
            edge_top = pygame.Rect(row_rect.x, row_rect.y, row_rect.w, 4)
            pygame.draw.rect(surface, COLOR_SHELF_LIGHT, edge_top)
            edge_bot = pygame.Rect(row_rect.x, row_rect.bottom - 6, row_rect.w, 6)
            pygame.draw.rect(surface, COLOR_SHELF_DARK, edge_bot, border_radius=4)
            # Border
            pygame.draw.rect(surface, COLOR_SHELF_EDGE, row_rect, 2, border_radius=8)

            # Slot label (left side, vertically centered)
            label = self.label_font.render(SLOT_LABELS[slot], True, COLOR_BG)
            ly = row_rect.centery - label.get_height() // 2
            surface.blit(label, (row_rect.x + 20, ly))

            # Item thumbnail buttons
            items = ACCESSORIES_BY_SLOT.get(slot, [])
            for acc in items:
                rect = self.item_btn_rects[acc.id]
                is_equipped = (self.character.equipped[slot] == acc.id)
                is_hover = (self.hover_item == acc.id)

                # Button background
                if is_equipped:
                    bg = COLOR_PANEL_HOVER
                    bc = COLOR_ACCENT
                    bw = 3
                elif is_hover:
                    bg = (255, 250, 240)
                    bc = COLOR_ACCENT_LIGHT
                    bw = 2
                else:
                    bg = COLOR_PANEL_BG
                    bc = COLOR_PANEL_BORDER
                    bw = 2

                pygame.draw.rect(surface, bg, rect, border_radius=8)
                pygame.draw.rect(surface, bc, rect, bw, border_radius=8)

                # Thumbnail centered in button
                thumb = self.thumb_surfaces.get(acc.id)
                if thumb:
                    thx = rect.centerx - thumb.get_width() // 2
                    thy = rect.centery - thumb.get_height() // 2
                    surface.blit(thumb, (thx, thy))

                # Equipped indicator: small dot
                if is_equipped:
                    pygame.draw.circle(surface, COLOR_ACCENT,
                                       (rect.right - 10, rect.top + 10), 6)

    def _draw_button(self, surface, rect, text, mouse_logical,
                     idle_color=None, hover_color=None):
        """Draw a styled button."""
        ic = idle_color or COLOR_BUTTON_IDLE
        hc = hover_color or COLOR_BUTTON_HOVER
        is_hover = rect.collidepoint(mouse_logical)
        bg = hc if is_hover else ic
        pygame.draw.rect(surface, bg, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, 2, border_radius=8)
        t = self.font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(t, t.get_rect(center=rect.center))

    def _compose_character(self):
        """Compose character + equipped accessories at preview size."""
        species = self.character.species
        anch = ANCHORS[species]
        raw_w, raw_h = anch["w"], anch["h"]

        # Start with the base character at raw resolution
        comp = self.base_surface.copy()

        # Layer order: bottoms → top → neck → glasses → hat
        for slot in ["bottoms", "top"]:
            aid = self.character.equipped[slot]
            if aid and aid in self.overlay_cache:
                overlay = self.overlay_cache[aid]
                comp.blit(overlay, (0, 0))

        # Standalone items (neck, glasses, hat) - position via anchors
        for slot in ["neck", "glasses", "hat"]:
            aid = self.character.equipped[slot]
            if aid and aid in self.standalone_cache:
                standalone = self.standalone_cache[aid]
                pos = self._anchor_position(slot, standalone, anch)
                comp.blit(standalone, pos)

        # Scale to preview size using nearest-neighbor for pixel art
        preview = pygame.transform.scale(comp, (self.preview_w, self.preview_h))
        return preview

    def _anchor_position(self, slot, sprite_surface, anchors):
        """Calculate (x, y) position for a standalone accessory on the raw-size canvas."""
        sw, sh = sprite_surface.get_size()
        eye_cx = anchors["eye_cx"]
        eye_cy = anchors["eye_cy"]
        neck_y = anchors["neck_y"]

        if slot == "hat":
            x = eye_cx - sw // 2
            y = eye_cy - sh - 10
            y = max(0, y)
        elif slot == "glasses":
            x = eye_cx - sw // 2
            y = eye_cy - sh // 2
        elif slot == "neck":
            x = eye_cx - sw // 2
            y = neck_y - sh // 4
        else:
            x, y = 0, 0

        return (x, y)
