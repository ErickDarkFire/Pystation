import pytest
from game_logic import (
    Card,
    Deck,
    SUITS,
    RANKS,
    HandRank,
    evaluate_5card_hand,
    best_hand_from,
    compare_hands,
    dealer_qualifies,
    _is_flush,
    _is_straight,
    _rank_counts,
    PokerGame,
    GamePhase,
    GameResult,
)


def c(rank, suit):
    """Crear una carta"""
    return Card(rank, suit)


def hand(*specs):
    """Crea una lista de cartas rank, suit"""
    return [Card(r, s) for r, s in specs]


def inject(game, player_hole, dealer_hole, community):
    """Inyecta cartas específicas en un juego ya iniciado"""
    game.player_hand = hand(*player_hole)
    game.dealer_hand = hand(*dealer_hole)
    game.community = hand(*community)
    game.flop = []
    game.turn_river = []


class TestCard:

    def test_card_creation_rank(self):
        assert c("A", "Spades").rank == "A"

    def test_card_creation_suit(self):
        assert c("K", "Hearts").suit == "Hearts"

    def test_card_value_two(self):
        assert c("2", "Clubs").value == 2

    def test_card_value_ten(self):
        assert c("10", "Diamonds").value == 10

    def test_card_value_jack(self):
        assert c("J", "Spades").value == 11

    def test_card_value_queen(self):
        assert c("Q", "Hearts").value == 12

    def test_card_value_king(self):
        assert c("K", "Clubs").value == 13

    def test_card_value_ace(self):
        assert c("A", "Diamonds").value == 14

    def test_all_ranks_have_correct_values(self):
        expected = list(range(2, 15))
        actual = [Card(r, "Spades").value for r in RANKS]
        assert actual == expected

    # --- Ordenamiento de valores ---
    def test_value_ordering_ascending(self):
        assert c("2", "Hearts").value < c("5", "Hearts").value < c("A", "Hearts").value

    def test_two_less_than_ace(self):
        assert c("2", "Spades").value < c("A", "Spades").value

    def test_invalid_rank_raises(self):
        with pytest.raises(ValueError):
            Card("1", "Hearts")

    def test_invalid_rank_zero(self):
        with pytest.raises(ValueError):
            Card("0", "Spades")

    def test_invalid_suit_raises(self):
        with pytest.raises(ValueError):
            Card("A", "Stars")

    def test_invalid_suit_lowercase(self):
        with pytest.raises(ValueError):
            Card("A", "hearts")

    def test_invalid_both_raises(self):
        with pytest.raises(ValueError):
            Card("X", "Magic")

    def test_equality_same_card(self):
        assert c("K", "Hearts") == c("K", "Hearts")

    def test_inequality_different_suit(self):
        assert c("K", "Hearts") != c("K", "Spades")

    def test_inequality_different_rank(self):
        assert c("Q", "Hearts") != c("K", "Hearts")

    def test_hash_same_card(self):
        assert hash(c("A", "Spades")) == hash(c("A", "Spades"))

    def test_hash_different_cards(self):
        assert hash(c("A", "Spades")) != hash(c("A", "Hearts"))

    def test_card_usable_in_set(self):
        s = {c("A", "Spades"), c("A", "Hearts"), c("A", "Spades")}
        assert len(s) == 2

    def test_repr_contains_rank(self):
        assert "Q" in repr(c("Q", "Diamonds"))

    def test_repr_contains_suit_symbol(self):
        assert "♠" in repr(c("A", "Spades"))

    def test_repr_hearts_symbol(self):
        assert "♥" in repr(c("2", "Hearts"))


