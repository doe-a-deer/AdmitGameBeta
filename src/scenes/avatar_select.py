import os
import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_PANEL_BG,
    COLOR_PANEL_BORDER, COLOR_PANEL_HOVER, COLOR_BUTTON_IDLE,
    COLOR_BUTTON_TEXT, COLOR_RULE_LINE, SPRITE_DIR, CHAR_DISPLAY_SIZE
)

SPECIES = ["cat", "dog", "fox"]


class AvatarSelectScene(Scene):
    def __init__(self):
        super().__init__()
        self.selected = 0
        self.sprites = {}
        self.rects = []
        self.font = None
        self.title_font = None
        self.small_font = None
        self.confirm_rect = None

    def startup(self, persistent):
        super().startup(persistent)
        self.selected = 0
        self.font = get_font(36, bold=True)
        self.title_font = get_font(48, bold=True)
        self.small_font = get_font(30)

        self.sprites = {}
        card_w, card_h = 300, 400
        spacing = 60
        total_w = card_w * 3 + spacing * 2
        start_x = (LOGICAL_WIDTH - total_w) // 2
        # Max sprite area inside each card (with padding for label)
        max_sprite_w = card_w - 32   # 16px padding each side
        max_sprite_h = card_h - 80   # room for label at bottom
        self.rects = []
        for i, species in enumerate(SPECIES):
            path = os.path.join(SPRITE_DIR, "characters", f"{species}_base.png")
            try:
                raw = pygame.image.load(path).convert_alpha()
                # Scale to fit inside card while preserving aspect ratio
                rw, rh = raw.get_size()
                scale = min(max_sprite_w / rw, max_sprite_h / rh)
                new_w = max(1, int(rw * scale))
                new_h = max(1, int(rh * scale))
                self.sprites[species] = pygame.transform.scale(raw, (new_w, new_h))
            except (pygame.error, FileNotFoundError):
                s = pygame.Surface((max_sprite_w, max_sprite_h), pygame.SRCALPHA)
                pygame.draw.rect(s, COLOR_PANEL_BORDER, (0, 0, max_sprite_w, max_sprite_h), 1)
                self.sprites[species] = s
            self.rects.append(pygame.Rect(start_x + i * (card_w + spacing), 220, card_w, card_h))

        self.confirm_rect = pygame.Rect(0, 0, 360, 76)
        self.confirm_rect.center = (LOGICAL_WIDTH // 2, 740)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: self.selected = (self.selected - 1) % 3
                elif event.key == pygame.K_RIGHT: self.selected = (self.selected + 1) % 3
                elif event.key == pygame.K_RETURN: self._confirm()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(self.rects):
                    if r.collidepoint(event.pos): self.selected = i
                if self.confirm_rect.collidepoint(event.pos): self._confirm()
            elif event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(self.rects):
                    if r.collidepoint(event.pos): self.selected = i

    def _confirm(self):
        self.persistent["species"] = SPECIES[self.selected]
        self.next_scene = "DRESS_UP"
        self.done = True

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(COLOR_BG)
        profile_label = self.persistent.get("profile_label", "Applicant")
        header = self.small_font.render(
            f"Profile: {profile_label}  \u00b7  Select Your Representative", True, COLOR_TEXT_DIM)
        surface.blit(header, (80, 40))
        pygame.draw.line(surface, COLOR_RULE_LINE, (80, 76), (LOGICAL_WIDTH - 80, 76), 2)

        title = self.title_font.render("Choose Your Avatar", True, COLOR_ACCENT_DARK)
        surface.blit(title, title.get_rect(center=(LOGICAL_WIDTH // 2, 130)))
        sub = self.small_font.render("Your representative for the admissions process.", True, COLOR_TEXT_LIGHT)
        surface.blit(sub, sub.get_rect(center=(LOGICAL_WIDTH // 2, 180)))

        for i, species in enumerate(SPECIES):
            rect = self.rects[i]
            is_sel = (i == self.selected)
            bg = COLOR_PANEL_HOVER if is_sel else COLOR_PANEL_BG
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            border = COLOR_ACCENT if is_sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, border, rect, 3 if is_sel else 2, border_radius=12)
            sprite = self.sprites[species]
            # Center sprite horizontally and vertically in the card (above label)
            sprite_area_h = rect.height - 72  # leave room for label
            sx = rect.centerx - sprite.get_width() // 2
            sy = rect.y + 12 + (sprite_area_h - sprite.get_height()) // 2
            surface.blit(sprite, (sx, sy))
            color = COLOR_ACCENT_DARK if is_sel else COLOR_TEXT_DIM
            label = self.font.render(species.capitalize(), True, color)
            surface.blit(label, label.get_rect(center=(rect.centerx, rect.bottom - 32)))

        # Confirm button
        pygame.draw.rect(surface, COLOR_BUTTON_IDLE, self.confirm_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.confirm_rect, 2, border_radius=8)
        btn = self.font.render("Confirm Selection", True, COLOR_BUTTON_TEXT)
        surface.blit(btn, btn.get_rect(center=self.confirm_rect.center))

        hint = self.small_font.render(
            "\u2190\u2192 or mouse  \u00b7  Enter to confirm", True, COLOR_TEXT_LIGHT)
        surface.blit(hint, hint.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 100)))
