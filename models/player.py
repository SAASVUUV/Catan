import pygame
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT
from models.inventory import Inventory


class Player:
    def __init__(self, player_id: int, name: str, color: tuple):
        self.id = player_id
        self.name = name
        self.color = color

        # Contagem de estruturas ativas no tabuleiro
        self.settlements_count = 0
        self.cities_count = 0
        self.roads_count = 0

        # Pontos de vitória acumulados
        self.victory_points = 0

        # Inventário de matérias-primas
        self.inventory = Inventory()

    # --- VERIFICAÇÃO DE FASE DO JOGO ---
    def is_in_setup_phase(self) -> bool:
        """
        RN17: Retorna True se o jogador ainda estiver posicionando
        as suas 2 aldeias e 2 estradas iniciais gratuitas.
        """
        return self.settlements_count < 2 or self.roads_count < 2

    # --- VALIDAÇÃO DE LIMITES DE PEÇAS (RF09) ---
    def can_build_settlement(self, max_limit: int = 5) -> bool:
        return self.settlements_count < max_limit

    def can_build_city(self, max_limit: int = 4) -> bool:
        return self.cities_count < max_limit

    def can_build_road(self, max_limit: int = 15) -> bool:
        return self.roads_count < max_limit

    # --- VALIDAÇÃO DE CUSTOS DE MATÉRIA-PRIMA (RN24) ---
    def has_resources_for_road(self) -> bool:
        return self.inventory.has(BRICK, 1) and self.inventory.has(TREE, 1)

    def has_resources_for_settlement(self) -> bool:
        return (self.inventory.has(BRICK, 1) and
                self.inventory.has(TREE, 1) and
                self.inventory.has(LAMB, 1) and
                self.inventory.has(WHEAT, 1))

    def has_resources_for_city(self) -> bool:
        return self.inventory.has(ROCK, 3) and self.inventory.has(WHEAT, 2)

    # --- AÇÕES PURAS DE ESTADO (Usadas no Setup) ---
    def add_road(self):
        self.roads_count += 1

    def add_settlement(self):
        self.settlements_count += 1
        self.victory_points += 1

    def upgrade_to_city(self):
        self.settlements_count -= 1
        self.cities_count += 1
        self.victory_points += 1  # Ganho líquido de +1 ponto (aldeia vale 1, cidade vale 2)

    # --- AÇÕES FINANCEIRAS / COMPRA (Fase Principal - RF21) ---
    def buy_road(self, max_limit: int = 15) -> bool:
        if self.can_build_road(max_limit) and self.has_resources_for_road():
            self.inventory.remove(BRICK, 1)
            self.inventory.remove(TREE, 1)
            self.add_road()
            return True
        return False

    def buy_settlement(self, max_limit: int = 5) -> bool:
        if self.can_build_settlement(max_limit) and self.has_resources_for_settlement():
            self.inventory.remove(BRICK, 1)
            self.inventory.remove(TREE, 1)
            self.inventory.remove(LAMB, 1)
            self.inventory.remove(WHEAT, 1)
            self.add_settlement()
            return True
        return False

    def buy_city(self, max_limit: int = 4) -> bool:
        if self.settlements_count > 0 and self.can_build_city(max_limit) and self.has_resources_for_city():
            self.inventory.remove(ROCK, 3)
            self.inventory.remove(WHEAT, 2)
            self.upgrade_to_city()
            return True
        return False