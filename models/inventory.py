from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT

TRADEABLE_RESOURCES = [ROCK, TREE, LAMB, BRICK, WHEAT]

class Inventory:
    def __init__(self):
        self.cards = {r: 0 for r in TRADEABLE_RESOURCES}

    def add(self, resource: int, count: int = 1):
        if resource in self.cards:
            self.cards[resource] += count

    def remove(self, resource: int, count: int = 1) -> bool:
        if not self.has(resource, count):
            return False
        self.cards[resource] -= count
        return True

    def has(self, resource: int, count: int = 1) -> bool:
        return self.cards.get(resource, 0) >= count

    def has_multiple(self, resources: dict) -> bool:
        return all(self.has(r, c) for r, c in resources.items())

    def get_count(self, resource: int) -> int:
        return self.cards.get(resource, 0)

    def total(self) -> int:
        return sum(self.cards.values())
