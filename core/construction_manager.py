class ConstructionManager:
    def __init__(self, board):
        self.board = board  # Referência ao tabuleiro com encruzilhadas e caminhos

    def attempt_build_road(self, player, path_id) -> bool:
        """Valida e processa a compra e colocação de uma estrada."""
        path = self.board.get_path(path_id)

        # RF22: Verifica se a encruzilhada/caminho é adjacente a uma estrutura ou estrada própria válida
        if not self.board.is_valid_road_connection(path, player):
            return False

        # Tenta efetuar a compra deduzindo recursos no jogador
        if player.buy_road():
            path.occupy(player)
            return True
        return False

    def attempt_build_settlement(self, player, intersection_id) -> bool:
        """Valida e processa a compra e colocação de uma nova aldeia."""
        intersection = self.board.get_intersection(intersection_id)

        # RN10: Valida se as 3 encruzilhadas adjacentes estão livres
        if not self.board.respects_distance_rule(intersection):
            return False

        # RF23: Valida se chega pelo menos uma estrada do próprio jogador ao local
        if not self.board.has_connecting_road(intersection, player):
            return False

        # Tenta efetuar a compra deduzindo recursos e adicionando os pontos
        if player.buy_settlement():
            intersection.build_settlement(player)
            return True
        return False

    def attempt_upgrade_to_city(self, player, intersection_id) -> bool:
        """Valida e processa a elevação de uma aldeia a cidade."""
        intersection = self.board.get_intersection(intersection_id)

        # RF24: Garante que a encruzilhada possui uma aldeia pertencente ao jogador da vez
        if not intersection.has_player_settlement(player):
            return False

        # Efetiva o pagamento e o ajuste de pontuação
        if player.buy_city():
            intersection.upgrade_to_city()
            return True
        return False