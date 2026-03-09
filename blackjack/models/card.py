from core.settings import WIDTH

class Card:
    """Represents a playing card in the Blackjack game.

    Attributes:
        suit (str): The suit of the card (e.g., '♠', '♥', '♦', '♣').
        rank (str): The rank of the card (e.g., '2', 'K', 'A').
        value (int): The numerical game value of the card.
        face_up (bool): Whether the card is facing up or down.
        width (int): Target width for UI rendering.
        height (int): Target height for UI rendering.
        x (float): Current X position for UI tracking.
        y (float): Current Y position for UI tracking.
        target_x (float): Target X position for animations.
        target_y (float): Target Y position for animations.
    """

    def __init__(self, suit: str, rank: str) -> None:
        """Initializes a Card with the specified suit and rank."""
        self.suit = suit
        self.rank = rank
        self.face_up = True
        
        # Numerical logic value
        if rank in ['J', 'Q', 'K']: 
            self.value = 10
        elif rank == 'A': 
            self.value = 11
        else: 
            self.value = int(rank)

        # UI Positioning properties (maintained here for easy animation interpolation)
        self.width = 110
        self.height = 160
        self.x = float(WIDTH - 100)
        self.y = 100.0
        self.target_x = self.x
        self.target_y = self.y

    def update(self) -> None:
        """Updates the card's position towards its defined target position to create an animation effect."""
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * 0.15

