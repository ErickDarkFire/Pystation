import unittest
from models.player import Player, Dealer
from models.card import Card


class TestPlayer(unittest.TestCase):

    def test_player_initialization(self):
        p = Player(initial_money=500)
        self.assertEqual(p.money, 500)
        self.assertEqual(len(p.hand), 0)
        self.assertEqual(p.current_bet, 0)

    def test_player_reset_hand(self):
        p = Player()
        p.hand.append(Card("♠", "A"))
        p.current_bet = 50
        p.reset_hand()
        self.assertEqual(len(p.hand), 0)
        self.assertEqual(p.current_bet, 0)

    def test_dealer_initialization(self):
        d = Dealer()
        self.assertEqual(len(d.hand), 0)

    def test_dealer_reset_hand(self):
        d = Dealer()
        d.hand.append(Card("♠", "A"))
        d.reset_hand()
        self.assertEqual(len(d.hand), 0)


if __name__ == "__main__":
    unittest.main()
