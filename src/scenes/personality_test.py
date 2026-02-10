import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_PANEL_BG,
    COLOR_PANEL_BORDER, COLOR_PANEL_HOVER, COLOR_RULE_LINE
)
from src.data.questions import QUESTIONS
from src.systems.profile_engine import assign_profile, PROFILE_BASELINES


class PersonalityTestScene(Scene):
    def __init__(self):
        super().__init__()
        self.current_q = 0
        self.selected = 0
        self.answers = []
        self.font = None
        self.small_font = None
        self.q_font = None
        self.state = "question"
        self.process_timer = 0
        self.typewriter_timer = 0
        self.typewriter_index = 0
        self.answer_rects = []

    def startup(self, persistent):
        super().startup(persistent)
        self.current_q = 0
        self.selected = 0
        self.answers = []
        self.state = "question"
        self.process_timer = 0
        self.typewriter_timer = 0
        self.typewriter_index = 0
        self.font = get_font(34, bold=True)
        self.small_font = get_font(30)
        self.q_font = get_font(40, italic=True)

    def handle_events(self, events):
        if self.state != "question":
            return
        question = QUESTIONS[self.current_q]
        num_answers = len(question["answers"])
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % num_answers
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % num_answers
                elif event.key == pygame.K_RETURN:
                    self._confirm_answer()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.answer_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        self._confirm_answer()
                        break
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.answer_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        break

    def _confirm_answer(self):
        self.answers.append(self.selected)
        self.current_q += 1
        self.selected = 0
        self.typewriter_index = 0
        self.typewriter_timer = 0
        if self.current_q >= len(QUESTIONS):
            self.state = "processing"
            self.process_timer = 0

    def update(self, dt):
        if self.state == "question":
            self.typewriter_timer += dt
            text_len = len(QUESTIONS[self.current_q]["text"])
            self.typewriter_index = min(int(self.typewriter_timer * 40), text_len)
        elif self.state == "processing":
            self.process_timer += dt
            if self.process_timer >= 2.5:
                profile_key, profile_label = assign_profile(self.answers)
                self.persistent["quiz_answers"] = self.answers
                self.persistent["profile"] = profile_key
                self.persistent["profile_label"] = profile_label
                self.persistent["base_stats"] = dict(PROFILE_BASELINES[profile_key])
                self.next_scene = "AVATAR_SELECT"
                self.done = True

    def draw(self, surface):
        surface.fill(COLOR_BG)
        q_num = self.current_q + 1 if self.state == "question" else len(QUESTIONS)
        header = self.small_font.render(
            f"Intake Assessment  \u00b7  Question {q_num} of {len(QUESTIONS)}", True, COLOR_TEXT_DIM)
        surface.blit(header, (80, 50))
        pygame.draw.line(surface, COLOR_RULE_LINE, (80, 88), (LOGICAL_WIDTH - 80, 88), 2)

        if self.state == "question":
            self._draw_question(surface)
        elif self.state == "processing":
            self._draw_processing(surface)

    def _draw_question(self, surface):
        question = QUESTIONS[self.current_q]
        visible = question["text"][:self.typewriter_index]
        lines = self._wrap_text(visible, self.q_font, LOGICAL_WIDTH - 200)
        y = 130
        for line in lines:
            surface.blit(self.q_font.render(line, True, COLOR_ACCENT_DARK), (100, y))
            y += 44

        y = max(y + 50, 280)
        self.answer_rects = []
        for i, answer in enumerate(question["answers"]):
            rect = pygame.Rect(100, y, LOGICAL_WIDTH - 200, 100)
            self.answer_rects.append(rect)
            is_sel = (i == self.selected)
            bg = COLOR_PANEL_HOVER if is_sel else COLOR_PANEL_BG
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            border = COLOR_ACCENT if is_sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, border, rect, 2, border_radius=8)
            bx, by = rect.x + 36, rect.centery
            if is_sel:
                pygame.draw.circle(surface, COLOR_ACCENT, (bx, by), 10)
            else:
                pygame.draw.circle(surface, COLOR_PANEL_BORDER, (bx, by), 10, 2)
            alines = self._wrap_text(answer["text"], self.font, rect.width - 100)
            ay = rect.y + 16
            for al in alines:
                color = COLOR_TEXT if is_sel else COLOR_TEXT_DIM
                surface.blit(self.font.render(al, True, color), (rect.x + 72, ay))
                ay += 36
            y += 120

        hint = self.small_font.render(
            "\u2191\u2193 or mouse  \u00b7  Enter to confirm", True, COLOR_TEXT_LIGHT)
        surface.blit(hint, (100, LOGICAL_HEIGHT - 110))

    def _draw_processing(self, surface):
        cx = LOGICAL_WIDTH // 2
        label = self.q_font.render("Processing your profile\u2026", True, COLOR_TEXT)
        surface.blit(label, (cx - label.get_width() // 2, LOGICAL_HEIGHT // 2 - 80))
        bar_w, bar_h = 520, 28
        bar_x = (LOGICAL_WIDTH - bar_w) // 2
        bar_y = LOGICAL_HEIGHT // 2
        t = self.process_timer / 2.5
        if t < 0.3: progress = t / 0.3 * 0.33
        elif t < 0.45: progress = 0.33
        elif t < 0.65: progress = 0.33 + (t - 0.45) / 0.2 * 0.33
        elif t < 0.8: progress = 0.66
        else: progress = 0.66 + (t - 0.8) / 0.2 * 0.34
        progress = min(progress, 1.0)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bar_x, bar_y, bar_w, bar_h), border_radius=14)
        fw = int(bar_w * progress)
        if fw > 0:
            pygame.draw.rect(surface, COLOR_ACCENT, (bar_x, bar_y, fw, bar_h), border_radius=14)
        sub = self.small_font.render("Holistic deliberation in progress\u2026", True, COLOR_TEXT_LIGHT)
        surface.blit(sub, (cx - sub.get_width() // 2, bar_y + 48))

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current: lines.append(current)
                current = word
        if current: lines.append(current)
        return lines or [""]
