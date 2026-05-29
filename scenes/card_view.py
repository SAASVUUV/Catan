import pygame
from constants.colors import BLACK, RED
from components.card_states import CardState

# Cores locais para evitar quebra de referência em constants.colors
BROWN_DARK = (92, 64, 51)
BEIGE_LIGHT = (245, 245, 220)
GOLD = (255, 215, 0)

class CardView:
    def __init__(self, card, x, y, width=100, height=140):
        self.card = card
        self.rect = pygame.Rect(x, y, width, height)
        
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        try:
            self.font = pygame.font.Font(caminho_fonte, 12)
            self.title_font = pygame.font.Font(caminho_fonte, 14)
        except:
            self.font = pygame.font.SysFont("Arial", 12)
            self.title_font = pygame.font.SysFont("Arial", 14)
            
        self.is_hovered = False
        self.is_selected = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
    def render(self, surface):
        bg_color = BEIGE_LIGHT
        border_color = BROWN_DARK
        
        if self.card.state == CardState.LOCKED:
            bg_color = (200, 200, 200)
            border_color = (150, 150, 150)
        elif self.card.state == CardState.USED:
            bg_color = (160, 160, 160)
            border_color = (100, 100, 100)
            
        if self.is_hovered and self.card.state != CardState.USED:
            border_color = GOLD
            
        if self.is_selected:
            pygame.draw.rect(surface, GOLD, self.rect.inflate(4, 4), border_radius=5)
            
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=5)
        
        # Título
        title = self.title_font.render(self.card.name, True, BLACK)
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Estado
        state_text = self.font.render(self.card.state.value, True, (80, 80, 80))
        surface.blit(state_text, (self.rect.x + 5, self.rect.y + 25))

        if self.card.state == CardState.USED:
            used_indicator = self.font.render("USADA", True, RED)
            surface.blit(used_indicator, (self.rect.x + 5, self.rect.y + self.rect.height - 20))
        
        if self.is_hovered:
            self._render_tooltip(surface)

    def _render_tooltip(self, surface):
        tooltip_width = 180
        tooltip_height = 60
        if self.card.state == CardState.LOCKED:
            tooltip_height += 20
            
        tooltip_rect = pygame.Rect(self.rect.x, self.rect.y - tooltip_height - 5, tooltip_width, tooltip_height)
        if tooltip_rect.right > surface.get_width(): tooltip_rect.right = surface.get_width() - 5
        if tooltip_rect.top < 0: tooltip_rect.top = self.rect.bottom + 5
            
        pygame.draw.rect(surface, (40, 40, 40, 240), tooltip_rect, border_radius=5)
        pygame.draw.rect(surface, GOLD, tooltip_rect, width=1, border_radius=5)
        
        surface.blit(self.title_font.render(self.card.name, True, GOLD), (tooltip_rect.x + 5, tooltip_rect.y + 5))
        surface.blit(self.font.render(self.card.description, True, (220, 220, 220)), (tooltip_rect.x + 5, tooltip_rect.y + 25))
        
        if self.card.state == CardState.LOCKED:
            surface.blit(self.font.render("Bloqueada (Comprada neste turno)", True, (255, 100, 100)), (tooltip_rect.x + 5, tooltip_rect.y + 45))
        elif self.card.state == CardState.USED:
            surface.blit(self.font.render("Carta já utilizada", True, (255, 200, 100)), (tooltip_rect.x + 5, tooltip_rect.y + 45))