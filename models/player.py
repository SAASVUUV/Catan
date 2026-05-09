from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color

        # Custos e inventário inicial (RN24, RF21)
        self.resources = {
            ROCK: 0,
            TREE: 0,
            LAMB: 0,
            BRICK: 0,
            WHEAT: 0
        }

        # RF09: Limite estrito de figuras de construção por jogador
        self.available_roads = 15
        self.available_villages = 5
        self.available_cities = 4

        # RF17, RN08: Pontos de Vitória acumulados
        self.victory_points = 0

    def has_resources(self, cost):
        """Verifica se o jogador possui a quantidade necessária de recursos."""
        for resource_type, amount in cost.items():
            if self.resources.get(resource_type, 0) < amount:
                return False
        return True

    def deduct_resources(self, cost):
        """Deduz os recursos do inventário após validação da compra."""
        if self.has_resources(cost):
            for resource_type, amount in cost.items():
                self.resources[resource_type] -= amount