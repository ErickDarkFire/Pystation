from typing import List
from models.card import Card

class Player:
    """Represents a Blackjack player.
    
    Attributes:
        money (int): The player's total available money for betting.
        hand (List[Card]): The cards the player currently holds.
        current_bet (int): The current bet placed in the active round.
    """
    
    def __init__(self, initial_money: int = 1000) -> None:
        self.money = initial_money
        self.hand: List[Card] = []
        self.current_bet = 0
        
    def reset_hand(self) -> None:
        """Clears the player's hand and resets the current bet for a new round."""
        self.hand.clear()
        self.current_bet = 0

class Dealer:
    """Represents the dealer in a Blackjack game.
    
    Attributes:
        hand (List[Card]): The cards the dealer currently holds.
    """
    
    def __init__(self) -> None:
        self.hand: List[Card] = []
        
    def reset_hand(self) -> None:
        """Clears the dealer's hand for a new round."""
        self.hand.clear()

