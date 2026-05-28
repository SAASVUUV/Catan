import pygame
from .circle import Circle
from constants.colors import *

class Slider:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.slide_bar_color = BROWN_DARK
        self.slide_bar_rect = pygame.Rect(x, y, w, h)
        self.hovered = False
        self.mouse_in = False
        self.click = False
        self.circle = Circle(
            x,
            y + h/2,
            self.h * 2,
            BLUE_BRIGHT,
        )
        self.percent = 0

    def cursor_hover(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    def cursor_default(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_in = True if self.hovered else False
            self.hovered = self.circle.collidepoint(event.pos)
            if(self.hovered and self.mouse_in): self.cursor_hover()
            elif(not self.hovered and self.mouse_in): self.cursor_default()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if(self.hovered):
                self.click = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.click = False
    
    def update(self):
        if(self.click):
            x,_ = pos = pygame.mouse.get_pos()
            self.circle.x = x if self.x <= x <= self.x + self.w else (self.x if x <= self.x else self.x + self.w)
            self.percent = (self.circle.x - self.x) / self.w

    def render(self, surface):
        pygame.draw.rect(surface, self.slide_bar_color, self.slide_bar_rect)
        self.circle.render(surface)