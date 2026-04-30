import unittest
from unittest.mock import patch
import pygame

from core.game import Game
from models.card import Card


class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = Game()

    def tearDown(self):
        pass

    def test_run_simulation(self):
        self.game.run_simulation()
        self.assertIsNotNone(self.game.sim_stats)
        self.assertIn("profit", self.game.sim_stats)
        self.assertIn("win_rate", self.game.sim_stats)
        self.assertEqual(self.game.state, "SIM_RESULT")

    def test_update_count(self):
        self.game.running_count = 0
        self.game.shoe.cards = [Card("♠", "A")] * 52

        # Cartas altas restan 1
        self.game.update_count(Card("♠", "A"))
        self.assertEqual(self.game.running_count, -1)
        self.game.update_count(Card("♠", "10"))
        self.assertEqual(self.game.running_count, -2)

        # Cartas bajas suman 1
        self.game.update_count(Card("♠", "2"))
        self.assertEqual(self.game.running_count, -1)
        self.game.update_count(Card("♠", "6"))
        self.assertEqual(self.game.running_count, 0)

        # Cartas neutrales no afectan
        self.game.update_count(Card("♠", "7"))
        self.assertEqual(self.game.running_count, 0)

    def test_get_true_count(self):
        self.game.running_count = 2
        # 6 barajas (312 cartas)
        self.assertEqual(len(self.game.shoe.cards), 312)
        # true_count = running_count / (len / 52) = 2 / (312/52) = 2 / 6 = 0.333
        self.assertAlmostEqual(self.game.get_true_count(), 0.3333333333333333)

    def test_handle_result_win(self):
        self.game.state = "DEALER_ANIM"
        self.game.player.current_bet = 50
        self.game.player.money = 1000

        # Anadir carta boca abajo para no dar error al revelar
        self.game.dealer.hand.append(Card("♠", "2"))
        self.game.dealer.hand.append(Card("♠", "2"))

        self.game.handle_result("WIN")
        self.assertEqual(self.game.state, "RESULT")
        self.assertEqual(self.game.player.money, 1100)  # Gano 100

    def test_handle_result_lose(self):
        self.game.player.current_bet = 50
        self.game.player.money = 1000
        self.game.dealer.hand.extend([Card("♠", "2"), Card("♠", "2")])
        self.game.handle_result("LOSE")
        self.assertEqual(self.game.player.money, 1000)  # Pierde, no recupera

    def test_handle_result_push(self):
        self.game.player.current_bet = 50
        self.game.player.money = 1000
        self.game.dealer.hand.extend([Card("♠", "2"), Card("♠", "2")])
        self.game.handle_result("PUSH")
        self.assertEqual(self.game.player.money, 1050)  # Recupera los 50

    def test_game_run_loop(self):
        with patch("pygame.event.get") as mock_get, patch(
            "sys.exit", side_effect=SystemExit
        ) as mock_exit, patch("pygame.quit"):

            e_click = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"pos": (50, 400), "button": 1}
            )
            e_quit = pygame.event.Event(pygame.QUIT)
            mock_get.side_effect = [[e_click], [e_quit]]
            self.game.state = "BETTING"
            self.game.player.money = 1000

            # Forzamos los rectángulos para que haga click exacto
            self.game.chip_rects = [(pygame.Rect(0, 0, 100, 500), 10)]

            with self.assertRaises(SystemExit):
                self.game.run()

            self.assertEqual(self.game.player.current_bet, 10)
            mock_exit.assert_called_once()

    def test_ui_events_in_states(self):
        self.game.coach_enabled = False
        with patch.object(
            self.game.btn_toggle_coach, "update", return_value="toggle_coach"
        ):
            self.game.update([])
            self.assertTrue(self.game.coach_enabled)

        self.game.state = "BETTING"
        with patch.object(
            self.game.btn_sim, "update", return_value="simulate"
        ), patch.object(self.game, "run_simulation") as mock_sim:
            self.game.update([])
            mock_sim.assert_called_once()

        m_start = self.game.player.money
        with patch.object(self.game.btn_add, "update", return_value="add"):
            self.game.update([])
            self.assertEqual(self.game.player.money, m_start + 1000)

        self.game.state = "SIM_RESULT"
        with patch.object(self.game.btn_reset, "update", return_value="reset"):
            self.game.update([])
            self.assertEqual(self.game.state, "BETTING")

        self.game.state = "RESULT"
        with patch.object(self.game.btn_reset, "update", return_value="reset"):
            self.game.update([])
            self.assertEqual(self.game.state, "BETTING")

        self.game.state = "PLAYING"
        self.game.player.current_bet = 10
        self.game.player.money = 100
        self.game.player.hand = []
        with patch.object(self.game.btn_double, "update", return_value="double"):
            self.game.shoe.cards = [Card("♠", "10")]
            self.game.update([])
            self.assertEqual(self.game.player.current_bet, 20)

        # btn_double con BUST
        self.game.state = "PLAYING"
        self.game.player.current_bet = 10
        self.game.player.money = 100
        self.game.player.hand = [Card("♠", "10"), Card("♥", "10")]
        self.game.dealer.hand = [Card("♠", "2"), Card("♥", "2")]
        with patch.object(self.game.btn_double, "update", return_value="double"):
            self.game.shoe.cards = [Card("♦", "10")]  # Roba otro 10 y revienta (30)
            self.game.update([])
            self.assertEqual(self.game.state, "RESULT")

    def test_dealer_anim_drawing_cards(self):
        self.game.state = "DEALER_ANIM"
        self.game.dealer.hand = [Card("♠", "2"), Card("♥", "3")]  # 5
        self.game.player.hand = [Card("♠", "10"), Card("♥", "10")]  # 20
        self.game.shoe.cards = [Card("♦", "10"), Card("♣", "10")]

        with patch("pygame.time.wait"):
            self.game.update([])  # Dealer roba 10 (total 15), sigue en DEALER_ANIM
            self.assertEqual(len(self.game.dealer.hand), 3)
            self.assertEqual(self.game.state, "DEALER_ANIM")

            self.game.update([])  # Dealer roba 10 (total 25), evalúa BUST
            self.assertEqual(len(self.game.dealer.hand), 4)
            self.assertEqual(self.game.state, "DEALER_ANIM")

            self.game.update([])  # Evalúa el 25 >= 17, se va a RESULT
            self.assertEqual(self.game.state, "RESULT")

        # Probar LOSE (Dealer gana)
        self.game.state = "DEALER_ANIM"
        self.game.dealer.hand = [Card("♠", "10"), Card("♥", "10")]  # 20
        self.game.player.hand = [Card("♠", "10"), Card("♥", "8")]  # 18
        with patch("pygame.time.wait"):
            self.game.update([])  # Ya tiene 20 (>=17), evalúa
            self.assertEqual(self.game.state, "RESULT")
            self.assertEqual(self.game.msg_main, "DEALER WINS")

        # Probar PUSH (Empate)
        self.game.state = "DEALER_ANIM"
        self.game.dealer.hand = [Card("♠", "10"), Card("♥", "10")]  # 20
        self.game.player.hand = [Card("♠", "10"), Card("♥", "10")]  # 20
        with patch("pygame.time.wait"):
            self.game.update([])  # Ya tiene 20 (>=17), evalúa
            self.assertEqual(self.game.state, "RESULT")
            self.assertEqual(self.game.msg_main, "PUSH")

    def test_game_draw_states(self):
        states = ["BETTING", "PLAYING", "RESULT", "SIM_RESULT"]
        self.game.sim_stats = {"profit": 0, "win_rate": 0, "ev": 0, "edge": 0, "bjs": 0}
        self.game.msg_main, self.game.msg_sub, self.game.msg_color = (
            "TEST",
            "TEST",
            (255, 255, 255),
        )

        # Añadir cartas para cubrir draw_card() dentro del loop
        self.game.player.hand = [Card("♠", "10")]
        self.game.dealer.hand = [Card("♥", "10"), Card("♥", "2")]

        for s in states:
            self.game.state = s
            self.game.draw()

    def test_sim_double_bust(self):
        with patch("core.game.calculate_score", return_value=22):
            with patch("models.hand.get_strategy_advice", return_value="DOUBLE"):
                self.game.run_simulation()


if __name__ == "__main__":
    unittest.main()
