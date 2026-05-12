from abc import ABC, abstractmethod

class Buildable(ABC):
    def __init__(self):
        owner = getattr(self, 'owner', None)
        self.color = owner.color if owner else (180, 180, 180)

    @abstractmethod
    def try_build(self, player) -> bool:
        pass