from enum import Enum


class CardType(Enum):
    KNIGHT = "knight"
    PROGRESS = "progress"
    UNIVERSITY = "university"
    MARKET = "market"
    PALACE = "palace"
    CHAPEL = "chapel"
    LIBRARY = "library"
    VICTORY_POINT = "victory_point"
    ROAD_BUILDING = "road_building"
    YEAR_OF_PLENTY = "year_of_plenty"
    MONOPOLY = "monopoly"

    def __str__(self):
        return self.value
