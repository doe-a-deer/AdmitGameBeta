import pygame
from src.scene import Scene
from src.font_loader import get_font
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, COLOR_BG, COLOR_BG_ALT, COLOR_TEXT,
    COLOR_TEXT_DIM, COLOR_TEXT_LIGHT, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HOVER,
    COLOR_BUTTON_IDLE, COLOR_BUTTON_TEXT, COLOR_RULE_LINE, MAX_COLLEGE_APPS
)
from src.data.colleges import COLLEGES
from src.data.euphemisms import LOADING_SUBTEXTS


class CollegeAppScene(Scene):
    def __init__(self):
        super().__init__()
        self.phase = "select"
        self.selected_colleges = []
        self.college_rects = []
        self.confirm_rect = None
        self.font = None
        self.small_font = None
        self.title_font = None
        self.tiny_font = None
        self.current_app_index = 0
        self.applications = []
        self.app_essay_choice = 0
        self.app_extra_selected = set()
        self.app_statement = ""
        self.app_cursor_visible = True
        self.app_cursor_timer = 0
        self.essay_rects = []
        self.extra_rects = []
        self.submit_rect = None
        self.process_timer = 0

    def startup(self, persistent):
        super().startup(persistent)
        self.phase = "select"
        self.selected_colleges = []
        self.applications = []
        self.current_app_index = 0
        self.process_timer = 0
        self.font = get_font(32, bold=True)
        self.small_font = get_font(30)
        self.title_font = get_font(44, bold=True)
        self.tiny_font = get_font(26)
        self._build_select_layout()

    def _build_select_layout(self):
        self.college_rects = []
        y = 180
        for _ in COLLEGES:
            self.college_rects.append(pygame.Rect(100, y, LOGICAL_WIDTH - 200, 180))
            y += 200
        self.confirm_rect = pygame.Rect(0, 0, 360, 68)
        self.confirm_rect.center = (LOGICAL_WIDTH // 2, y + 40)

    def _build_app_layout(self):
        college = COLLEGES[self.selected_colleges[self.current_app_index]]
        self.essay_rects = []
        y = 170
        for _ in college.essay_prompts:
            self.essay_rects.append(pygame.Rect(80, y, LOGICAL_WIDTH - 160, 64))
            y += 76
        self.extra_rects = []
        y += 28
        for _ in college.extracurriculars:
            self.extra_rects.append(pygame.Rect(80, y, LOGICAL_WIDTH - 160, 44))
            y += 52
        last_bottom = self.extra_rects[-1].bottom if self.extra_rects else y
        submit_y = last_bottom + 20 + 32 + 68 + 90
        self.submit_rect = pygame.Rect(0, 0, 360, 68)
        self.submit_rect.center = (LOGICAL_WIDTH // 2, submit_y)
        self.app_essay_choice = 0
        self.app_extra_selected = set()
        self.app_statement = ""

    def handle_events(self, events):
        if self.phase == "select": self._handle_select(events)
        elif self.phase == "apply": self._handle_apply(events)

    def _handle_select(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(self.college_rects):
                    if r.collidepoint(event.pos):
                        if i in self.selected_colleges: self.selected_colleges.remove(i)
                        elif len(self.selected_colleges) < MAX_COLLEGE_APPS: self.selected_colleges.append(i)
                if self.confirm_rect.collidepoint(event.pos) and len(self.selected_colleges) == MAX_COLLEGE_APPS:
                    self.phase = "apply"
                    self.current_app_index = 0
                    self._build_app_layout()

    def _handle_apply(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(self.essay_rects):
                    if r.collidepoint(event.pos): self.app_essay_choice = i
                for i, r in enumerate(self.extra_rects):
                    if r.collidepoint(event.pos):
                        if i in self.app_extra_selected: self.app_extra_selected.remove(i)
                        elif len(self.app_extra_selected) < 2: self.app_extra_selected.add(i)
                if self.submit_rect.collidepoint(event.pos): self._submit_application()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: self.app_statement = self.app_statement[:-1]
                elif event.key == pygame.K_RETURN and self.app_statement: self._submit_application()
                elif event.unicode and len(self.app_statement) < 200 and event.unicode.isprintable():
                    self.app_statement += event.unicode

    def _submit_application(self):
        college = COLLEGES[self.selected_colleges[self.current_app_index]]
        self.applications.append({
            "college": college.name, "college_id": college.id,
            "essay_topic_index": self.app_essay_choice,
            "extracurricular_selections": list(self.app_extra_selected),
            "personal_statement_length": len(self.app_statement),
        })
        self.current_app_index += 1
        if self.current_app_index < len(self.selected_colleges):
            self._build_app_layout()
        else:
            self.persistent["applications"] = self.applications
            self.phase = "processing"
            self.process_timer = 0

    def update(self, dt):
        if self.phase == "apply":
            self.app_cursor_timer += dt
            self.app_cursor_visible = (self.app_cursor_timer % 1.0) < 0.5
        elif self.phase == "processing":
            self.process_timer += dt
            if self.process_timer >= 3.0:
                self.next_scene = "DECISION"
                self.done = True

    def draw(self, surface):
        surface.fill(COLOR_BG)
        if self.phase == "select": self._draw_select(surface)
        elif self.phase == "apply": self._draw_apply(surface)
        elif self.phase == "processing": self._draw_processing(surface)

    def _draw_select(self, surface):
        surface.blit(self.small_font.render(
            "College Application Portal  \u00b7  Select 2 Institutions", True, COLOR_TEXT_DIM), (80, 30))
        pygame.draw.line(surface, COLOR_RULE_LINE, (80, 64), (LOGICAL_WIDTH - 80, 64), 2)
        t = self.title_font.render("Where Will You Apply?", True, COLOR_ACCENT_DARK)
        surface.blit(t, t.get_rect(center=(LOGICAL_WIDTH//2, 100)))
        s = self.tiny_font.render(f"Select {MAX_COLLEGE_APPS} of {len(COLLEGES)} institutions.", True, COLOR_TEXT_LIGHT)
        surface.blit(s, s.get_rect(center=(LOGICAL_WIDTH//2, 144)))

        for i, college in enumerate(COLLEGES):
            r = self.college_rects[i]
            sel = i in self.selected_colleges
            bg = COLOR_PANEL_HOVER if sel else COLOR_PANEL_BG
            pygame.draw.rect(surface, bg, r, border_radius=10)
            bd = COLOR_ACCENT if sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, bd, r, 3 if sel else 2, border_radius=10)
            cb = pygame.Rect(r.x+24, r.y+24, 32, 32)
            pygame.draw.rect(surface, COLOR_PANEL_BG, cb, border_radius=4)
            pygame.draw.rect(surface, bd, cb, 2, border_radius=4)
            if sel:
                pygame.draw.line(surface, COLOR_ACCENT, (cb.x+6, cb.centery), (cb.centerx, cb.bottom-6), 3)
                pygame.draw.line(surface, COLOR_ACCENT, (cb.centerx, cb.bottom-6), (cb.right-6, cb.y+6), 3)
            surface.blit(self.font.render(college.name, True, COLOR_TEXT), (r.x+76, r.y+20))
            surface.blit(self.tiny_font.render(college.motto, True, COLOR_ACCENT), (r.x+76, r.y+56))
            surface.blit(self.small_font.render(college.tagline, True, COLOR_TEXT_DIM), (r.x+76, r.y+90))
            ext = ", ".join(college.extracurriculars[:3]) + "\u2026"
            surface.blit(self.tiny_font.render(ext, True, COLOR_TEXT_LIGHT), (r.x+76, r.y+130))

        ok = len(self.selected_colleges) == MAX_COLLEGE_APPS
        bg = COLOR_BUTTON_IDLE if ok else COLOR_BG_ALT
        pygame.draw.rect(surface, bg, self.confirm_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT if ok else COLOR_PANEL_BORDER, self.confirm_rect, 2, border_radius=8)
        lbl = "Begin Applications" if ok else f"Select {MAX_COLLEGE_APPS - len(self.selected_colleges)} More"
        bt = self.font.render(lbl, True, COLOR_BUTTON_TEXT if ok else COLOR_TEXT_LIGHT)
        surface.blit(bt, bt.get_rect(center=self.confirm_rect.center))

    def _draw_apply(self, surface):
        college = COLLEGES[self.selected_colleges[self.current_app_index]]
        surface.blit(self.small_font.render(
            f"Application {self.current_app_index+1} of {len(self.selected_colleges)}  \u00b7  {college.name}",
            True, COLOR_TEXT_DIM), (80, 24))
        pygame.draw.line(surface, COLOR_RULE_LINE, (80, 56), (LOGICAL_WIDTH-80, 56), 2)

        pl = self.persistent.get("profile_label", "Applicant")
        sp = self.persistent.get("species", "?").capitalize()
        surface.blit(self.tiny_font.render(f"Applicant: {sp}  |  Type: {pl}", True, COLOR_TEXT_LIGHT), (80, 76))

        surface.blit(self.font.render("Select Essay Prompt:", True, COLOR_ACCENT_DARK), (80, 136))
        for i, r in enumerate(self.essay_rects):
            sel = (i == self.app_essay_choice)
            bg = COLOR_PANEL_HOVER if sel else COLOR_PANEL_BG
            pygame.draw.rect(surface, bg, r, border_radius=8)
            bd = COLOR_ACCENT if sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, bd, r, 2, border_radius=8)
            pygame.draw.circle(surface, bd, (r.x+28, r.centery), 12, 2)
            if sel: pygame.draw.circle(surface, COLOR_ACCENT, (r.x+28, r.centery), 8)
            pr = self._truncate(college.essay_prompts[i], self.small_font, r.width-70)
            surface.blit(self.small_font.render(pr, True, COLOR_TEXT if sel else COLOR_TEXT_DIM), (r.x+52, r.centery-14))

        ya = self.essay_rects[-1].bottom + 20 if self.essay_rects else 360
        surface.blit(self.font.render("Select 2 Activities:", True, COLOR_ACCENT_DARK), (80, ya))
        for i, r in enumerate(self.extra_rects):
            sel = i in self.app_extra_selected
            bg = COLOR_PANEL_HOVER if sel else COLOR_PANEL_BG
            pygame.draw.rect(surface, bg, r, border_radius=6)
            bd = COLOR_ACCENT if sel else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, bd, r, 2, border_radius=6)
            cb = pygame.Rect(r.x+12, r.centery-12, 24, 24)
            pygame.draw.rect(surface, COLOR_PANEL_BG, cb, border_radius=4)
            pygame.draw.rect(surface, bd, cb, 2, border_radius=4)
            if sel:
                pygame.draw.line(surface, COLOR_ACCENT, (cb.x+4, cb.centery), (cb.centerx, cb.bottom-4), 3)
                pygame.draw.line(surface, COLOR_ACCENT, (cb.centerx, cb.bottom-4), (cb.right-4, cb.y+4), 3)
            surface.blit(self.small_font.render(college.extracurriculars[i], True,
                         COLOR_TEXT if sel else COLOR_TEXT_DIM), (r.x+48, r.centery-14))

        ys = self.extra_rects[-1].bottom + 20 if self.extra_rects else 620
        surface.blit(self.font.render("Personal Statement:", True, COLOR_ACCENT_DARK), (80, ys))
        sr = pygame.Rect(80, ys+32, LOGICAL_WIDTH-160, 68)
        pygame.draw.rect(surface, COLOR_PANEL_BG, sr, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, sr, 2, border_radius=8)
        dt = self.app_statement + ("|" if self.app_cursor_visible else "")
        mc = (sr.width-32) // 14
        surface.blit(self.small_font.render(dt[-mc:], True, COLOR_TEXT), (sr.x+16, sr.y+12))
        surface.blit(self.tiny_font.render(f"{len(self.app_statement)}/200", True, COLOR_TEXT_LIGHT), (sr.right-70, sr.bottom+6))
        if not self.app_statement:
            surface.blit(self.tiny_font.render("Begin typing your authentic narrative here\u2026", True, COLOR_TEXT_LIGHT), (sr.x+16, sr.y+40))

        pygame.draw.rect(surface, COLOR_BUTTON_IDLE, self.submit_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.submit_rect, 2, border_radius=8)
        sl = self.font.render("Submit Application", True, COLOR_BUTTON_TEXT)
        surface.blit(sl, sl.get_rect(center=self.submit_rect.center))

    def _draw_processing(self, surface):
        cx = LOGICAL_WIDTH // 2
        surface.blit(self.title_font.render("Submitting applications\u2026", True, COLOR_TEXT),
                     (cx - 240, LOGICAL_HEIGHT//2 - 80))
        bw, bh = 520, 28
        bx, by = (LOGICAL_WIDTH-bw)//2, LOGICAL_HEIGHT//2
        t = self.process_timer / 3.0
        if t < 0.3: p = t/0.3*0.33
        elif t < 0.45: p = 0.33
        elif t < 0.65: p = 0.33 + (t-0.45)/0.2*0.33
        elif t < 0.8: p = 0.66
        else: p = 0.66 + (t-0.8)/0.2*0.34
        p = min(p, 1.0)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, (bx, by, bw, bh), border_radius=14)
        fw = int(bw*p)
        if fw > 0: pygame.draw.rect(surface, COLOR_ACCENT, (bx, by, fw, bh), border_radius=14)
        idx = min(int(self.process_timer), len(LOADING_SUBTEXTS)-1)
        sub = self.tiny_font.render(LOADING_SUBTEXTS[idx], True, COLOR_TEXT_LIGHT)
        surface.blit(sub, (cx - sub.get_width()//2, by + 48))

    def _truncate(self, text, font, max_w):
        if font.size(text)[0] <= max_w: return text
        while font.size(text + "\u2026")[0] > max_w and text: text = text[:-1]
        return text + "\u2026"
