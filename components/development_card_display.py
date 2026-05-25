import pygame

class DevelopmentCardDisplay:
    def __init__(self, x, y, scale=1.0, on_click=None):
        self.x = x
        self.y = y
        self.scale = scale
        self.on_click = on_click

        self.card_back_image = pygame.image.load("assets/images/cards/card-back.png")
        self.card_back_image = pygame.transform.scale(self.card_back_image, (int(60 * scale), int(90 * scale)))
        self.rect = self.card_back_image.get_rect(topleft=(x, y))
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def update(self):
        pass

    def render(self, surface):
        surface.blit(self.card_back_image, self.rect)
        if not self.enabled:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            surface.blit(overlay, self.rect.topleft)
