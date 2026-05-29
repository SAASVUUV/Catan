import sys
import types

# Minimal fake pygame module for test environment (avoid requiring pygame install)
pygame = types.ModuleType('pygame')
pygame.init = lambda *a, **k: None
pygame.quit = lambda *a, **k: None
pygame.SYSTEM_CURSOR_ARROW = 0

class DummyFont:
    def __init__(self, *a, **k):
        pass

    def render(self, *a, **k):
        return None


pygame.font = types.SimpleNamespace(Font=lambda *a, **k: DummyFont(), SysFont=lambda *a, **k: DummyFont())

class DummyRect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.left = x
        self.top = y
        self.width = w
        self.height = h
        self.right = x + w
        self.bottom = y + h
        self.centerx = x + (w // 2)
        self.centery = y + (h // 2)

    def collidepoint(self, pos):
        try:
            px, py = pos
        except Exception:
            return False
        return self.left <= px <= self.right and self.top <= py <= self.bottom

    def get_rect(self, **kwargs):
        return self

class DummySurface:
    def __init__(self, size=(0, 0), flags=None):
        self._size = size

    def convert_alpha(self):
        return self

    def get_size(self):
        return self._size

    def copy(self):
        return DummySurface(self._size)

    def fill(self, *a, **k):
        return None

    def blit(self, *a, **k):
        return None

    def get_rect(self, **kwargs):
        return DummyRect(0, 0, self._size[0], self._size[1])

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

pygame.Surface = lambda size, flags=None: DummySurface(size)
pygame.Rect = DummyRect
pygame.mouse = types.SimpleNamespace(get_pos=lambda: (0, 0), set_cursor=lambda *a, **k: None)
class Event:
    pass
pygame.event = types.SimpleNamespace(Event=Event)
pygame.image = types.SimpleNamespace(load=lambda path: DummySurface((64, 64)))
pygame.error = Exception
pygame.transform = types.SimpleNamespace(smoothscale=lambda surf, size: DummySurface(size), rotate=lambda base, ang: base)
pygame.display = types.SimpleNamespace(Info=lambda: types.SimpleNamespace(current_w=800, current_h=600))

sys.modules['pygame'] = pygame
