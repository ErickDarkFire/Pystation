import unittest
from models.card import Card
from models.hand import calculate_score, get_strategy_advice

class TestHand(unittest.TestCase):

    def test_calculate_score_simple(self):
        hand = [Card('♠', '10'), Card('♥', '7')]
        self.assertEqual(calculate_score(hand), 17)

    def test_calculate_score_with_ace(self):
        hand = [Card('♠', 'A'), Card('♥', '9')]
        self.assertEqual(calculate_score(hand), 20)

    def test_calculate_score_with_multiple_aces(self):
        hand = [Card('♠', 'A'), Card('♥', 'A'), Card('♦', '9')]
        self.assertEqual(calculate_score(hand), 21)

    def test_calculate_score_bust_prevention(self):
        hand = [Card('♠', '10'), Card('♥', '8'), Card('♦', 'A')]
        self.assertEqual(calculate_score(hand), 19)

    def test_get_strategy_advice_hard_hand(self):
        hand16 = [Card('♠', '10'), Card('♥', '6')]
        self.assertEqual(get_strategy_advice(hand16, Card('♦', '10')), "HIT")
        self.assertEqual(get_strategy_advice(hand16, Card('♦', '6')), "STAND")

        hand11 = [Card('♠', '8'), Card('♥', '3')]
        self.assertEqual(get_strategy_advice(hand11, Card('♦', '6')), "DOUBLE")

    def test_get_strategy_advice_soft_hand(self):
        soft18 = [Card('♠', 'A'), Card('♥', '7')]
        self.assertEqual(get_strategy_advice(soft18, Card('♦', '2')), "STAND")
        self.assertEqual(get_strategy_advice(soft18, Card('♦', '9')), "HIT")

if __name__ == '__main__':
    unittest.main()
