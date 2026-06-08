import os
import math
import pygame
from .base_scene import BaseScene
from components.button import Button
import settings
from constants import colors as C
from components.selection_icons import PlayerSlot
import scenes.configurations as configurations
import scenes.game as game
from utils.resources import resource_path
  
class MainMenu(BaseScene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT

        self._load_fonts()
        self._init_buttons()
        self._init_board_image()
        self._init_slots()

    def _load_fonts(self):
        caminho_fonte = resource_path('assets', 'fonts', 'MedievalSharp-Regular.ttf')
        title_size = int(self.screen_height * 0.2)
        label_size = int(self.screen_height * 0.040)
        try:
            self.title_font = pygame.font.Font(caminho_fonte, title_size)
            self.label_font = pygame.font.Font(caminho_fonte, label_size)
        except FileNotFoundError:
            print("Fonte não encontrada! Usando fallback.")
            self.title_font = pygame.font.SysFont("serif", title_size, bold=True)
            self.label_font = pygame.font.SysFont("serif", label_size)

    def _init_buttons(self):
        W = self.screen_width
        H = self.screen_height
        centro_alinhamento_x = W // 3.5

        bw = int(W * 0.25)
        bh = int(H * 0.09)
        gap = int(H * 0.04)
        font_size = int(H * 0.05)
        btn_y_start = int(H * 0.3)

        bx = centro_alinhamento_x - (bw // 2)

        self.btn_start   = Button(bx, btn_y_start,                  bw, bh, "Iniciar Jogo",  font_size, shadow=True)
        self.btn_config  = Button(bx, btn_y_start + bh + gap,       bw, bh, "Configurações", font_size, shadow=True)
        self.btn_quit    = Button(bx, btn_y_start + (bh + gap) * 2, bw, bh, "Sair do Jogo",  font_size, shadow=True)

    def _init_board_image(self):
        board_size = int(self.screen_height * 0.55)
        margin = int(self.screen_width * 0.03)
        top_margin = int(self.screen_height * 0.08)
        self.board_rect = pygame.Rect(self.screen_width - board_size - margin, top_margin, board_size, board_size)
        try:
            imagem_original = pygame.image.load(resource_path('assets', 'images', 'boardImage.png')).convert_alpha()
            self.board_image = pygame.transform.smoothscale(imagem_original, (board_size, board_size))
        except FileNotFoundError:
            print("Aviso: Imagem do tabuleiro não encontrada. Criando placeholder vermelho.")
            self.board_image = pygame.Surface((board_size, board_size))
            self.board_image.fill((255, 0, 0))

    def _init_slots(self):
        slot_s = int(self.screen_height * 0.12)
        gap_s = int(self.screen_height * 0.015)
        grid_x = int(self.screen_width * 0.45)
        grid_y = self.screen_height - (slot_s * 2 + gap_s) - int(self.screen_height * 0.08)
        self.slots = [
            PlayerSlot(grid_x, grid_y, 0, slot_s),
            PlayerSlot(grid_x + slot_s + gap_s, grid_y, 1, slot_s),
            PlayerSlot(grid_x, grid_y + slot_s + gap_s, 2, slot_s),
            PlayerSlot(grid_x + slot_s + gap_s, grid_y + slot_s + gap_s, 3, slot_s),
        ]
 
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
 
        if self.btn_start.handle_event(event):
            bot_list = []
            for slot in self.slots:
                if slot.is_bot:
                    bot_list.append(slot.index + 1)
            self.manager.replace(game.Game(self.manager, bot_list=bot_list))
        if self.btn_config.handle_event(event):
            self.manager.replace(configurations.Configurations(self.manager))
        if self.btn_quit.handle_event(event):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
 
        for slot in self.slots:
            slot.handle_event(event)
 
    def update(self, dt):
        self.btn_start.update()
        self.btn_config.update()
        self.btn_quit.update()
        for slot in self.slots:
            slot.update()
 
    def render(self, surface):
        surface.fill(C.BACKGROUND)

        texto_sombra = self.title_font.render("CATAN", True, C.TEXT_TITLE_SHADOW)
        texto_titulo = self.title_font.render("CATAN", True, C.TEXT_TITLE)

        title_center_x = self.screen_width // 3.5
        top_y = int(self.screen_height * 0.08)

        surface.blit(texto_sombra, texto_sombra.get_rect(centerx=title_center_x + 4, top=top_y + 4))
        surface.blit(texto_titulo, texto_titulo.get_rect(centerx=title_center_x, top=top_y))
 
        surface.blit(self.board_image, self.board_rect.topleft) 
        
        self.btn_start.render(surface)
        self.btn_config.render(surface)
        self.btn_quit.render(surface)
 
        for slot in self.slots:
            slot.render(surface)
 
        grid_bottom = self.slots[2].rect.bottom
        lbl = self.label_font.render("Clique para alternar bot <-> jogador", True, C.TEXT_BODY)
        grid_cx = (self.slots[0].rect.left + self.slots[1].rect.right) // 2
        surface.blit(lbl, lbl.get_rect(centerx=grid_cx, top=grid_bottom + 10))