import math
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT

# Tabela de Custos (RN24)
ROAD_COST = {BRICK: 1, TREE: 1}
VILLAGE_COST = {BRICK: 1, TREE: 1, LAMB: 1, WHEAT: 1}
CITY_COST = {ROCK: 3, WHEAT: 2}


class ConstructionManager:
    def __init__(self, tabletop):
        self.tabletop = tabletop

    def _points_match(self, x_a, y_a, x_b, y_b, tol=1.0):
        """Verifica a coincidência espacial de dois vértices tolerando imprecisões de ponto flutuante."""
        return math.hypot(x_a - x_b, y_a - y_b) < tol

    def get_adjacent_roads_to_house(self, house):
        """Obtém todas as arestas (estradas) conectadas a uma encruzilhada."""
        adj_roads = []
        for road in self.tabletop.roads:
            if (self._points_match(house.x, house.y, road.x0, road.y0) or
                    self._points_match(house.x, house.y, road.x1, road.y1)):
                adj_roads.append(road)
        return adj_roads

    def get_adjacent_houses_to_house(self, house):
        """Obtém as encruzilhadas diretamente vizinhas (1 salto de aresta) para validar a regra de distância."""
        adj_houses = []
        roads = self.get_adjacent_roads_to_house(house)
        for road in roads:
            # Identifica as coordenadas do extremo oposto
            target_x = road.x1 if self._points_match(house.x, house.y, road.x0, road.y0) else road.x0
            target_y = road.y1 if self._points_match(house.x, house.y, road.x0, road.y0) else road.y0

            for other_house in self.tabletop.houses:
                if other_house != house and self._points_match(target_x, target_y, other_house.x, other_house.y):
                    adj_houses.append(other_house)
                    break
        return adj_houses

    # -------------------------------------------------------------------------
    # COMPRA DE ESTRADA (RF09, RF21, RF22, RN24)
    # -------------------------------------------------------------------------
    def can_buy_road(self, player, road):
        if road.is_built:
            return False, "O local já possui uma estrada construída."

        if player.available_roads <= 0:
            return False, "Limite máximo de 15 estradas atingido (RF09)."

        if not player.has_resources(ROAD_COST):
            return False, "Recursos insuficientes para construir uma estrada (RN24)."

        # RF22: A estrada deve conectar-se a uma estrutura (aldeia/cidade) própria
        # OU a outra estrada própria, desde que não haja estrutura inimiga a bloquear a encruzilhada.
        endpoints = [(road.x0, road.y0), (road.x1, road.y1)]
        valid_connection = False

        for px, py in endpoints:
            current_house = None
            for h in self.tabletop.houses:
                if self._points_match(px, py, h.x, h.y):
                    current_house = h
                    break

            # Se a encruzilhada contiver uma aldeia/cidade de um oponente, o caminho está bloqueado
            if current_house and current_house.level > 0 and current_house.owner != player:
                continue

            # Válido se conectar a uma aldeia/cidade do próprio jogador
            if current_house and current_house.level > 0 and current_house.owner == player:
                valid_connection = True
                break

            # Válido se conectar a outra estrada do próprio jogador
            for other_road in self.tabletop.roads:
                if other_road != road and other_road.is_built and other_road.owner == player:
                    if (self._points_match(px, py, other_road.x0, other_road.y0) or
                            self._points_match(px, py, other_road.x1, other_road.y1)):
                        valid_connection = True
                        break

            if valid_connection:
                break

        if not valid_connection:
            return False, "A estrada deve ser adjacente a uma estrutura ou estrada própria sem bloqueios inimigos (RF22)."

        return True, "Compra válida."

    def buy_road(self, player, road):
        valid, msg = self.can_buy_road(player, road)
        if valid:
            player.deduct_resources(ROAD_COST)
            player.available_roads -= 1
            road.is_built = True
            road.owner = player
            return True, msg
        return False, msg

    # -------------------------------------------------------------------------
    # COMPRA DE ALDEIA (RF09, RF17, RF21, RF23, RN08, RN10, RN24)
    # -------------------------------------------------------------------------
    def can_buy_village(self, player, house):
        if house.level > 0:
            return False, "A encruzilhada já se encontra ocupada."

        if player.available_villages <= 0:
            return False, "Limite máximo de 5 aldeias atingido (RF09)."

        if not player.has_resources(VILLAGE_COST):
            return False, "Recursos insuficientes para construir uma aldeia (RN24)."

        # RN10: Regra de Distância - Nenhuma das 3 encruzilhadas adjacentes pode estar ocupada
        adj_houses = self.get_adjacent_houses_to_house(house)
        for adj_h in adj_houses:
            if adj_h.level > 0:
                return False, "Violação da Regra de Distância: existe uma estrutura numa encruzilhada adjacente (RN10)."

        # RF23: Deve chegar pelo menos uma estrada própria à encruzilhada
        has_own_road = False
        adj_roads = self.get_adjacent_roads_to_house(house)
        for r in adj_roads:
            if r.is_built and r.owner == player:
                has_own_road = True
                break

        if not has_own_road:
            return False, "É necessária a conexão de pelo menos uma estrada própria a esta encruzilhada (RF23)."

        return True, "Compra válida."

    def buy_village(self, player, house):
        valid, msg = self.can_buy_village(player, house)
        if valid:
            player.deduct_resources(VILLAGE_COST)
            player.available_villages -= 1
            house.level = 1
            house.owner = player
            # RF17, RN08: Atribuição de +1 ponto de vitória pela aldeia
            player.victory_points += 1
            return True, msg
        return False, msg

    # -------------------------------------------------------------------------
    # ELEVAÇÃO A CIDADE (RF09, RF17, RF21, RF24, RN08, RN24)
    # -------------------------------------------------------------------------
    def can_buy_city(self, player, house):
        if house.level != 1 or house.owner != player:
            return False, "Apenas é possível elevar uma aldeia própria já existente (RF24)."

        if player.available_cities <= 0:
            return False, "Limite máximo de 4 cidades atingido (RF09)."

        if not player.has_resources(CITY_COST):
            return False, "Recursos insuficientes para elevar a cidade (RN24)."

        return True, "Compra válida."

    def buy_city(self, player, house):
        valid, msg = self.can_buy_city(player, house)
        if valid:
            player.deduct_resources(CITY_COST)
            player.available_cities -= 1
            # A aldeia substituída regressa ao stock do jogador (RF09)
            player.available_villages += 1

            house.level = 2
            # RF17, RN08: Cidades valem 2 pontos. Como a aldeia já conferia 1 ponto, soma-se +1 ponto
            player.victory_points += 1
            return True, msg
        return False, msg