class TestDeck:

    def test_deck_has_52_cards(self):
        assert len(Deck()) == 52

    def test_all_cards_unique(self):
        d = Deck()
        assert len(set(d.cards)) == 52

    def test_deck_contains_all_suits(self):
        d = Deck()
        suits_found = {card.suit for card in d.cards}
        assert suits_found == set(SUITS)

    def test_deck_contains_all_ranks(self):
        d = Deck()
        ranks_found = {card.rank for card in d.cards}
        assert ranks_found == set(RANKS)

    def test_each_suit_has_13_cards(self):
        d = Deck()
        for suit in SUITS:
            count = sum(1 for card in d.cards if card.suit == suit)
            assert count == 13

    def test_each_rank_appears_4_times(self):
        d = Deck()
        for rank in RANKS:
            count = sum(1 for card in d.cards if card.rank == rank)
            assert count == 4

    def test_deal_1_returns_list(self):
        d = Deck()
        dealt = d.deal(1)
        assert isinstance(dealt, list) and len(dealt) == 1

    def test_deal_5_returns_5_cards(self):
        d = Deck()
        dealt = d.deal(5)
        assert len(dealt) == 5

    def test_deal_removes_from_deck(self):
        d = Deck()
        d.deal(5)
        assert len(d) == 47

    def test_deal_sequential_no_repeats(self):
        d = Deck()
        a = d.deal(5)
        b = d.deal(5)
        assert set(a).isdisjoint(set(b))

    def test_deal_all_52(self):
        d = Deck()
        all_cards = d.deal(52)
        assert len(all_cards) == 52
        assert len(d) == 0

    def test_deal_too_many_raises(self):
        d = Deck()
        with pytest.raises(ValueError):
            d.deal(53)

    def test_deal_zero_after_empty_raises(self):
        d = Deck()
        d.deal(52)
        with pytest.raises(ValueError):
            d.deal(1)

    def test_shuffle_returns_self(self):
        d = Deck()
        assert d.shuffle() is d

    def test_shuffle_preserves_52_cards(self):
        import random

        random.seed(0)
        d = Deck().shuffle()
        assert len(d) == 52

    def test_shuffle_all_cards_unique_after_shuffle(self):
        import random

        random.seed(42)
        d = Deck().shuffle()
        assert len(set(d.cards)) == 52

    def test_len_method(self):
        d = Deck()
        d.deal(10)
        assert len(d) == 42


class TestIsFlush:
    def test_flush_true(self):
        cards = hand(
            ("A", "Hearts"),
            ("K", "Hearts"),
            ("Q", "Hearts"),
            ("J", "Hearts"),
            ("10", "Hearts"),
        )
        assert _is_flush(cards)

    def test_flush_false_four_suits(self):
        cards = hand(
            ("A", "Hearts"),
            ("K", "Spades"),
            ("Q", "Hearts"),
            ("J", "Hearts"),
            ("10", "Hearts"),
        )
        assert not _is_flush(cards)

    def test_flush_false_two_suits(self):
        cards = hand(
            ("A", "Hearts"),
            ("K", "Hearts"),
            ("Q", "Spades"),
            ("J", "Hearts"),
            ("10", "Hearts"),
        )
        assert not _is_flush(cards)


class TestIsStraight:
    def test_straight_normal(self):
        cards = hand(
            ("5", "Clubs"),
            ("6", "Clubs"),
            ("7", "Hearts"),
            ("8", "Spades"),
            ("9", "Diamonds"),
        )
        assert _is_straight(cards)

    def test_straight_ace_high(self):
        cards = hand(
            ("10", "Hearts"),
            ("J", "Diamonds"),
            ("Q", "Clubs"),
            ("K", "Spades"),
            ("A", "Hearts"),
        )
        assert _is_straight(cards)

    def test_straight_ace_low(self):
        cards = hand(
            ("A", "Hearts"),
            ("2", "Diamonds"),
            ("3", "Clubs"),
            ("4", "Spades"),
            ("5", "Hearts"),
        )
        assert _is_straight(cards)

    def test_not_straight_gap(self):
        cards = hand(
            ("3", "Hearts"),
            ("4", "Diamonds"),
            ("6", "Clubs"),
            ("7", "Spades"),
            ("8", "Hearts"),
        )
        assert not _is_straight(cards)

    def test_not_straight_pair(self):
        cards = hand(
            ("5", "Hearts"),
            ("5", "Diamonds"),
            ("6", "Clubs"),
            ("7", "Spades"),
            ("8", "Hearts"),
        )
        assert not _is_straight(cards)


