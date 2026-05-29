from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT


class Bank:
    """Simple bank model holding counts of tradeable resources.

    By default it initializes with 19 of each resource (standard Catan).
    """

    def __init__(self, initial_count: int = 19):
        self._counts = {r: initial_count for r in (ROCK, TREE, LAMB, BRICK, WHEAT)}

    def has(self, resource: int, count: int = 1) -> bool:
        return self._counts.get(resource, 0) >= count

    def remove(self, resource: int, count: int = 1) -> bool:
        if not self.has(resource, count):
            return False
        self._counts[resource] -= count
        return True

    def add(self, resource: int, count: int = 1):
        self._counts[resource] = self._counts.get(resource, 0) + count

    def get_count(self, resource: int) -> int:
        return self._counts.get(resource, 0)
