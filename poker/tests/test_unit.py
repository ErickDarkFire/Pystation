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
    return Card(rank, suit)


def hand(*specs):
    return [Card(r, s) for r, s in specs]


class TestCard:

    def test_card_properties(self):
        card = c("A", "Spades")
        assert card.rank == "A"
        assert card.suit == "Spades"
        assert card.value == 14

    def test_all_ranks_have_correct_values(self):
        expected = list(range(2, 15))
        actual = [Card(r, "Spades").value for r in RANKS]
        assert actual == expected

    def test_invalid_rank_raises(self):
        with pytest.raises(ValueError):
            Card("1", "Hearts")

    def test_invalid_suit_raises(self):
        with pytest.raises(ValueError):
            Card("A", "Stars")

    def test_equality_and_hash(self):
        a = c("K", "Hearts")
        b = c("K", "Hearts")
        c2 = c("K", "Spades")

        assert a == b
        assert a != c2
        assert hash(a) == hash(b)

    def test_card_usable_in_set(self):
        s = {c("A", "Spades"), c("A", "Hearts"), c("A", "Spades")}
        assert len(s) == 2

    def test_repr_contains_info(self):
        text = repr(c("Q", "Spades"))
        assert "Q" in text
        assert "♠" in text


class TestDeck:

    def test_deck_has_52_unique_cards(self):
        d = Deck()
        assert len(d) == 52
        assert len(set(d.cards)) == 52

    def test_deck_contains_all_suits_and_ranks(self):
        d = Deck()
        assert {c.suit for c in d.cards} == set(SUITS)
        assert {c.rank for c in d.cards} == set(RANKS)

    def test_each_rank_and_suit_count_correct(self):
        d = Deck()

        for suit in SUITS:
            assert sum(1 for c in d.cards if c.suit == suit) == 13

        for rank in RANKS:
            assert sum(1 for c in d.cards if c.rank == rank) == 4

    def test_deal_removes_cards_without_duplicates(self):
        d = Deck()
        a = d.deal(5)
        b = d.deal(5)

        assert len(d) == 42
        assert set(a).isdisjoint(set(b))

    def test_deal_too_many_raises(self):
        with pytest.raises(ValueError):
            Deck().deal(53)

    def test_shuffle_preserves_unique_cards(self):
        d = Deck().shuffle()
        assert len(d) == 52
        assert len(set(d.cards)) == 52


class TestHelpers:

    def test_is_flush(self):
        flush = hand(
            ("A", "Hearts"),
            ("K", "Hearts"),
            ("Q", "Hearts"),
            ("J", "Hearts"),
            ("10", "Hearts"),
        )

        non_flush = hand(
            ("A", "Hearts"),
            ("K", "Spades"),
            ("Q", "Hearts"),
            ("J", "Hearts"),
            ("10", "Hearts"),
        )

        assert _is_flush(flush)
        assert not _is_flush(non_flush)

    def test_is_straight(self):
        normal = hand(
            ("5", "Clubs"),
            ("6", "Clubs"),
            ("7", "Hearts"),
            ("8", "Spades"),
            ("9", "Diamonds"),
        )

        ace_low = hand(
            ("A", "Hearts"),
            ("2", "Diamonds"),
            ("3", "Clubs"),
            ("4", "Spades"),
            ("5", "Hearts"),
        )

        invalid = hand(
            ("5", "Hearts"),
            ("5", "Diamonds"),
            ("6", "Clubs"),
            ("7", "Spades"),
            ("8", "Hearts"),
        )

        assert _is_straight(normal)
        assert _is_straight(ace_low)
        assert not _is_straight(invalid)

    def test_rank_counts(self):
        cards = hand(
            ("K", "Hearts"),
            ("K", "Spades"),
            ("K", "Clubs"),
            ("2", "Diamonds"),
            ("3", "Hearts"),
        )

        counts = _rank_counts(cards)
        assert counts[13] == 3
        assert counts[2] == 1


class TestEvaluate5CardHand:

    @pytest.mark.parametrize(
        "cards, expected",
        [
            (
                hand(
                    ("10", "Hearts"),
                    ("J", "Hearts"),
                    ("Q", "Hearts"),
                    ("K", "Hearts"),
                    ("A", "Hearts"),
                ),
                HandRank.ROYAL_FLUSH,
            ),
            (
                hand(
                    ("5", "Clubs"),
                    ("6", "Clubs"),
                    ("7", "Clubs"),
                    ("8", "Clubs"),
                    ("9", "Clubs"),
                ),
                HandRank.STRAIGHT_FLUSH,
            ),
            (
                hand(
                    ("K", "Hearts"),
                    ("K", "Diamonds"),
                    ("K", "Clubs"),
                    ("K", "Spades"),
                    ("2", "Hearts"),
                ),
                HandRank.FOUR_OF_A_KIND,
            ),
            (
                hand(
                    ("J", "Hearts"),
                    ("J", "Diamonds"),
                    ("J", "Clubs"),
                    ("9", "Spades"),
                    ("9", "Hearts"),
                ),
                HandRank.FULL_HOUSE,
            ),
            (
                hand(
                    ("2", "Hearts"),
                    ("5", "Hearts"),
                    ("7", "Hearts"),
                    ("9", "Hearts"),
                    ("K", "Hearts"),
                ),
                HandRank.FLUSH,
            ),
            (
                hand(
                    ("10", "Hearts"),
                    ("J", "Diamonds"),
                    ("Q", "Clubs"),
                    ("K", "Spades"),
                    ("A", "Hearts"),
                ),
                HandRank.STRAIGHT,
            ),
            (
                hand(
                    ("8", "Hearts"),
                    ("8", "Diamonds"),
                    ("8", "Clubs"),
                    ("3", "Spades"),
                    ("K", "Hearts"),
                ),
                HandRank.THREE_OF_A_KIND,
            ),
            (
                hand(
                    ("A", "Hearts"),
                    ("A", "Diamonds"),
                    ("K", "Clubs"),
                    ("K", "Spades"),
                    ("2", "Hearts"),
                ),
                HandRank.TWO_PAIR,
            ),
            (
                hand(
                    ("Q", "Hearts"),
                    ("Q", "Diamonds"),
                    ("3", "Clubs"),
                    ("7", "Spades"),
                    ("9", "Hearts"),
                ),
                HandRank.ONE_PAIR,
            ),
            (
                hand(
                    ("2", "Hearts"),
                    ("5", "Diamonds"),
                    ("7", "Clubs"),
                    ("9", "Spades"),
                    ("K", "Hearts"),
                ),
                HandRank.HIGH_CARD,
            ),
        ],
    )
    def test_all_hand_types(self, cards, expected):
        assert evaluate_5card_hand(cards)[0] == expected

    def test_wrong_card_count_raises(self):
        with pytest.raises(ValueError):
            evaluate_5card_hand(hand(("A", "Hearts"), ("K", "Spades")))

    def test_tiebreakers_sorted_descending(self):
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

    def test_picks_best_possible_hand(self):
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

    def test_plays_the_board_when_better(self):
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
        with pytest.raises(ValueError):
            best_hand_from(
                hand(("A", "Spades"), ("K", "Spades")),
                hand(("Q", "Spades"), ("J", "Spades")),
            )


