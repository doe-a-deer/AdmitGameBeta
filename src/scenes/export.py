import pygame
from src.scene import Scene
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
        self.font = pygame.font.SysFont("Georgia", 12, bold=True)
        self.small_font = pygame.font.SysFont("Georgia", 11)
        self.title_font = pygame.font.SysFont("Georgia", 18, bold=True)
        self.tiny_font = pygame.font.SysFont("Georgia", 10)
        self.save_rect = pygame.Rect(30, LOGICAL_HEIGHT-75, 130, 30)
        self.export_rect = pygame.Rect(170, LOGICAL_HEIGHT-75, 130, 30)
        self.menu_rect = pygame.Rect(LOGICAL_WIDTH-160, LOGICAL_HEIGHT-75, 130, 30)
        self.save_message = ""
        self.save_message_timer = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.save_rect.collidepoint(event.pos):
                    p = save_local(self.persistent)
                    self.save_message = f"Saved to {p.name}"; self.save_message_timer = 3.0
                elif self.export_rect.collidepoint(event.pos):
                    p = export_downloadable(self.persistent)
                    self.save_message = f"Exported: {p.name}"; self.save_message_timer = 3.0
                elif self.menu_rect.collidepoint(event.pos):
                    self.next_scene = "MAIN_MENU"; self.done = True

    def update(self, dt):
        if self.save_message_timer > 0:
            self.save_message_timer -= dt
            if self.save_message_timer <= 0: self.save_message = ""

    def draw(self, surface):
        surface.fill(COLOR_BG)
        cx = LOGICAL_WIDTH // 2
        pygame.draw.line(surface, COLOR_RULE_LINE, (60, 16), (LOGICAL_WIDTH-60, 16), 1)
        t = self.title_font.render("Applicant Dossier", True, COLOR_ACCENT_DARK)
        surface.blit(t, t.get_rect(center=(cx, 30)))
        pygame.draw.line(surface, COLOR_RULE_LINE, (60, 50), (LOGICAL_WIDTH-60, 50), 1)

        sp = self.persistent.get("species", "?").capitalize()
        pl = self.persistent.get("profile_label", "?")
        info = self.font.render(f"{sp}  \u00b7  {pl}", True, COLOR_TEXT)
        surface.blit(info, info.get_rect(center=(cx, 62)))

        # Stat bars
        bx, bw, bh, y = 50, 220, 16, 90
        for sk in STAT_ORDER:
            v = self.stats.get(sk, 0)
            c = STAT_COLORS.get(sk, COLOR_TEXT)
            surface.blit(self.font.render(sk.capitalize(), True, c), (bx, y))
            surface.blit(self.small_font.render(str(v), True, COLOR_TEXT_DIM), (bx+bw+8, y+2))
            by = y + 18
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bx, by, bw, bh), border_radius=3)
            fw = int(bw * v / 100)
            if fw > 0: pygame.draw.rect(surface, c, (bx, by, fw, bh), border_radius=3)
            y += 42

        # Right column
        dx, dy = 370, 90
        surface.blit(self.font.render("Decisions", True, COLOR_ACCENT_DARK), (dx, dy))
        pygame.draw.line(surface, COLOR_RULE_LINE, (dx, dy+16), (dx+200, dy+16), 1)
        dy += 24
        rc = {"accepted": COLOR_ACCEPT, "waitlisted": COLOR_WAITLIST, "rejected": COLOR_REJECT}
        for name, result in self.persistent.get("decisions", {}).items():
            surface.blit(self.small_font.render(name, True, COLOR_TEXT_DIM), (dx, dy)); dy += 14
            surface.blit(self.small_font.render(result.upper(), True, rc.get(result, COLOR_TEXT)), (dx+12, dy)); dy += 22

        dy += 8
        surface.blit(self.font.render("Accessories", True, COLOR_ACCENT_DARK), (dx, dy))
        pygame.draw.line(surface, COLOR_RULE_LINE, (dx, dy+16), (dx+200, dy+16), 1)
        dy += 22
        for slot, aid in self.persistent.get("equipped_accessories", {}).items():
            disp = aid.replace("_", " ").title() if aid else "\u2014"
            surface.blit(self.tiny_font.render(f"{slot.capitalize()}: {disp}", True, COLOR_TEXT_DIM), (dx, dy)); dy += 16

        dy += 8
        tags = self.persistent.get("cosmetic_tags", {})
        ts = f"W:{tags.get('wealth',0)}  S:{tags.get('striving',0)}  R:{tags.get('rebellion',0)}"
        surface.blit(self.tiny_font.render(f"Tags: {ts}", True, COLOR_TEXT_LIGHT), (dx, dy))

        self._btn(surface, self.save_rect, "Save Local")
        self._btn(surface, self.export_rect, "Export JSON")
        self._btn(surface, self.menu_rect, "Main Menu")
        if self.save_message:
            surface.blit(self.small_font.render(self.save_message, True, COLOR_ACCEPT), (30, LOGICAL_HEIGHT-90))

    def _btn(self, surface, rect, text):
        pygame.draw.rect(surface, COLOR_BUTTON_IDLE, rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, 1, border_radius=4)
        l = self.font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(l, l.get_rect(center=rect.center))
