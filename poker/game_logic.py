
import random
from enum import Enum, auto
from itertools import combinations



SUITS = ("Hearts", "Diamonds", "Clubs", "Spades")
RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}  # 2=2 … A=14

SUIT_SYMBOLS = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}



class Card:
    """Represents a single playing card."""

    def __init__(self, rank: str, suit: str):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __repr__(self):
        return f"{self.rank}{SUIT_SYMBOLS[self.suit]}"

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    """Standard 52-card deck."""

    def __init__(self):
        self.cards: list[Card] = [Card(r, s) for s in SUITS for r in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)
        return self

    def deal(self, n: int = 1) -> list[Card]:
        if n > len(self.cards):
            raise ValueError("Not enough cards left in the deck.")
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def __len__(self):
        return len(self.cards)



class HandRank(Enum):
    HIGH_CARD       = 1
    ONE_PAIR        = 2
    TWO_PAIR        = 3
    THREE_OF_A_KIND = 4
    STRAIGHT        = 5
    FLUSH           = 6
    FULL_HOUSE      = 7
    FOUR_OF_A_KIND  = 8
    STRAIGHT_FLUSH  = 9
    ROYAL_FLUSH     = 10


def _is_flush(cards: list[Card]) -> bool:
    return len({c.suit for c in cards}) == 1


def _is_straight(cards: list[Card]) -> bool:
    vals = sorted({c.value for c in cards})
    if len(vals) != 5:
        return False
    if vals[-1] - vals[0] == 4:
        return True
    if vals == [2, 3, 4, 5, 14]:
        return True
    return False


