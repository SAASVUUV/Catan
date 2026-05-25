import pygame
from components.modal import Modal
from components.button import Button
from constants.assets import VICTORY_POINT_CARDS_IMAGES
from constants.colors import BROWN_DARK
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class DevelopmentCardDialog(Modal):
    def __init__(self, player, on_cancel):
        width = int(SCREEN_WIDTH * 0.5)
        height = int(SCREEN_HEIGHT * 0.4)
        super().__init__(width, height, "Cartas de Desenvolvimento")
        self.player = player
        self.on_cancel = on_cancel

        self.cards = []
        self.card_images = []
        self._load_card_images()

        btn_w, btn_h = 100, 40
        btn_x = self.x + (self.width - btn_w) // 2
        btn_y = self.y + self.height - btn_h - 20
        self.btn_close = Button(btn_x, btn_y, btn_w, btn_h, "Fechar", on_click=self.on_cancel)

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 24)

    def _load_card_images(self):
        self.cards = self.player.victory_point_cards
        
        # Define a altura máxima da carta como 60% da altura do diálogo
        max_card_height = self.height * 0.6
        
        for card_name in self.cards:
            image_path = VICTORY_POINT_CARDS_IMAGES.get(card_name)
            if image_path:
                image = pygame.image.load(image_path)
                w, h = image.get_size()
                
                # Calcula a escala com base na altura máxima
                scale = max_card_height / h
                
                new_w = int(w * scale)
                new_h = int(h * scale)
                image = pygame.transform.scale(image, (new_w, new_h))
                self.card_images.append(image)

    def handle_event(self, event):
        if not self.visible:
            return False
        if self.btn_close.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_cancel()
            return True
        return super().handle_event(event)

    def update(self, dt):
        if not self.visible:
            return
        self.btn_close.update()

    def render(self, surface):
        if not self.visible:
            return
        super().render(surface)

        if not self.card_images:
            text_surf = self.font.render("Não há cartas!", True, BROWN_DARK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        else:
            total_width = sum(img.get_width() for img in self.card_images) + (len(self.card_images) - 1) * 10
            start_x = self.x + (self.width - total_width) // 2
            card_y = self.y + (self.height - self.card_images[0].get_height()) // 2

            for i, img in enumerate(self.card_images):
                surface.blit(img, (start_x + i * (img.get_width() + 10), card_y))

        self.btn_close.render(surface)
