class Scene:
    """Abstract base class for all game scenes."""

    def __init__(self):
        self.done = False
        self.quit = False
        self.next_scene = None
        self.persistent = {}

    def startup(self, persistent):
        """Called when scene becomes active. Receives shared data dict."""
        self.persistent = persistent
        self.done = False
        self.quit = False
        self.next_scene = None

    def cleanup(self):
        """Called when scene is leaving. Returns data to pass forward."""
        return self.persistent

    def handle_events(self, events):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError
