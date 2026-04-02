import pygame
from .base_scene import BaseScene
from components.button import Button
import settings


class MainMenu(BaseScene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.title_font = pygame.font.SysFont("Arial", 48)

        self.btn_settings = Button(
            x=settings.SCREEN_WIDTH // 2 - 50,
            y=settings.SCREEN_HEIGHT - 160,
            width=104,
            height=36,
            text="Settings",
            font_size=18,
        )

        self.btn_enter = Button(
            x=settings.SCREEN_WIDTH // 2 - 100,
            y=settings.SCREEN_HEIGHT - 80,
            width=200,
            height=48,
            text="JOGAR",
            font_size=24,
        )

    def handle_event(self, event):
        if self.btn_settings.handle_event(event):
            print("Abrindo Settings...")

        if self.btn_enter.handle_event(event):
            print("Iniciando Jogo...")  

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            print("Iniciando Jogo...")

    def update(self, dt):
        self.btn_settings.update()
        self.btn_enter.update()

    def render(self, surface):
        surface.fill((30, 30, 30))

        title = self.title_font.render("Catan", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 60)))

        self.btn_settings.render(surface)
        self.btn_enter.render(surface)