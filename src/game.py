import pygame
from src.settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    FPS, SCALE_FACTOR
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

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            raw_events = pygame.event.get()

            # Translate mouse positions to logical coordinates
            events = []
            for event in raw_events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    # Scale mouse coords from window space to logical space
                    lx = event.pos[0] // SCALE_FACTOR
                    ly = event.pos[1] // SCALE_FACTOR
                    # Create a new event with scaled pos since event.pos is read-only
                    if event.type == pygame.MOUSEMOTION:
                        new_event = pygame.event.Event(event.type,
                            pos=(lx, ly), rel=event.rel, buttons=event.buttons)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        new_event = pygame.event.Event(event.type,
                            pos=(lx, ly), button=event.button)
                    else:  # MOUSEBUTTONUP
                        new_event = pygame.event.Event(event.type,
                            pos=(lx, ly), button=event.button)
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
                self.logical_surface, (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()

    def _switch_scene(self):
        next_name = self.current_scene.next_scene
        persistent = self.current_scene.cleanup()
        self.persistent.update(persistent)
        self.current_scene_name = next_name
        self.current_scene = self.scenes[next_name]
        self.current_scene.startup(self.persistent)
