import pytest
from models.player import Player
from components.base_card import BaseCard
from components.card_types import CardType
from components.card_states import CardState
from systems.card_manager import CardManager
from constants.types import ROCK, LAMB, WHEAT

def test_buy_development_card_deducts_resources():
    player = Player(1, "Test Player", (255, 0, 0))
    manager = CardManager([player])
    
    # Adiciona a quantidade exata de recursos para 1 carta
    player.inventory.add(ROCK, 1)
    player.inventory.add(LAMB, 1)
    player.inventory.add(WHEAT, 1)
    
    success = manager.attempt_buy_card(player)
    
    assert success is True
    assert len(player.development_cards) == 1
    assert player.inventory.get_count(ROCK) == 0
    assert player.inventory.get_count(LAMB) == 0
    assert player.inventory.get_count(WHEAT) == 0

def test_buy_development_card_fails_without_resources():
    player = Player(1, "Test Player", (255, 0, 0))
    manager = CardManager([player])
    
    # Recursos insuficientes
    player.inventory.add(ROCK, 1)
    
    success = manager.attempt_buy_card(player)
    
    assert success is False
    assert len(player.development_cards) == 0

def test_newly_bought_card_is_locked():
    player = Player(1, "Test Player", (255, 0, 0))
    card = BaseCard("Knight", "Desc", CardType.KNIGHT)
    
    player.add_development_card(card)
    
    assert card.state == CardState.LOCKED
    assert card.bought_this_turn is True
    
    can_act, reason = card.can_activate(has_played_card_this_turn=False)
    assert can_act is False
    assert "não está pronta" in reason or "recém-compradas" in reason

def test_card_becomes_ready_next_turn():
    player = Player(1, "Test Player", (255, 0, 0))
    manager = CardManager([player])
    card = BaseCard("Knight", "Desc", CardType.KNIGHT)
    
    player.add_development_card(card)
    manager.on_turn_start(player)  # Simula rotação/início do próximo turno
    
    assert card.state == CardState.READY
    assert card.bought_this_turn is False
    
    can_act, reason = card.can_activate(has_played_card_this_turn=False)
    assert can_act is True

def test_cannot_play_multiple_cards_per_turn():
    player = Player(1, "Test Player", (255, 0, 0))
    manager = CardManager([player])
    card1 = BaseCard("Card 1", "Desc", CardType.KNIGHT)
    card2 = BaseCard("Card 2", "Desc", CardType.PROGRESS)
    
    player.add_development_card(card1)
    player.add_development_card(card2)
    
    manager.on_turn_start(player)
    
    success = manager.attempt_activate_card(player, card1)
    assert success is True
    assert card1.state == CardState.USED
    
    success2 = manager.attempt_activate_card(player, card2)
    assert success2 is False
    assert card2.state == CardState.READY  # A carta 2 permanece pronta