import asyncio
import pygame
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, FPS, COLOR_BG_DARK
)


class Game:
    """Main game controller. Manages the loop, scene transitions, and scaling."""

    def __init__(self, screen, scenes, start_scene_name):
        self.screen = screen
        self.logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.scenes = scenes
        self.current_scene_name = start_scene_name
        self.current_scene = self.scenes[start_scene_name]
        self.clock = pygame.time.Clock()
        self.running = True
        self.persistent = {}
        self.current_scene.startup(self.persistent)
        self._update_scaling()

    def _update_scaling(self):
        """Recalculate scale factor and offset to fit logical surface in window."""
        win_w, win_h = self.screen.get_size()
        scale_x = win_w / LOGICAL_WIDTH
        scale_y = win_h / LOGICAL_HEIGHT
        self.scale = min(scale_x, scale_y)
        self.scaled_w = int(LOGICAL_WIDTH * self.scale)
        self.scaled_h = int(LOGICAL_HEIGHT * self.scale)
        self.offset_x = (win_w - self.scaled_w) // 2
        self.offset_y = (win_h - self.scaled_h) // 2

    def _translate_mouse(self, pos):
        """Convert window mouse coords to logical coords."""
        lx = int((pos[0] - self.offset_x) / self.scale)
        ly = int((pos[1] - self.offset_y) / self.scale)
        lx = max(0, min(lx, LOGICAL_WIDTH - 1))
        ly = max(0, min(ly, LOGICAL_HEIGHT - 1))
        return (lx, ly)

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            raw_events = pygame.event.get()

            # Translate mouse positions to logical coordinates
            events = []
            for event in raw_events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE)
                    self._update_scaling()
                    continue
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    lpos = self._translate_mouse(event.pos)
                    if event.type == pygame.MOUSEMOTION:
                        new_event = pygame.event.Event(event.type,
                            pos=lpos, rel=event.rel, buttons=event.buttons)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        new_event = pygame.event.Event(event.type,
                            pos=lpos, button=event.button)
                    else:  # MOUSEBUTTONUP
                        new_event = pygame.event.Event(event.type,
                            pos=lpos, button=event.button)
                    events.append(new_event)
                else:
                    events.append(event)

            self.current_scene.handle_events(events)
            self.current_scene.update(dt)

            if self.current_scene.quit:
                self.running = False
                return

            if self.current_scene.done:
                self._switch_scene()

            self.current_scene.draw(self.logical_surface)
            scaled = pygame.transform.scale(
                self.logical_surface, (self.scaled_w, self.scaled_h)
            )
            self.screen.fill(COLOR_BG_DARK)
            self.screen.blit(scaled, (self.offset_x, self.offset_y))
            pygame.display.flip()
            await asyncio.sleep(0)

    def _switch_scene(self):
        next_name = self.current_scene.next_scene
        persistent = self.current_scene.cleanup()
        self.persistent.update(persistent)
        self.current_scene_name = next_name
        self.current_scene = self.scenes[next_name]
        self.current_scene.startup(self.persistent)
