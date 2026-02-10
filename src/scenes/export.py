import os
import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_BUTTON_IDLE, COLOR_BUTTON_TEXT,
    COLOR_RULE_LINE, COLOR_ACCEPT, COLOR_REJECT, COLOR_WAITLIST
)
from src.systems.stat_engine import compute_final_stats
from src.systems.save_manager import save_local, export_downloadable

STAT_COLORS = {
    "money": (180, 155, 50), "connections": (70, 130, 170), "time": (120, 160, 80),
    "stress": (175, 80, 65), "reputation": (140, 110, 180), "integrity": (80, 160, 130),
}
STAT_ORDER = ["money", "connections", "time", "stress", "reputation", "integrity"]


class ExportScene(Scene):
    def __init__(self):
        super().__init__()
        self.stats = {}
        self.font = None
        self.small_font = None
        self.title_font = None
        self.tiny_font = None
        self.save_rect = None
        self.export_rect = None
        self.menu_rect = None
        self.save_message = ""
        self.save_message_timer = 0

    def startup(self, persistent):
        super().startup(persistent)
        self.stats = compute_final_stats(persistent)
        persistent["stats"] = self.stats
        self.font = get_font(32, bold=True)
        self.small_font = get_font(30)
        self.title_font = get_font(48, bold=True)
        self.tiny_font = get_font(26)
        self.save_rect = pygame.Rect(60, LOGICAL_HEIGHT-150, 260, 60)
        self.export_rect = pygame.Rect(340, LOGICAL_HEIGHT-150, 260, 60)
        self.menu_rect = pygame.Rect(LOGICAL_WIDTH-320, LOGICAL_HEIGHT-150, 260, 60)
        self.save_message = ""
        self.save_message_timer = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.save_rect.collidepoint(event.pos):
                    p = save_local(self.persistent)
                    if p:
                        self.save_message = f"Saved to {os.path.basename(p)}"
                    else:
                        self.save_message = "Save unavailable in web version"
                    self.save_message_timer = 3.0
                elif self.export_rect.collidepoint(event.pos):
                    p = export_downloadable(self.persistent)
                    if p:
                        self.save_message = f"Exported: {os.path.basename(p)}"
                    else:
                        self.save_message = "Export unavailable in web version"
                    self.save_message_timer = 3.0
                elif self.menu_rect.collidepoint(event.pos):
                    self.next_scene = "MAIN_MENU"; self.done = True

    def update(self, dt):
        if self.save_message_timer > 0:
            self.save_message_timer -= dt
            if self.save_message_timer <= 0: self.save_message = ""

    def draw(self, surface):
        surface.fill(COLOR_BG)
        cx = LOGICAL_WIDTH // 2
        pygame.draw.line(surface, COLOR_RULE_LINE, (120, 32), (LOGICAL_WIDTH-120, 32), 2)
        t = self.title_font.render("Applicant Dossier", True, COLOR_ACCENT_DARK)
        surface.blit(t, t.get_rect(center=(cx, 60)))
        pygame.draw.line(surface, COLOR_RULE_LINE, (120, 100), (LOGICAL_WIDTH-120, 100), 2)

        sp = self.persistent.get("species", "?").capitalize()
        pl = self.persistent.get("profile_label", "?")
        info = self.font.render(f"{sp}  \u00b7  {pl}", True, COLOR_TEXT)
        surface.blit(info, info.get_rect(center=(cx, 124)))

        # Stat bars
        bx, bw, bh, y = 100, 440, 32, 180
        for sk in STAT_ORDER:
            v = self.stats.get(sk, 0)
            c = STAT_COLORS.get(sk, COLOR_TEXT)
            surface.blit(self.font.render(sk.capitalize(), True, c), (bx, y))
            surface.blit(self.small_font.render(str(v), True, COLOR_TEXT_DIM), (bx+bw+16, y+4))
            by = y + 36
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bx, by, bw, bh), border_radius=6)
            fw = int(bw * v / 100)
            if fw > 0: pygame.draw.rect(surface, c, (bx, by, fw, bh), border_radius=6)
            y += 84

        # Right column
        dx, dy = 740, 180
        surface.blit(self.font.render("Decisions", True, COLOR_ACCENT_DARK), (dx, dy))
        pygame.draw.line(surface, COLOR_RULE_LINE, (dx, dy+32), (dx+400, dy+32), 2)
        dy += 48
        rc = {"accepted": COLOR_ACCEPT, "waitlisted": COLOR_WAITLIST, "rejected": COLOR_REJECT}
        for name, result in self.persistent.get("decisions", {}).items():
            surface.blit(self.small_font.render(name, True, COLOR_TEXT_DIM), (dx, dy)); dy += 28
            surface.blit(self.small_font.render(result.upper(), True, rc.get(result, COLOR_TEXT)), (dx+24, dy)); dy += 44

        dy += 16
        surface.blit(self.font.render("Accessories", True, COLOR_ACCENT_DARK), (dx, dy))
        pygame.draw.line(surface, COLOR_RULE_LINE, (dx, dy+32), (dx+400, dy+32), 2)
        dy += 44
        for slot, aid in self.persistent.get("equipped_accessories", {}).items():
            disp = aid.replace("_", " ").title() if aid else "\u2014"
            surface.blit(self.tiny_font.render(f"{slot.capitalize()}: {disp}", True, COLOR_TEXT_DIM), (dx, dy)); dy += 32

        dy += 16
        tags = self.persistent.get("cosmetic_tags", {})
        ts = f"W:{tags.get('wealth',0)}  S:{tags.get('striving',0)}  R:{tags.get('rebellion',0)}"
        surface.blit(self.tiny_font.render(f"Tags: {ts}", True, COLOR_TEXT_LIGHT), (dx, dy))

        self._btn(surface, self.save_rect, "Save Local")
        self._btn(surface, self.export_rect, "Export JSON")
        self._btn(surface, self.menu_rect, "Main Menu")
        if self.save_message:
            surface.blit(self.small_font.render(self.save_message, True, COLOR_ACCEPT), (60, LOGICAL_HEIGHT-180))

    def _btn(self, surface, rect, text):
        pygame.draw.rect(surface, COLOR_BUTTON_IDLE, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, 2, border_radius=8)
        l = self.font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(l, l.get_rect(center=rect.center))
