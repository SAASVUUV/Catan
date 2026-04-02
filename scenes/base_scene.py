from abc import ABC, abstractmethod
import pygame


class BaseScene(ABC):
    def __init__(self, manager=None):
        self.manager = manager

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass