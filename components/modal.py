import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from constants.colors import BEIGE_LIGHT, BROWN_DARK, BLACK
from utils.resources import resource_path

class Modal:
    def __init__(self, width: int, height: int, title: str = "", overlay_fullscreen: bool = True):
        self.width = width
        self.height = height
        self.title = title
        self.visible = False

        self.x = (SCREEN_WIDTH - width) // 2
        self.y = (SCREEN_HEIGHT - height) // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)

        self.bg_color = BEIGE_LIGHT
        self.border_color = BROWN_DARK
        self.overlay_color = (0, 0, 0, 150)
        # Controls whether the overlay darkens the full screen (including board)
        self.overlay_fullscreen = overlay_fullscreen

        caminho_fonte = resource_path('assets', 'fonts', 'MedievalSharp-Regular.ttf')
        self.title_font = pygame.font.Font(caminho_fonte, 24)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False
        return True

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        if self.overlay_fullscreen:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(self.overlay_color)
            surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=8)

        if self.title:
            title_surf = self.title_font.render(self.title, True, BROWN_DARK)
            title_rect = title_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top + 15)
            surface.blit(title_surf, title_rect)
