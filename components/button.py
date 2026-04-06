import pygame

class Button:
    def __init__(self, x, y, width, height, text, font_size=20, bg_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.hovered = False
        self.mouse_in = False

        self.bg_image = pygame.transform.smoothscale(bg_image, (width, height)) if bg_image else None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_in = True if self.hovered else False
            self.hovered = self.rect.collidepoint(event.pos)
            if(self.hovered and self.mouse_in): self.cursor_hover()
            elif(not self.hovered and self.mouse_in): self.cursor_default()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def cursor_hover(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    def cursor_default(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def update(self):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, self.rect.topleft)
        else:
            color = (100, 100, 100) if self.hovered else (70, 70, 70)
            pygame.draw.rect(surface, color, self.rect, border_radius=6)

        text_color = (218, 165, 32) if self.hovered else (255, 255, 255)
        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))