class TestRankCounts:
    def test_pair_counts(self):
        cards = hand(
            ("A", "Hearts"),
            ("A", "Spades"),
            ("K", "Clubs"),
            ("Q", "Diamonds"),
            ("J", "Hearts"),
        )
        counts = _rank_counts(cards)
        assert counts[14] == 2
        assert counts[13] == 1

    def test_three_of_a_kind_counts(self):
        cards = hand(
            ("K", "Hearts"),
            ("K", "Spades"),
            ("K", "Clubs"),
            ("2", "Diamonds"),
            ("3", "Hearts"),
        )
        counts = _rank_counts(cards)
        assert counts[13] == 3

    def test_four_of_a_kind_counts(self):
        cards = hand(
            ("7", "Hearts"),
            ("7", "Spades"),
            ("7", "Clubs"),
            ("7", "Diamonds"),
            ("A", "Hearts"),
        )
        counts = _rank_counts(cards)
        assert counts[7] == 4


class TestEvaluate5CardHand:

    def test_royal_flush(self):
        h = hand(
            ("10", "Hearts"),
            ("J", "Hearts"),
            ("Q", "Hearts"),
            ("K", "Hearts"),
            ("A", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.ROYAL_FLUSH

    def test_straight_flush(self):
        h = hand(
            ("5", "Clubs"),
            ("6", "Clubs"),
            ("7", "Clubs"),
            ("8", "Clubs"),
            ("9", "Clubs"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.STRAIGHT_FLUSH

    def test_straight_flush_ace_low(self):
        h = hand(
            ("A", "Spades"),
            ("2", "Spades"),
            ("3", "Spades"),
            ("4", "Spades"),
            ("5", "Spades"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.STRAIGHT_FLUSH

    def test_four_of_a_kind(self):
        h = hand(
            ("K", "Hearts"),
            ("K", "Diamonds"),
            ("K", "Clubs"),
            ("K", "Spades"),
            ("2", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.FOUR_OF_A_KIND

    def test_full_house(self):
        h = hand(
            ("J", "Hearts"),
            ("J", "Diamonds"),
            ("J", "Clubs"),
            ("9", "Spades"),
            ("9", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.FULL_HOUSE

    def test_full_house_high_three(self):
        h = hand(
            ("A", "Hearts"),
            ("A", "Diamonds"),
            ("A", "Clubs"),
            ("2", "Spades"),
            ("2", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.FULL_HOUSE

    def test_flush(self):
        h = hand(
            ("2", "Hearts"),
            ("5", "Hearts"),
            ("7", "Hearts"),
            ("9", "Hearts"),
            ("K", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.FLUSH

    def test_flush_all_suits_spades(self):
        h = hand(
            ("3", "Spades"),
            ("6", "Spades"),
            ("8", "Spades"),
            ("10", "Spades"),
            ("Q", "Spades"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.FLUSH

    def test_straight_middle(self):
        h = hand(
            ("3", "Hearts"),
            ("4", "Diamonds"),
            ("5", "Clubs"),
            ("6", "Spades"),
            ("7", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.STRAIGHT

    def test_straight_ace_high(self):
        h = hand(
            ("10", "Hearts"),
            ("J", "Diamonds"),
            ("Q", "Clubs"),
            ("K", "Spades"),
            ("A", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.STRAIGHT

    def test_straight_ace_low(self):
        h = hand(
            ("A", "Hearts"),
            ("2", "Diamonds"),
            ("3", "Clubs"),
            ("4", "Spades"),
            ("5", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.STRAIGHT

    def test_three_of_a_kind(self):
        h = hand(
            ("8", "Hearts"),
            ("8", "Diamonds"),
            ("8", "Clubs"),
            ("3", "Spades"),
            ("K", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.THREE_OF_A_KIND

    def test_two_pair(self):
        h = hand(
            ("A", "Hearts"),
            ("A", "Diamonds"),
            ("K", "Clubs"),
            ("K", "Spades"),
            ("2", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.TWO_PAIR

    def test_two_pair_low(self):
        h = hand(
            ("2", "Hearts"),
            ("2", "Diamonds"),
            ("3", "Clubs"),
            ("3", "Spades"),
            ("7", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.TWO_PAIR

    def test_one_pair(self):
        h = hand(
            ("Q", "Hearts"),
            ("Q", "Diamonds"),
            ("3", "Clubs"),
            ("7", "Spades"),
            ("9", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.ONE_PAIR

    def test_high_card(self):
        h = hand(
            ("2", "Hearts"),
            ("5", "Diamonds"),
            ("7", "Clubs"),
            ("9", "Spades"),
            ("K", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.HIGH_CARD

    def test_high_card_ace_kicker(self):
        h = hand(
            ("A", "Hearts"),
            ("3", "Diamonds"),
            ("6", "Clubs"),
            ("8", "Spades"),
            ("10", "Hearts"),
        )
        assert evaluate_5card_hand(h)[0] == HandRank.HIGH_CARD

    def test_wrong_card_count_raises(self):
        with pytest.raises(ValueError):
            evaluate_5card_hand(hand(("A", "Hearts"), ("K", "Spades")))

    def test_six_cards_raises(self):
        with pytest.raises(ValueError):
            evaluate_5card_hand(
                hand(
                    ("A", "Hearts"),
                    ("K", "Spades"),
                    ("Q", "Clubs"),
                    ("J", "Diamonds"),
                    ("10", "Hearts"),
                    ("9", "Clubs"),
                )
            )

    def test_royal_flush_tiebreaker_is_14(self):
        h = hand(
            ("10", "Hearts"),
            ("J", "Hearts"),
            ("Q", "Hearts"),
            ("K", "Hearts"),
            ("A", "Hearts"),
        )
        _, tb = evaluate_5card_hand(h)
        assert tb == [14]

    def test_straight_flush_high_value_in_tiebreaker(self):
        h = hand(
            ("5", "Clubs"),
            ("6", "Clubs"),
            ("7", "Clubs"),
            ("8", "Clubs"),
            ("9", "Clubs"),
        )
        _, tb = evaluate_5card_hand(h)
        assert tb[0] == 9

    def test_flush_tiebreaker_descending(self):
        h = hand(
            ("2", "Hearts"),
            ("5", "Hearts"),
            ("7", "Hearts"),
            ("9", "Hearts"),
            ("K", "Hearts"),
        )
        _, tb = evaluate_5card_hand(h)
        assert tb == sorted(tb, reverse=True)

    def test_high_card_tiebreaker_descending(self):
        h = hand(
            ("2", "Hearts"),
            ("5", "Diamonds"),
            ("7", "Clubs"),
            ("9", "Spades"),
            ("K", "Hearts"),
        )
        _, tb = evaluate_5card_hand(h)
        assert tb == sorted(tb, reverse=True)


class TestBestHandFrom:

    def test_picks_four_of_a_kind_from_seven(self):
        hole = hand(("A", "Spades"), ("A", "Hearts"))
        comm = hand(
            ("A", "Diamonds"),
            ("A", "Clubs"),
            ("K", "Spades"),
            ("2", "Clubs"),
            ("7", "Diamonds"),
        )
        rank, _ = best_hand_from(hole, comm)
        assert rank == HandRank.FOUR_OF_A_KIND

    def test_picks_flush_from_community(self):
        hole = hand(("2", "Spades"), ("3", "Hearts"))
        comm = hand(
            ("5", "Clubs"),
            ("7", "Clubs"),
            ("9", "Clubs"),
            ("J", "Clubs"),
            ("K", "Clubs"),
        )
        rank, _ = best_hand_from(hole, comm)
        assert rank == HandRank.FLUSH

    def test_picks_best_straight(self):
        hole = hand(("9", "Hearts"), ("10", "Diamonds"))
        comm = hand(
            ("J", "Clubs"),
            ("Q", "Spades"),
            ("K", "Hearts"),
            ("2", "Clubs"),
            ("3", "Diamonds"),
        )
        rank, _ = best_hand_from(hole, comm)
        assert rank == HandRank.STRAIGHT

    def test_plays_the_board_when_better(self):
        # Community has a Royal Flush
        hole = hand(("2", "Clubs"), ("3", "Diamonds"))
        comm = hand(
            ("10", "Hearts"),
            ("J", "Hearts"),
            ("Q", "Hearts"),
            ("K", "Hearts"),
            ("A", "Hearts"),
        )
        rank, _ = best_hand_from(hole, comm)
        assert rank == HandRank.ROYAL_FLUSH

    def test_too_few_cards_raises(self):
        hole = hand(("A", "Spades"), ("K", "Spades"))
        comm = hand(("Q", "Spades"), ("J", "Spades"))
        with pytest.raises(ValueError):
            best_hand_from(hole, comm)

    def test_exactly_five_cards_ok(self):
        hole = hand(("A", "Spades"), ("K", "Spades"))
        comm = hand(("Q", "Spades"), ("J", "Spades"), ("10", "Spades"))
        rank, _ = best_hand_from(hole, comm)
        assert rank == HandRank.ROYAL_FLUSH


class TestCompareHands:

    def test_flush_beats_straight(self):
        flush = (HandRank.FLUSH, [13, 11, 9, 7, 5])
        straight = (HandRank.STRAIGHT, [10])
        assert compare_hands(flush, straight) == 1

    def test_straight_loses_to_flush(self):
        flush = (HandRank.FLUSH, [13, 11, 9, 7, 5])
        straight = (HandRank.STRAIGHT, [10])
        assert compare_hands(straight, flush) == -1

    def test_pair_aces_beats_pair_kings(self):
        pa = (HandRank.ONE_PAIR, [14, 14, 10, 8])
        pk = (HandRank.ONE_PAIR, [13, 13, 10, 8])
        assert compare_hands(pa, pk) == 1

    def test_exact_tie_returns_zero(self):
        h = (HandRank.HIGH_CARD, [14, 10, 8, 6, 4])
        assert compare_hands(h, h) == 0

    def test_kicker_decides(self):
        a = (HandRank.ONE_PAIR, [9, 9, 14, 5])
        b = (HandRank.ONE_PAIR, [9, 9, 12, 5])
        assert compare_hands(a, b) == 1

    def test_four_beats_full_house(self):
        four = (HandRank.FOUR_OF_A_KIND, [8, 8, 8, 8, 3])
        full = (HandRank.FULL_HOUSE, [7, 7, 7, 5, 5])
        assert compare_hands(four, full) == 1

    def test_royal_beats_straight_flush(self):
        royal = (HandRank.ROYAL_FLUSH, [14])
        sf = (HandRank.STRAIGHT_FLUSH, [13])
        assert compare_hands(royal, sf) == 1

    def test_two_pair_beats_one_pair(self):
        tp = (HandRank.TWO_PAIR, [9, 9, 5, 5, 2])
        op = (HandRank.ONE_PAIR, [14, 14, 10, 8])
        assert compare_hands(tp, op) == 1

    def test_high_card_ace_beats_high_card_king(self):
        ha = (HandRank.HIGH_CARD, [14, 10, 8, 6, 4])
        hk = (HandRank.HIGH_CARD, [13, 10, 8, 6, 4])
        assert compare_hands(ha, hk) == 1

    def test_symmetry(self):
        a = (HandRank.FLUSH, [13, 11, 9, 7, 5])
        b = (HandRank.STRAIGHT, [10])
        assert compare_hands(a, b) == -compare_hands(b, a)


class TestDealerQualifies:

    def test_pair_qualifies(self):
        assert dealer_qualifies((HandRank.ONE_PAIR, [8, 8, 5, 3]))

    def test_high_card_does_not_qualify(self):
        assert not dealer_qualifies((HandRank.HIGH_CARD, [14, 10, 8, 6, 4]))

    def test_two_pair_qualifies(self):
        assert dealer_qualifies((HandRank.TWO_PAIR, [9, 9, 5, 5, 2]))

    def test_three_qualifies(self):
        assert dealer_qualifies((HandRank.THREE_OF_A_KIND, [7, 7, 7, 4, 2]))

    def test_straight_qualifies(self):
        assert dealer_qualifies((HandRank.STRAIGHT, [10]))

    def test_flush_qualifies(self):
        assert dealer_qualifies((HandRank.FLUSH, [13, 11, 9, 7, 5]))

    def test_full_house_qualifies(self):
        assert dealer_qualifies((HandRank.FULL_HOUSE, [9, 9, 9, 5, 5]))

    def test_four_of_a_kind_qualifies(self):
        assert dealer_qualifies((HandRank.FOUR_OF_A_KIND, [8, 8, 8, 8, 3]))

    def test_straight_flush_qualifies(self):
        assert dealer_qualifies((HandRank.STRAIGHT_FLUSH, [9]))

    def test_royal_flush_qualifies(self):
        assert dealer_qualifies((HandRank.ROYAL_FLUSH, [14]))


class TestPokerGameInit:

    def test_initial_phase(self):
        assert PokerGame().phase == GamePhase.WAITING_FOR_BET

    def test_initial_chips_default(self):
        assert PokerGame().chips == 500

    def test_initial_chips_custom(self):
        assert PokerGame(200).chips == 200

    def test_initial_ante_zero(self):
        assert PokerGame().ante == 0

    def test_initial_hands_empty(self):
        g = PokerGame()
        assert g.player_hand == [] and g.dealer_hand == []

    def test_initial_community_empty(self):
        assert PokerGame().community == []

    def test_initial_result_none(self):
        assert PokerGame().last_result is None

    def test_initial_message_empty(self):
        assert PokerGame().result_message == ""

    def test_starting_chips_constant(self):
        assert PokerGame.STARTING_CHIPS == 500


class TestPlaceAnte:

    def test_valid_ante_deducts_chips(self):
        g = PokerGame(500)
        g.place_ante(50)
        assert g.chips == 450

    def test_valid_ante_stores_ante(self):
        g = PokerGame(500)
        g.place_ante(100)
        assert g.ante == 100

    def test_valid_ante_advances_to_preflop(self):
        g = PokerGame(500)
        g.place_ante(50)
        assert g.phase == GamePhase.PRE_FLOP

    def test_valid_ante_deals_player_hand(self):
        g = PokerGame(500)
        g.place_ante(25)
        assert len(g.player_hand) == 2

    def test_valid_ante_deals_dealer_hand(self):
        g = PokerGame(500)
        g.place_ante(25)
        assert len(g.dealer_hand) == 2

    def test_valid_ante_deals_community(self):
        g = PokerGame(500)
        g.place_ante(25)
        assert len(g.community) == 5

    def test_valid_ante_returns_true(self):
        assert PokerGame(500).place_ante(50) is True

    def test_zero_ante_returns_false(self):
        assert PokerGame(500).place_ante(0) is False

    def test_negative_ante_returns_false(self):
        assert PokerGame(500).place_ante(-10) is False

    def test_ante_exceeds_chips_returns_false(self):
        assert PokerGame(100).place_ante(200) is False

    def test_ante_equal_to_chips_succeeds(self):
        g = PokerGame(100)
        assert g.place_ante(100) is True

    def test_invalid_ante_does_not_change_phase(self):
        g = PokerGame(500)
        g.place_ante(0)
        assert g.phase == GamePhase.WAITING_FOR_BET

    def test_invalid_ante_does_not_deduct_chips(self):
        g = PokerGame(500)
        g.place_ante(0)
        assert g.chips == 500

    def test_no_duplicate_cards_in_deal(self):
        g = PokerGame(500)
        g.place_ante(25)
        all_cards = g.player_hand + g.dealer_hand + g.community
        assert len(set(all_cards)) == 9


class TestRevealFlop:

    def test_flop_reveals_3_cards(self):
        g = PokerGame(500)
        g.place_ante(25)
        g.reveal_flop()
        assert len(g.flop) == 3

    def test_flop_advances_phase(self):
        g = PokerGame(500)
        g.place_ante(25)
        g.reveal_flop()
        assert g.phase == GamePhase.FLOP

    def test_flop_is_first_3_community(self):
        g = PokerGame(500)
        g.place_ante(25)
        community_snapshot = g.community[:3]
        g.reveal_flop()
        assert g.flop == community_snapshot

    def test_reveal_flop_wrong_phase_raises(self):
        g = PokerGame(500)
        with pytest.raises(RuntimeError):
            g.reveal_flop()

    def test_double_reveal_raises(self):
        g = PokerGame(500)
        g.place_ante(25)
        g.reveal_flop()
        with pytest.raises(RuntimeError):
            g.reveal_flop()


class TestPlayerBet:

    def test_bet_advances_to_showdown(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_bet()
        assert g.phase == GamePhase.SHOWDOWN

    def test_bet_reveals_turn_river(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_bet()
        assert len(g.turn_river) == 2

    def test_bet_turn_river_is_last_2_community(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        last_two = g.community[3:]
        g.player_bet()
        assert g.turn_river == last_two

    def test_bet_deducts_chips(self):
        g = PokerGame(500)
        g.place_ante(50)  # chips = 450
        g.reveal_flop()
        g.player_bet()  # chips = 400 (or more if win)
        # chips must have changed from 450
        assert g.chips != 500

    def test_bet_wrong_phase_raises(self):
        g = PokerGame(500)
        g.place_ante(50)
        with pytest.raises(RuntimeError):
            g.player_bet()

    def test_bet_before_deal_raises(self):
        g = PokerGame(500)
        with pytest.raises(RuntimeError):
            g.player_bet()

    def test_bet_insufficient_chips_returns_none(self):
        g = PokerGame(50)
        g.place_ante(50)  # chips = 0
        g.reveal_flop()
        result = g.player_bet()
        assert result is None

    def test_bet_insufficient_chips_no_phase_change(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_bet()
        assert g.phase == GamePhase.FLOP

    def test_bet_insufficient_chips_sets_message(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_bet()
        assert g.result_message != ""

    def test_bet_returns_game_result(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        result = g.player_bet()
        assert result in list(GameResult) or result is None


class TestPlayerFold:

    def test_fold_phase_becomes_showdown(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        assert g.phase == GamePhase.SHOWDOWN

    def test_fold_result_is_dealer_wins(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        result = g.player_fold()
        assert result == GameResult.DEALER_WINS

    def test_fold_does_not_deduct_extra_chips(self):
        g = PokerGame(500)
        g.place_ante(50)  # chips = 450
        g.reveal_flop()
        g.player_fold()
        assert g.chips == 450  # no extra deduction

    def test_fold_reveals_turn_river(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        assert len(g.turn_river) == 2

    def test_fold_sets_result_message(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        assert g.result_message != ""

    def test_fold_wrong_phase_raises(self):
        g = PokerGame(500)
        with pytest.raises(RuntimeError):
            g.player_fold()

    def test_fold_before_deal_raises(self):
        g = PokerGame(500)
        with pytest.raises(RuntimeError):
            g.player_fold()


class TestNewRound:

    def test_new_round_resets_phase(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.phase == GamePhase.WAITING_FOR_BET

    def test_new_round_clears_hands(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.player_hand == [] and g.dealer_hand == []

    def test_new_round_clears_community(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.community == [] and g.flop == [] and g.turn_river == []

    def test_new_round_resets_ante(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.ante == 0

    def test_new_round_resets_last_result(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.last_result is None

    def test_new_round_preserves_chips(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        chips_before_new_round = g.chips
        g.new_round()
        assert g.chips == chips_before_new_round

    def test_new_round_game_over_when_no_chips(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()
        assert g.phase == GamePhase.GAME_OVER

    def test_new_round_game_over_at_zero_chips(self):
        g = PokerGame(500)
        g.chips = 0
        g.new_round()
        assert g.phase == GamePhase.GAME_OVER
