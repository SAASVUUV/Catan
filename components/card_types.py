from enum import Enum


class CardType(Enum):
    KNIGHT = "knight"
    PROGRESS = "progress"
    VICTORY_POINT = "victory_point"

    def __str__(self):
        return self.value
