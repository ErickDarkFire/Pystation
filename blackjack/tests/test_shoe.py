import unittest
from models.shoe import Shoe

class TestShoe(unittest.TestCase):

    def test_shoe_initialization(self):
        s = Shoe()
        self.assertEqual(len(s.cards), 6 * 52)

    def test_draw_card(self):
        s = Shoe()
        initial_count = len(s.cards)
        card = s.draw_card()
        self.assertIsNotNone(card)
        self.assertEqual(len(s.cards), initial_count - 1)

    def test_shoe_rebuild_when_empty(self):
        s = Shoe()
        s.cards.clear()
        self.assertEqual(len(s.cards), 0)
        card = s.draw_card()
        # It should rebuild and then pop one
        self.assertEqual(len(s.cards), (6 * 52) - 1)
        self.assertIsNotNone(card)

if __name__ == '__main__':
    unittest.main()
