"""Bot AI decision system for Catan."""

import random
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT


class BotDecisionMaker:
    """Makes decisions for AI-controlled players."""
    
    def __init__(self, player):
        self.player = player
    
    # ========== TRADING ==========
    
    def should_accept_trade_offer(self, offer) -> bool:
        """Decide whether to accept a trade offer from another player."""
        # Check if can even accept
        for resource, count in offer.requesting.items():
            if not self.player.inventory.has(resource, count):
                return False
        
        # Evaluate trade value
        # Score high-value resources (WHEAT, ROCK) more
        def score_resources(res_dict):
            score = 0
            for resource, count in res_dict.items():
                if resource in [WHEAT, ROCK]:
                    score += count * 2
                else:
                    score += count * 1
            return score
        
        offering_score = score_resources(offer.offering)
        requesting_score = score_resources(offer.requesting)
        
        # Accept if offering is better value
        if offering_score > requesting_score:
            return True
        
        # Check if offering fills critical need
        for resource in offer.offering.keys():
            if resource in [WHEAT, ROCK] and self.player.inventory.get_count(resource) == 0:
                return True
        
        return False
    
    def get_bank_trade(self, ports: list):
        """Suggest a bank trade if beneficial. Returns (give_type, give_count, receive_type) or None."""
        from core.trade import BankTrade
        
        # If has more than 7 of same type, offer 4:1 trade
        most_abundant = self.player.get_most_abundant_resource()
        if most_abundant and self.player.inventory.get_count(most_abundant) > 7:
            # Find resource with least cards
            least_abundant = self.player.get_least_abundant_resource()
            if least_abundant and least_abundant != most_abundant:
                # Check if bank trade is possible
                ratio = BankTrade.get_ratio(self.player, most_abundant, ports)
                if self.player.inventory.get_count(most_abundant) >= ratio:
                    return (most_abundant, ratio, least_abundant)
        
        return None
    
    def should_make_4_for_3_trade(self) -> tuple | None:
        """If has >7 of same resource, offer 4 for 3 of least abundant. 
        Returns (give_type, give_count, receive_type) or None."""
        
        # Find resource with most cards (>7)
        counts = self.player.get_resource_counts()
        most_abundant = max(counts.items(), key=lambda x: x[1]) if counts else None
        
        if not most_abundant or most_abundant[1] <= 6:
            return None
        
        # Find least abundant resource (that we have at least 1)
        least_abundant = self.player.get_least_abundant_resource()
        if not least_abundant or least_abundant == most_abundant[0]:
            return None
        
        # Return trade offer: 4 of most abundant for 3 of least abundant
        return (most_abundant[0], 3, least_abundant, 2)
    
    # ========== BUILDING ==========
    
    def should_build_settlement(self) -> bool:
        """Decide if should build a settlement."""
        return (self.player.can_build_settlement(5) and 
                self.player.has_resources_for_settlement())
    
    def should_build_road(self) -> bool:
        """Decide if should build a road."""
        return (self.player.can_build_road(15) and 
                self.player.has_resources_for_road())
    
    def should_build_city(self) -> bool:
        """Decide if should upgrade a settlement to city."""
        return (self.player.can_build_city(4) and 
                self.player.settlements_count > 0 and
                self.player.has_resources_for_city())
    
    # ========== DEVELOPMENT CARDS ==========
    
    def should_buy_development_card(self, turn_number: int) -> bool:
        """Decide if should buy a development card."""
        if not self.player.has_resources_for_dev_card():
            return False
        
        # Buy if hasn't bought in more than 2 turns
        if self.player.turns_since_last_dev_card > 2:
            return True
        
        # Buy if high resource surplus
        if self.player.inventory.total() > 9:
            return True
        
        return False
    
    def should_play_knight(self, robber_tile=None) -> bool:
        """Decide if should play a knight card."""
        # Prefer to play if can get largest army (2+ knights already played)
        if self.player.knights_played >= 2:
            return True
        
        # Play if robber is on a tile with opponent settlements
        if robber_tile:
            for house in robber_tile.extract_houses():
                if house.owner and house.owner != self.player and house.level > 0:
                    return True
        
        return False
    
    # ========== ROBBER ==========
    
    def select_robber_victim(self, candidates: list):
        """Select a random player to steal from among valid candidates."""
        if not candidates:
            return None
        return random.choice(candidates)
    
    def select_robber_tile(self, available_tiles: list):
        """Select best tile to move robber to (with opponent settlements)."""
        if not available_tiles:
            return None
        
        best_tile = None
        best_score = -1
        
        for tile in available_tiles:
            score = 0
            for house in tile.extract_houses():
                if house.owner and house.owner != self.player and house.level > 0:
                    if house.level == 2:  # City
                        score += 2
                    else:  # Settlement
                        score += 1
            
            if score > best_score:
                best_score = score
                best_tile = tile
        
        # If no tile with opponents, choose random
        return best_tile or random.choice(available_tiles)
    
    def select_discard_resources(self, discard_count: int) -> dict:
        """Select which resources to discard when >7 cards."""
        # Priority: keep high-value resources (WHEAT, ROCK)
        priority = {
            TREE: 1,
            LAMB: 1,
            BRICK: 2,
            WHEAT: 3,
            ROCK: 3,
        }
        
        discarding = {}
        to_discard = discard_count
        
        # Discard in reverse priority order
        for resource in sorted(priority.keys(), key=lambda r: priority[r]):
            count = self.player.inventory.get_count(resource)
            if count > 0 and to_discard > 0:
                discard_amount = min(count, to_discard)
                discarding[resource] = discard_amount
                to_discard -= discard_amount
        
        return discarding
