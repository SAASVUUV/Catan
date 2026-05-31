from systems.longest_road import calculate_longest_road

MIN_ROAD_LENGTH = 5
MIN_KNIGHTS = 3


class AchievementsManager:
    def __init__(self, players):
        self.players = players
        self.longest_road_holder = None
        self.largest_army_holder = None

    def update_longest_road(self, all_roads):
        """Recalcula quem detém a conquista de Maior Estrada."""
        best_player = None
        best_length = MIN_ROAD_LENGTH - 1

        for player in self.players:
            length = calculate_longest_road(player, all_roads)
            if length > best_length:
                best_length = length
                best_player = player

        if best_player != self.longest_road_holder:
            if self.longest_road_holder:
                self.longest_road_holder.has_longest_road = False
            if best_player:
                best_player.has_longest_road = True
            self.longest_road_holder = best_player

    def update_largest_army(self):
        """Recalcula quem detém a conquista de Maior Exército."""
        best_player = None
        best_count = MIN_KNIGHTS - 1

        for player in self.players:
            count = player.played_knights_count
            if count > best_count:
                best_count = count
                best_player = player

        if best_player != self.largest_army_holder:
            if self.largest_army_holder:
                self.largest_army_holder.has_largest_army = False
            if best_player:
                best_player.has_largest_army = True
            self.largest_army_holder = best_player
