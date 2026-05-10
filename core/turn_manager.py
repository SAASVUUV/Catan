class TurnManager:
    def __init__(self, players):
        self.players = players
        self.is_setup_phase = True
        self.setup_order = list(range(len(players))) + list(range(len(players)-1, -1, -1))
        self.setup_index = 0
        self.normal_turn_index = 0

    @property
    def current_player(self):
        if self.is_setup_phase:
            return self.players[self.setup_order[self.setup_index]]
        return self.players[self.normal_turn_index]

    def next_turn(self):
        # Avança o turno respeitando a fase atual
        if self.is_setup_phase:
            self.setup_index += 1
            # Se terminou a lista da serpente, passa para a fase normal
            if self.setup_index >= len(self.setup_order):
                self.is_setup_phase = False
                self.normal_turn_index = 0
        else:
            self.normal_turn_index = (self.normal_turn_index + 1) % len(self.players)
        
        print(f"Próximo turno: {self.current_player.name} (Fase: {'Setup' if self.is_setup_phase else 'Normal'})")