class TestCompareHands:

    def test_flush_beats_straight(self):
        flush = (HandRank.FLUSH, [13, 11, 9, 7, 5])
        straight = (HandRank.STRAIGHT, [10])

        assert compare_hands(flush, straight) == 1
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


class TestDealerQualifies:

    @pytest.mark.parametrize(
        "hand_value, expected",
        [
            ((HandRank.HIGH_CARD, [14, 10, 8, 6, 4]), False),
            ((HandRank.ONE_PAIR, [8, 8, 5, 3]), True),
            ((HandRank.TWO_PAIR, [9, 9, 5, 5, 2]), True),
            ((HandRank.STRAIGHT, [10]), True),
            ((HandRank.FLUSH, [13, 11, 9, 7, 5]), True),
            ((HandRank.ROYAL_FLUSH, [14]), True),
        ],
    )
    def test_dealer_qualifies(self, hand_value, expected):
        assert dealer_qualifies(hand_value) == expected


class TestPokerGameInit:

    def test_initial_state(self):
        g = PokerGame()

        assert g.phase == GamePhase.WAITING_FOR_BET
        assert g.chips == 500
        assert g.ante == 0
        assert g.player_hand == []
        assert g.dealer_hand == []
        assert g.community == []
        assert g.last_result is None
        assert g.result_message == ""


class TestPlaceAnte:

    def test_valid_ante_initializes_round(self):
        g = PokerGame(500)

        assert g.place_ante(50) is True
        assert g.chips == 450
        assert g.ante == 50
        assert g.phase == GamePhase.PRE_FLOP
        assert len(g.player_hand) == 2
        assert len(g.dealer_hand) == 2
        assert len(g.community) == 5

    def test_invalid_antes_return_false(self):
        g = PokerGame(100)

        assert g.place_ante(0) is False
        assert g.place_ante(-10) is False
        assert g.place_ante(200) is False

    def test_no_duplicate_cards_in_deal(self):
        g = PokerGame(500)
        g.place_ante(25)

        all_cards = g.player_hand + g.dealer_hand + g.community
        assert len(set(all_cards)) == 9


class TestRevealFlop:

    def test_flop_reveals_first_three_cards(self):
        g = PokerGame(500)
        g.place_ante(25)

        expected = g.community[:3]

        g.reveal_flop()

        assert g.flop == expected
        assert g.phase == GamePhase.FLOP

    def test_reveal_flop_wrong_phase_raises(self):
        with pytest.raises(RuntimeError):
            PokerGame().reveal_flop()


class TestPlayerBet:

    def test_bet_advances_to_showdown(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()

        result = g.player_bet()

        assert g.phase == GamePhase.SHOWDOWN
        assert len(g.turn_river) == 2
        assert result in list(GameResult) or result is None

    def test_bet_wrong_phase_raises(self):
        g = PokerGame(500)
        g.place_ante(50)

        with pytest.raises(RuntimeError):
            g.player_bet()

    def test_bet_insufficient_chips(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()

        result = g.player_bet()

        assert result is None
        assert g.phase == GamePhase.FLOP
        assert g.result_message != ""


class TestPlayerFold:

    def test_fold_sets_dealer_win(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()

        result = g.player_fold()

        assert result == GameResult.DEALER_WINS
        assert g.phase == GamePhase.SHOWDOWN
        assert len(g.turn_river) == 2
        assert g.result_message != ""

    def test_fold_wrong_phase_raises(self):
        with pytest.raises(RuntimeError):
            PokerGame().player_fold()


class TestNewRound:

    def test_new_round_resets_state(self):
        g = PokerGame(500)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()

        chips_before = g.chips

        g.new_round()

        assert g.phase == GamePhase.WAITING_FOR_BET
        assert g.player_hand == []
        assert g.dealer_hand == []
        assert g.community == []
        assert g.ante == 0
        assert g.last_result is None
        assert g.chips == chips_before

    def test_new_round_game_over_when_no_chips(self):
        g = PokerGame(50)
        g.place_ante(50)
        g.reveal_flop()
        g.player_fold()
        g.new_round()

        assert g.phase == GamePhase.GAME_OVER
