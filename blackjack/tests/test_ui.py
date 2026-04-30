import unittest
import os
import pygame

from ui.button import Button
from ui.card_renderer import draw_card
from ui.overlay import draw_result_overlay
from ui.table import (
    draw_table_base,
    draw_scores,
    draw_chips,
    draw_coach,
    draw_simulation_results,
)
from models.card import Card
import core.settings as st


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.surface = pygame.Surface((800, 600))

    def tearDown(self):
        pass

    def test_button_draw_and_update(self):
        btn = Button("TEST", 0, 0, 100, 50, "test_id")
        btn.draw(self.surface)

        # Test disabled
        btn.enabled = False
        btn.draw(self.surface)

        # Test hover state
        btn.enabled = True
        btn.hover = True
        btn.draw(self.surface)

    def test_button_update(self):
        btn = Button("TEST", 0, 0, 100, 50, "test_id")
        # Collides
        with unittest.mock.patch("pygame.mouse.get_pos", return_value=(50, 25)):
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
            res = btn.update([event])
            self.assertEqual(res, "test_id")

        # Doesn't collide
        with unittest.mock.patch("pygame.mouse.get_pos", return_value=(200, 200)):
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
            res = btn.update([event])
            self.assertIsNone(res)

    def test_draw_card(self):
        suits = ["♠", "♥", "♦", "♣"]
        for i, suit in enumerate(suits):
            c = Card(suit, "10")
            c.x, c.y = 10 * i, 10 * i
            draw_card(self.surface, c)

        # Prueba boca abajo
        c_down = Card("♥", "10")
        c_down.face_up = False
        draw_card(self.surface, c_down)

    def test_draw_suit_shape_default_color(self):
        from ui.card_renderer import draw_suit_shape

        draw_suit_shape(self.surface, "♠", 10, 10)

    def test_settings_get_font(self):
        with unittest.mock.patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}):
            font = st.get_font(10)
            self.assertIsNotNone(font)

        with unittest.mock.patch.dict(os.environ, {"SDL_VIDEODRIVER": "dummy"}):
            font = st.get_font(10)
            font.render("test", True, (0, 0, 0))
            font.get_rect()
            self.assertIsNotNone(font)

    def test_draw_result_overlay(self):
        draw_result_overlay(self.surface, "WIN", "YAY", st.WIN_GREEN, 10)
        draw_result_overlay(self.surface, "WIN", "YAY", st.WIN_GREEN, 30)

    def test_draw_table_base(self):
        draw_table_base(self.surface, 1000, 50, 250, 5, 1.5)

    def test_draw_scores(self):
        p_hand = [Card("♠", "10"), Card("♥", "7")]
        d_hand = [Card("♠", "10"), Card("♦", "10")]
        draw_scores(self.surface, p_hand, d_hand)

        d_hand[1].face_up = False
        draw_scores(self.surface, p_hand, d_hand)

    def test_draw_chips(self):
        chip_rects = [
            (pygame.Rect(50, 50, 80, 80), 10),
            (pygame.Rect(150, 50, 80, 80), 50),
        ]
        draw_chips(self.surface, chip_rects)

    def test_draw_coach(self):
        p_hand = [Card("♠", "10"), Card("♥", "7")]
        d_hand = [Card("♠", "10"), Card("♦", "10")]
        draw_coach(self.surface, p_hand, d_hand)

        # Soft hand
        p_hand_soft = [Card("♠", "A"), Card("♥", "7")]
        draw_coach(self.surface, p_hand_soft, d_hand)

    def test_draw_simulation_results(self):
        stats = {"profit": 100, "win_rate": 50.0, "ev": 0.05, "edge": 0, "bjs": 10}
        draw_simulation_results(self.surface, stats)


if __name__ == "__main__":
    unittest.main()
