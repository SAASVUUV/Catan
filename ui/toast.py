import time
import pygame


class ToastManager:
    def __init__(self):
        self.items = []  # list of (message, expire_time)
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        try:
            self.font = pygame.font.Font(caminho_fonte, 18)
        except Exception:
            self.font = pygame.font.SysFont("Arial", 18)

    def show(self, message: str, duration: float = 2.5):
        expires = time.time() + duration
        self.items.append((message, expires))

    def update(self, dt: float = None):
        now = time.time()
        self.items = [(m, e) for (m, e) in self.items if e > now]

    def render(self, surface: pygame.Surface):
        if not self.items:
            return
        # render the last message centered near the top
        message = self.items[-1][0]
        txt = self.font.render(message, True, (255, 255, 255))
        pad_x = 12
        pad_y = 8
        w = txt.get_width() + pad_x * 2
        h = txt.get_height() + pad_y * 2
        x = (surface.get_width() - w) // 2
        y = 20
        # semi-transparent background
        s = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        s.fill((10, 10, 10, 200))
        pygame.draw.rect(s, (255, 255, 255), s.get_rect(), width=1, border_radius=6)
        surface.blit(s, (x, y))
        surface.blit(txt, (x + pad_x, y + pad_y))
