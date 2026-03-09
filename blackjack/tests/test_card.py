import unittest
from models.card import Card

class TestCard(unittest.TestCase):

    def test_card_initialization(self):
        card = Card('♠', 'A')
        self.assertEqual(card.suit, '♠')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.value, 11)
        self.assertTrue(card.face_up)

    def test_card_values(self):
        self.assertEqual(Card('♥', 'K').value, 10)
        self.assertEqual(Card('♦', 'Q').value, 10)
        self.assertEqual(Card('♣', 'J').value, 10)
        self.assertEqual(Card('♠', '10').value, 10)
        self.assertEqual(Card('♠', '2').value, 2)
        self.assertEqual(Card('♥', '9').value, 9)

if __name__ == '__main__':
    unittest.main()