def _rank_counts(cards: list[Card]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for c in cards:
        counts[c.value] = counts.get(c.value, 0) + 1
    return counts


def evaluate_5card_hand(cards: list[Card]) -> tuple[HandRank, list[int]]:

    if len(cards) != 5:
        raise ValueError("evaluate_5card_hand requires exactly 5 cards.")

    flush    = _is_flush(cards)
    straight = _is_straight(cards)
    counts   = _rank_counts(cards)
    vals     = sorted(counts.keys(), key=lambda v: (counts[v], v), reverse=True)

    if straight and flush:
        high = max(c.value for c in cards)
        if high == 14 and _is_straight(cards):
            low = sorted(c.value for c in cards)[0]
            if low == 10:
                return HandRank.ROYAL_FLUSH, [14]
        return HandRank.STRAIGHT_FLUSH, [high if high != 14 or sorted(c.value for c in cards)[0] != 2 else 5]

    count_vals = sorted(counts.values(), reverse=True)

    if count_vals[0] == 4:
        return HandRank.FOUR_OF_A_KIND, vals

    if count_vals[:2] == [3, 2]:
        return HandRank.FULL_HOUSE, vals

    if flush:
        return HandRank.FLUSH, sorted([c.value for c in cards], reverse=True)

    if straight:
        sorted_vals = sorted(c.value for c in cards)
        high = sorted_vals[-1]
        # Ace-low
        if sorted_vals == [2, 3, 4, 5, 14]:
            high = 5
        return HandRank.STRAIGHT, [high]

    if count_vals[0] == 3:
        return HandRank.THREE_OF_A_KIND, vals

    if count_vals[:2] == [2, 2]:
        return HandRank.TWO_PAIR, vals

    if count_vals[0] == 2:
        return HandRank.ONE_PAIR, vals

    return HandRank.HIGH_CARD, sorted([c.value for c in cards], reverse=True)


def best_hand_from(hole_cards: list[Card], community_cards: list[Card]) -> tuple[HandRank, list[int]]:
    """
    Given 2 hole cards and up to 5 community cards, return the best possible
    5-card hand evaluation.
    """
    all_cards = hole_cards + community_cards
    if len(all_cards) < 5:
        raise ValueError("Need at least 5 cards total to evaluate.")

    best = None
    for combo in combinations(all_cards, 5):
        result = evaluate_5card_hand(list(combo))
        if best is None or compare_hands(result, best) > 0:
            best = result
    return best  


def compare_hands(
    hand_a: tuple[HandRank, list[int]],
    hand_b: tuple[HandRank, list[int]],
) -> int:
    rank_a, tb_a = hand_a
    rank_b, tb_b = hand_b

    if rank_a.value != rank_b.value:
        return 1 if rank_a.value > rank_b.value else -1

    for a, b in zip(tb_a, tb_b):
        if a != b:
            return 1 if a > b else -1
    return 0


def dealer_qualifies(dealer_hand: tuple[HandRank, list[int]]) -> bool:
    """Dealer must have at least a pair to qualify."""
    return dealer_hand[0].value >= HandRank.ONE_PAIR.value



class GamePhase(Enum):
    WAITING_FOR_BET  = auto()   
    PRE_FLOP         = auto()   
    FLOP             = auto()   
    SHOWDOWN         = auto()   
    GAME_OVER        = auto()   


class GameResult(Enum):
    PLAYER_WINS         = auto()
    DEALER_WINS         = auto()
    TIE                 = auto()
    DEALER_NO_QUALIFY   = auto()   


class PokerGame:

    STARTING_CHIPS = 500

    def __init__(self, starting_chips: int = STARTING_CHIPS):
        self.chips: int = starting_chips
        self.phase: GamePhase = GamePhase.WAITING_FOR_BET
        self.ante: int = 0
        self.player_hand: list[Card] = []
        self.dealer_hand: list[Card] = []
        self.community: list[Card] = []
        self.flop: list[Card] = []
        self.turn_river: list[Card] = []
        self.last_result: GameResult | None = None
        self._deck: Deck = Deck()
        self.result_message: str = ""



    def place_ante(self, amount: int) -> bool:
        """
        Start a new round with a given ante.
        Returns False if amount is invalid, True on success.
        """
        if amount <= 0 or amount > self.chips:
            return False
        self.ante = amount
        self.chips -= amount
        self._deal_round()
        self.phase = GamePhase.PRE_FLOP
        return True

    def reveal_flop(self):
        """Transition from PRE_FLOP to FLOP (reveals first 3 community cards)."""
        if self.phase != GamePhase.PRE_FLOP:
            raise RuntimeError("Cannot reveal flop in current phase.")
        self.flop = self.community[:3]
        self.phase = GamePhase.FLOP

    def player_bet(self) -> GameResult:
        """Player matches the ante. Reveal remaining cards and settle."""
        if self.phase != GamePhase.FLOP:
            raise RuntimeError("Cannot bet in current phase.")
        if self.chips < self.ante:
            raise RuntimeError("Not enough chips to call.")
        self.chips -= self.ante         
        self.turn_river = self.community[3:]
        self.phase = GamePhase.SHOWDOWN
        return self._settle()

    def player_fold(self) -> GameResult:
        """Player folds — loses the ante already paid."""
        if self.phase != GamePhase.FLOP:
            raise RuntimeError("Cannot fold in current phase.")
        self.turn_river = self.community[3:]
        self.phase = GamePhase.SHOWDOWN
        self.last_result = GameResult.DEALER_WINS
        self.result_message = "You folded. Dealer wins the ante."
        return self.last_result

    def new_round(self):
        """Reset for a fresh round (keeps chip count)."""
        self.ante = 0
        self.player_hand = []
        self.dealer_hand = []
        self.community = []
        self.flop = []
        self.turn_river = []
        self.last_result = None
        self.result_message = ""
        if self.chips <= 0:
            self.phase = GamePhase.GAME_OVER
        else:
            self.phase = GamePhase.WAITING_FOR_BET

    def _deal_round(self):
        self._deck = Deck()
        self._deck.shuffle()
        self.player_hand = self._deck.deal(2)
        self.dealer_hand = self._deck.deal(2)
        self.community   = self._deck.deal(5)
        self.flop        = []
        self.turn_river  = []

    def _settle(self) -> GameResult:
        player_eval = best_hand_from(self.player_hand, self.community)
        dealer_eval = best_hand_from(self.dealer_hand, self.community)

        if not dealer_qualifies(dealer_eval):
            self.chips += self.ante + self.ante  
            self.last_result = GameResult.DEALER_NO_QUALIFY
            self.result_message = (
                f"Dealer doesn't qualify ({dealer_eval[0].name.replace('_', ' ').title()}). "
                f"Ante pays 1:1, bet is a push!"
            )
            return self.last_result

        cmp = compare_hands(player_eval, dealer_eval)

        if cmp == 1:
            self.chips += self.ante * 4  
            self.last_result = GameResult.PLAYER_WINS
            self.result_message = (
                f"You win! {player_eval[0].name.replace('_', ' ').title()} "
                f"beats {dealer_eval[0].name.replace('_', ' ').title()}."
            )
        elif cmp == -1:
            self.last_result = GameResult.DEALER_WINS
            self.result_message = (
                f"Dealer wins. {dealer_eval[0].name.replace('_', ' ').title()} "
                f"beats {player_eval[0].name.replace('_', ' ').title()}."
            )
        else:
            self.chips += self.ante * 2
            self.last_result = GameResult.TIE
            self.result_message = "It's a tie! Both bets returned."

        return self.last_result
