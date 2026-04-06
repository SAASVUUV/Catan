from .button import Button
import pygame

class Checkbox(Button):

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "")
        self.check = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_in = True if self.hovered else False
            self.hovered = self.rect.collidepoint(event.pos)
            if(self.hovered and self.mouse_in): self.cursor_hover()
            elif(not self.hovered and self.mouse_in): self.cursor_default()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.text = "" if self.check else "X"
                self.check = not self.check
                return True
        return False