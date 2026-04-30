import unittest
from models.card import Card
from models.hand import calculate_score, get_strategy_advice


class TestHand(unittest.TestCase):

    def test_calculate_score_simple(self):
        hand = [Card("♠", "10"), Card("♥", "7")]
        self.assertEqual(calculate_score(hand), 17)

    def test_calculate_score_with_ace(self):
        hand = [Card("♠", "A"), Card("♥", "9")]
        self.assertEqual(calculate_score(hand), 20)

    def test_calculate_score_with_multiple_aces(self):
        hand = [Card("♠", "A"), Card("♥", "A"), Card("♦", "9")]
        self.assertEqual(calculate_score(hand), 21)

    def test_calculate_score_bust_prevention(self):
        hand = [Card("♠", "10"), Card("♥", "8"), Card("♦", "A")]
        self.assertEqual(calculate_score(hand), 19)

    def test_get_strategy_advice_hard_hand(self):
        hand16 = [Card("♠", "10"), Card("♥", "6")]
        self.assertEqual(get_strategy_advice(hand16, Card("♦", "10")), "HIT")
        self.assertEqual(get_strategy_advice(hand16, Card("♦", "6")), "STAND")

        hand11 = [Card("♠", "8"), Card("♥", "3")]
        self.assertEqual(get_strategy_advice(hand11, Card("♦", "6")), "DOUBLE")

    def test_get_strategy_advice_soft_hand(self):
        soft18 = [Card("♠", "A"), Card("♥", "7")]
        self.assertEqual(get_strategy_advice(soft18, Card("♦", "2")), "STAND")
        self.assertEqual(get_strategy_advice(soft18, Card("♦", "9")), "HIT")

        soft19 = [Card("♠", "A"), Card("♥", "8")]
        self.assertEqual(get_strategy_advice(soft19, Card("♦", "2")), "STAND")

    def test_get_strategy_advice_more_branches(self):
        # 17+
        hand17 = [Card("♠", "10"), Card("♥", "7")]
        self.assertEqual(get_strategy_advice(hand17, Card("♦", "2")), "STAND")

        # 13-16 vs dealer > 6
        hand14 = [Card("♠", "10"), Card("♥", "4")]
        self.assertEqual(get_strategy_advice(hand14, Card("♦", "7")), "HIT")

        # 12 vs 2, 3
        hand12 = [Card("♠", "10"), Card("♥", "2")]
        self.assertEqual(get_strategy_advice(hand12, Card("♦", "2")), "HIT")
        self.assertEqual(get_strategy_advice(hand12, Card("♦", "3")), "HIT")

        # 10 vs 10
        hand10 = [Card("♠", "6"), Card("♥", "4")]
        self.assertEqual(get_strategy_advice(hand10, Card("♦", "10")), "HIT")

        # 9 vs 2
        hand9 = [Card("♠", "5"), Card("♥", "4")]
        self.assertEqual(get_strategy_advice(hand9, Card("♦", "2")), "HIT")
        self.assertEqual(get_strategy_advice(hand9, Card("♦", "3")), "DOUBLE")

        # 8
        hand8 = [Card("♠", "5"), Card("♥", "3")]
        self.assertEqual(get_strategy_advice(hand8, Card("♦", "5")), "HIT")


if __name__ == "__main__":
    unittest.main()
