import random
from typing import List

from models.card import Card


class Shoe:
    """Represents a casino-style shoe containing multiple decks of cards.

    Attributes:
        cards (List[Card]): The remaining cards in the shoe.
        num_decks (int): The number of decks in the shoe.
    """

    SUITS = ("♠", "♥", "♦", "♣")
    RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")

    def __init__(self, num_decks: int = 6) -> None:
        """Initializes the Shoe with a specified number of decks.

        Args:
            num_decks (int): Number of standard 52-card decks to use. Defaults to 6.
        """
        self.num_decks: int = num_decks
        self.cards: List[Card] = []
        self.build()

    def build(self) -> None:
        """Builds the shoe with the specified number of decks and shuffles them."""
        self.cards = [
            Card(suit, rank)
            for _ in range(self.num_decks)
            for suit in self.SUITS
            for rank in self.RANKS
        ]
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        """Draws a card from the shoe. Rebuilds the shoe if it's empty.

        Returns:
            Card: The drawn card object.
        """
        if not self.cards:
            self.build()
        return self.cards.pop()
