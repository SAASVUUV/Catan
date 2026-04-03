import os
import math
import pygame
from .base_scene import BaseScene
from components.button import Button
import settings
from constants import colors as C
from components.selection_icons import PlayerSlot
  
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

        self.btn_start   = Button(bx, btn_y_start,                  bw, bh, "Iniciar Jogo",  28)
        self.btn_config  = Button(bx, btn_y_start + bh + gap,       bw, bh, "Configurações", 28)
        self.btn_quit    = Button(bx, btn_y_start + (bh + gap) * 2, bw, bh, "Sair do Jogo",  28)

    def _init_board_image(self):
        board_size = 300
        self.board_rect = pygame.Rect(self.screen_width - board_size - 30, 20, board_size, board_size)
        try:
            imagem_original = pygame.image.load("./assets/images/boardImage.png").convert_alpha()
            self.board_image = pygame.transform.smoothscale(imagem_original, (board_size, board_size))
        except FileNotFoundError:
            print("Aviso: Imagem do tabuleiro não encontrada. Criando placeholder vermelho.")
            self.board_image = pygame.Surface((board_size, board_size))
            self.board_image.fill((255, 0, 0))

    def _init_slots(self):
        slot_s = PlayerSlot.SIZE
        gap_s = 10
        grid_x = self.screen_width // 2 + 20
        grid_y = self.screen_height - (slot_s * 2 + gap_s) - 60
        self.slots = [
            PlayerSlot(grid_x, grid_y, 0),
            PlayerSlot(grid_x + slot_s + gap_s, grid_y, 1),
            PlayerSlot(grid_x, grid_y + slot_s + gap_s, 2),
            PlayerSlot(grid_x + slot_s + gap_s, grid_y + slot_s + gap_s, 3),
        ]
 
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
 
        if self.btn_start.handle_event(event):
            print("Iniciando Jogo...")
        if self.btn_config.handle_event(event):
            print("Abrindo Configurações...")
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
        top_y = 60

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