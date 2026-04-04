import pygame
import os
import math
import pygame
from .base_scene import BaseScene
from components.button import Button
import settings
from constants import colors as C
from components.selection_icons import PlayerSlot

class Configurations(BaseScene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT

        self._load_fonts()
        self._init_buttons()

    def _load_fonts(self):
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        try:
            self.title_font = pygame.font.Font(caminho_fonte, 120)
            self.label_font = pygame.font.Font(caminho_fonte, 20)
        except FileNotFoundError:
            print("Fonte não encontrada! Usando fallback.")
            self.title_font = pygame.font.SysFont("serif", 100, bold=True)
            self.label_font = pygame.font.SysFont("serif", 20)

    def _init_buttons(self):

        W = self.screen_width 
        centro_alinhamento_x = W // 3.5

        bw, bh, gap = 250, 50, 10
        btn_y_start = 260

        bx = centro_alinhamento_x - (bw // 2)

        self.btn_sound_on = Button(bx, btn_y_start,                  bw, bh, "ON",  28)
        self.btn_sound_off = Button(220, self.screen_height - 120, 150, 50, "OFF", 24)

 
    def handle_event(self, event):
        pass
 
    def update(self, dt):
        self.btn_sound_on.update()
        self.btn_sound_off.update()
 
    def render(self, surface):
        self.btn_sound_on.render(surface)
        self.btn_sound_off.render(surface)

        surface.fill(C.BACKGROUND)