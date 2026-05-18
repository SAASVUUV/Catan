import random
from constants.phases import TurnPhase


class TurnManager:
    def __init__(self, players):
        self.players = players
        self.is_setup_phase = True
        self.setup_order = list(range(len(players))) + list(range(len(players)-1, -1, -1))
        self.setup_index = 0
        self.setup_built_house = False
        self.setup_built_road = False
        self.normal_turn_index = 0
        self.current_phase = TurnPhase.CONSTRUCTION
        self.last_dice_roll = None

    def setup_record_house(self):
        self.setup_built_house = True

    def setup_record_road(self):
        self.setup_built_road = True

    def setup_turn_complete(self) -> bool:
        return self.setup_built_house and self.setup_built_road

    def _reset_setup_turn(self):
        self.setup_built_house = False
        self.setup_built_road = False

    def shuffle_player_order(self):
        random.shuffle(self.players)

    @property
    def current_player(self):
        if self.is_setup_phase:
            return self.players[self.setup_order[self.setup_index]]
        return self.players[self.normal_turn_index]

    @property
    def dice_sum(self):
        if self.last_dice_roll:
            return self.last_dice_roll[0] + self.last_dice_roll[1]
        return 0

    def roll_dice(self):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.last_dice_roll = (die1, die2)
        self.current_phase = TurnPhase.COMMERCE
        return self.last_dice_roll

    def next_phase(self):
        if self.current_phase == TurnPhase.COMMERCE:
            self.current_phase = TurnPhase.CONSTRUCTION
        elif self.current_phase == TurnPhase.CONSTRUCTION:
            self.next_turn()

    def next_turn(self):
        if self.is_setup_phase:
            self._reset_setup_turn()
            self.setup_index += 1
            if self.setup_index >= len(self.setup_order):
                self.is_setup_phase = False
                self.normal_turn_index = 0
                self.current_phase = TurnPhase.DICE
                self.last_dice_roll = None
        else:
            self.normal_turn_index = (self.normal_turn_index + 1) % len(self.players)
            self.current_phase = TurnPhase.DICE
            self.last_dice_roll = None