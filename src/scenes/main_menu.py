import pygame
from src.scene import Scene
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_BUTTON_IDLE,
    COLOR_BUTTON_HOVER, COLOR_BUTTON_TEXT, COLOR_RULE_LINE, COLOR_PANEL_BORDER
)


class MainMenuScene(Scene):
    def __init__(self):
        super().__init__()
        self.title_font = None
        self.subtitle_font = None
        self.button_font = None
        self.small_font = None
        self.start_rect = None
        self.quit_rect = None
        self.hovered = None

    def startup(self, persistent):
        super().startup(persistent)
        self.title_font = pygame.font.SysFont("Georgia", 36, bold=True)
        self.subtitle_font = pygame.font.SysFont("Georgia", 16, italic=True)
        self.button_font = pygame.font.SysFont("Georgia", 15)
        self.small_font = pygame.font.SysFont("Georgia", 11)
        self.start_rect = pygame.Rect(0, 0, 200, 42)
        self.start_rect.center = (LOGICAL_WIDTH // 2, 270)
        self.quit_rect = pygame.Rect(0, 0, 200, 42)
        self.quit_rect.center = (LOGICAL_WIDTH // 2, 330)
        self.hovered = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
                if self.start_rect.collidepoint(pos):
                    self.hovered = "start"
                elif self.quit_rect.collidepoint(pos):
                    self.hovered = "quit"
                else:
                    self.hovered = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.start_rect.collidepoint(pos):
                    self.next_scene = "PERSONALITY_TEST"
                    self.done = True
                elif self.quit_rect.collidepoint(pos):
                    self.quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.next_scene = "PERSONALITY_TEST"
                    self.done = True
                elif event.key == pygame.K_ESCAPE:
                    self.quit = True

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(COLOR_BG)
        cx = LOGICAL_WIDTH // 2

        # Decorative top rule with diamond ornament
        pygame.draw.line(surface, COLOR_RULE_LINE, (80, 60), (LOGICAL_WIDTH - 80, 60), 1)
        pts = [(cx, 56), (cx + 4, 60), (cx, 64), (cx - 4, 60)]
        pygame.draw.polygon(surface, COLOR_ACCENT, pts)

        # Title
        title = self.title_font.render("HYBRIS", True, COLOR_ACCENT_DARK)
        surface.blit(title, title.get_rect(center=(cx, 110)))

        # Subtitle
        sub = self.subtitle_font.render("Create Your Applicant", True, COLOR_TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(cx, 150)))

        # Rule
        pygame.draw.line(surface, COLOR_RULE_LINE, (160, 175), (LOGICAL_WIDTH - 160, 175), 1)

        # Tagline
        tag = self.small_font.render(
            "A holistic assessment of your potential.", True, COLOR_TEXT_LIGHT)
        surface.blit(tag, tag.get_rect(center=(cx, 200)))

        # Buttons
        self._draw_button(surface, self.start_rect, "Begin Assessment", self.hovered == "start")
        self._draw_button(surface, self.quit_rect, "Exit", self.hovered == "quit")

        # Footer
        pygame.draw.line(surface, COLOR_RULE_LINE,
                         (80, LOGICAL_HEIGHT - 60), (LOGICAL_WIDTH - 80, LOGICAL_HEIGHT - 60), 1)
        footer = self.small_font.render(
            "v1.0  \u00b7  Institutional Review Pending", True, COLOR_TEXT_LIGHT)
        surface.blit(footer, footer.get_rect(center=(cx, LOGICAL_HEIGHT - 42)))

    def _draw_button(self, surface, rect, text, hovered):
        bg = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON_IDLE
        pygame.draw.rect(surface, bg, rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, 1, border_radius=4)
        label = self.button_font.render(text, True, COLOR_BUTTON_TEXT)
        surface.blit(label, label.get_rect(center=rect.center))
