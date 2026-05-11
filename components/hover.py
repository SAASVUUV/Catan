import pygame

class Hover:

    def __init__(self, collidepoint, pointer=True, on_mouse_click=None):
        self.hovered = False
        self.mouse_in = False
        self.collidepoint = collidepoint
        self.pointer = pointer
        self.on_mouse_click = on_mouse_click
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_in = True if self.hovered else False
            self.hovered = self.collidepoint(event.pos)
            if(self.pointer and self.hovered and self.mouse_in): self.cursor_hover()
            elif(self.pointer and not self.hovered and self.mouse_in): self.cursor_default()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.collidepoint(event.pos):
            if(self.on_mouse_click): self.on_mouse_click()
            return True
        return False

    def update(self):
        self.hovered = self.collidepoint(pygame.mouse.get_pos())

    def cursor_hover(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    def cursor_default(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)