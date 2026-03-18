from typing import List
from core.settings import WIDTH
from models.card import Card


def calculate_score(hand: List[Card]) -> int:
    """Calculates the best possible score for a Blackjack hand.

    Aces are counted as 11 unless the total score would exceed 21,
    in which case they automatically count as 1.

    Args:
        hand (List[Card]): A list of Card objects representing the hand.

    Returns:
        int: The evaluated score of the hand.
    """
    score = 0
    aces = 0
    for c in hand:
        score += c.value
        if c.rank == "A":
            aces += 1

    # Adjust for Aces if score is over 21
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1

    return score


def organize_hands(player_hand: List[Card], dealer_hand: List[Card]) -> None:
    """Calculates and assigns the UI target positions for the cards in play.

    Centers the cards horizontally for both the dealer and the player.

    Args:
        player_hand (List[Card]): The player's current hand.
        dealer_hand (List[Card]): The dealer's current hand.
    """
    if dealer_hand:
        start_x_dealer = (WIDTH - (len(dealer_hand) * 80)) // 2
        for i, c in enumerate(dealer_hand):
            c.target_x = float(start_x_dealer + i * 80)
            c.target_y = 150.0

    if player_hand:
        start_x_player = (WIDTH - (len(player_hand) * 80)) // 2
        for i, c in enumerate(player_hand):
            c.target_x = float(start_x_player + i * 80)
            c.target_y = 500.0


def get_strategy_advice(p_hand: List[Card], d_upcard: Card) -> str:
    """Provides Basic Strategy advice based on the player's hand and dealer's upcard.

    Args:
        p_hand (List[Card]): The player's hand.
        d_upcard (Card): The dealer's visible facing up card.

    Returns:
        str: Expected action string ("HIT", "STAND", "DOUBLE").
    """
    p_score = calculate_score(p_hand)
    d_val = d_upcard.value

    # Check if hand is "Soft" (contains an Ace counted as 11)
    is_soft = any(c.rank == "A" for c in p_hand) and sum(c.value for c in p_hand) <= 21

    if is_soft:
        if p_score >= 19:
            return "STAND"
        if p_score == 18:
            return "STAND" if d_val in [2, 7, 8] else "HIT"
        return "HIT"

    # "Hard" hand logic
    if p_score >= 17:
        return "STAND"
    if 13 <= p_score <= 16:
        return "STAND" if d_val <= 6 else "HIT"
    if p_score == 12:
        return "STAND" if d_val in [4, 5, 6] else "HIT"
    if p_score == 11:
        return "DOUBLE"
    if p_score == 10:
        return "DOUBLE" if d_val <= 9 else "HIT"
    if p_score == 9:
        return "DOUBLE" if d_val in [3, 4, 5, 6] else "HIT"

    return "HIT"
