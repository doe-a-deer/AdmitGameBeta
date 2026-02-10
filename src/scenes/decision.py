import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_PANEL_BORDER, COLOR_BUTTON_IDLE, COLOR_BUTTON_TEXT,
    COLOR_RULE_LINE, COLOR_ACCEPT, COLOR_REJECT, COLOR_WAITLIST
)
from src.systems.decision_engine import compute_all_decisions
from src.data.euphemisms import ACCEPTANCE_LETTERS, WAITLIST_LETTERS, REJECTION_LETTERS
from src.data.colleges import COLLEGE_LOOKUP

RESULT_COLORS = {"accepted": COLOR_ACCEPT, "waitlisted": COLOR_WAITLIST, "rejected": COLOR_REJECT}
RESULT_LABELS = {"accepted": "ACCEPTED", "waitlisted": "WAITLISTED", "rejected": "REJECTED"}


class DecisionScene(Scene):
    def __init__(self):
        super().__init__()
        self.decisions = {}
        self.reveal_order = []
        self.current_reveal = 0
        self.state = "envelope"
        self.font = None
        self.small_font = None
        self.title_font = None
        self.tiny_font = None
        self.envelope_rect = None
        self.continue_rect = None
        self.fade_timer = 0

    def startup(self, persistent):
        super().startup(persistent)
        self.decisions = compute_all_decisions(persistent)
        persistent["decisions"] = self.decisions
        self.reveal_order = list(self.decisions.keys())
        self.current_reveal = 0
        self.state = "envelope"
        self.fade_timer = 0
        self.font = get_font(34, bold=True)
        self.small_font = get_font(32)
        self.title_font = get_font(52, bold=True)
        self.tiny_font = get_font(26)
        self.envelope_rect = pygame.Rect(0, 0, 520, 300)
        self.envelope_rect.center = (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 20)
        self.continue_rect = pygame.Rect(0, 0, 320, 68)
        self.continue_rect.center = (LOGICAL_WIDTH//2, LOGICAL_HEIGHT - 120)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "envelope" and self.envelope_rect.collidepoint(event.pos):
                    self.state = "revealed"; self.fade_timer = 0
                elif self.state == "revealed" and self.continue_rect.collidepoint(event.pos):
                    self.current_reveal += 1
                    if self.current_reveal >= len(self.reveal_order): self.state = "all_done"
                    else: self.state = "envelope"; self.fade_timer = 0
                elif self.state == "all_done" and self.continue_rect.collidepoint(event.pos):
                    self.next_scene = "EXPORT"; self.done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.state == "envelope": self.state = "revealed"; self.fade_timer = 0
                elif self.state == "revealed":
                    self.current_reveal += 1
                    if self.current_reveal >= len(self.reveal_order): self.state = "all_done"
                    else: self.state = "envelope"; self.fade_timer = 0
                elif self.state == "all_done": self.next_scene = "EXPORT"; self.done = True

    def update(self, dt):
        self.fade_timer += dt

    def draw(self, surface):
        surface.fill(COLOR_BG)
        if self.state == "envelope": self._draw_envelope(surface)
        elif self.state == "revealed": self._draw_revealed(surface)
        elif self.state == "all_done": self._draw_summary(surface)

    def _draw_envelope(self, surface):
        cx = LOGICAL_WIDTH // 2
        name = self.reveal_order[self.current_reveal]
        surface.blit(self.small_font.render(
            f"Decision {self.current_reveal+1} of {len(self.reveal_order)}", True, COLOR_TEXT_DIM),
            (cx - 120, 60))
        t = self.title_font.render("Decision Letter", True, COLOR_ACCENT_DARK)
        surface.blit(t, t.get_rect(center=(cx, 130)))

        er = self.envelope_rect
        pygame.draw.rect(surface, (235, 220, 195), er, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT, er, 3, border_radius=8)
        flap = [(er.left+4, er.top+4), (er.centerx, er.centery-40), (er.right-4, er.top+4)]
        pygame.draw.polygon(surface, (225, 210, 185), flap)
        pygame.draw.polygon(surface, COLOR_ACCENT, flap, 2)
        pygame.draw.circle(surface, COLOR_ACCENT, (er.centerx, er.centery-40), 28)
        pygame.draw.circle(surface, COLOR_ACCENT_DARK, (er.centerx, er.centery-40), 28, 3)
        seal = self.tiny_font.render("H", True, COLOR_BG)
        surface.blit(seal, (er.centerx - seal.get_width()//2, er.centery-40-seal.get_height()//2))
        ns = self.font.render(name, True, COLOR_TEXT)
        surface.blit(ns, (er.centerx - ns.get_width()//2, er.centery+30))
        h = self.small_font.render("Click to open", True, COLOR_TEXT_LIGHT)
        surface.blit(h, (cx - h.get_width()//2, er.bottom+40))

    def _draw_revealed(self, surface):
        cx = LOGICAL_WIDTH // 2
        name = self.reveal_order[self.current_reveal]
        result = self.decisions[name]
        rc = RESULT_COLORS[result]
        surface.blit(self.small_font.render(name, True, COLOR_TEXT_DIM), (cx - 160, 50))
        pygame.draw.line(surface, COLOR_RULE_LINE, (160, 84), (LOGICAL_WIDTH-160, 84), 2)
        rt = self.title_font.render(RESULT_LABELS[result], True, rc)
        surface.blit(rt, rt.get_rect(center=(cx, 130)))

        cid = None
        for k, c in COLLEGE_LOOKUP.items():
            if c.name == name: cid = k; break
        if result == "accepted": letter = ACCEPTANCE_LETTERS.get(cid, "You have been accepted.")
        elif result == "waitlisted": letter = WAITLIST_LETTERS.get(cid, "You have been waitlisted.")
        else: letter = REJECTION_LETTERS.get(cid, "We regret to inform you\u2026")
        y = 210
        for line in self._wrap(letter, self.small_font, LOGICAL_WIDTH-240):
            surface.blit(self.small_font.render(line, True, COLOR_TEXT), (120, y)); y += 36
        self._btn(surface, self.continue_rect, "Continue")

    def _draw_summary(self, surface):
        cx = LOGICAL_WIDTH // 2
        t = self.title_font.render("Admissions Summary", True, COLOR_ACCENT_DARK)
        surface.blit(t, t.get_rect(center=(cx, 90)))
        pygame.draw.line(surface, COLOR_RULE_LINE, (200, 140), (LOGICAL_WIDTH-200, 140), 2)
        y = 180
        for name, result in self.decisions.items():
            surface.blit(self.font.render(name, True, COLOR_TEXT), (160, y))
            rs = self.font.render(RESULT_LABELS[result], True, RESULT_COLORS[result])
            surface.blit(rs, (LOGICAL_WIDTH-160-rs.get_width(), y))
            pygame.draw.line(surface, COLOR_RULE_LINE, (160, y+44), (LOGICAL_WIDTH-160, y+44), 2)
            y += 80
        f = self.tiny_font.render("All decisions reflect our commitment to institutional excellence.", True, COLOR_TEXT_LIGHT)
        surface.blit(f, (cx - f.get_width()//2, y+40))
        self.continue_rect.center = (cx, LOGICAL_HEIGHT-120)
        self._btn(surface, self.continue_rect, "View Your Profile")

    def _btn(self, surface, rect, text):
        pygame.draw.rect(surface, COLOR_BUTTON_IDLE, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, 2, border_radius=8)
        l = self.font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(l, l.get_rect(center=rect.center))

    def _wrap(self, text, font, mw):
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = cur + (" " if cur else "") + w
            if font.size(t)[0] <= mw: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines or [""]
