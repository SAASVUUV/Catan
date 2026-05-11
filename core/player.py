import pygame
from core.inventory import Inventory
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT

class Player:
    def __init__(self, player_id: int, name: str, color: tuple):
        self.id = player_id
        self.name = name
        self.color = color
        self.settlements_count = 0
        self.cities_count = 0
        self.roads_count = 0
        self.inventory = Inventory()

    def can_build_settlement(self, max_limit: int) -> bool:
        return self.settlements_count < max_limit

    def can_build_city(self, max_limit: int) -> bool:
        return self.cities_count < max_limit

    def can_build_road(self, max_limit: int) -> bool:
        return self.roads_count < max_limit

    def add_settlement(self):
        self.settlements_count += 1

    def upgrade_to_city(self):
        self.settlements_count -= 1
        self.cities_count += 1

    def add_road(self):
        self.roads_count += 1

    def has_resources_for_settlement(self) -> bool:
        return self.inventory.has_multiple({BRICK: 1, TREE: 1, LAMB: 1, WHEAT: 1})

    def has_resources_for_city(self) -> bool:
        return self.inventory.has_multiple({ROCK: 3, WHEAT: 2})

    def has_resources_for_road(self) -> bool:
        return self.inventory.has_multiple({BRICK: 1, TREE: 1})