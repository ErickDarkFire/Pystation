import unittest
from unittest.mock import patch
import pygame

from core.game import Game
from models.card import Card


class TestBlackjackSystemBDD(unittest.TestCase):
    """
    Pruebas de sistema/interfaz BDD
    """

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.game = Game()

        self.game.shoe.cards.clear()

    def tearDown(self):
        pass

    def simulate_click(self, x, y):
        """Simula un click del mouse en una coordenada x, y"""
        with patch("pygame.mouse.get_pos", return_value=(x, y)):
            event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, {"pos": (x, y), "button": 1}
            )

            if self.game.state == "BETTING":
                for r, v in self.game.chip_rects:
                    if r.collidepoint(event.pos) and self.game.player.money >= v:
                        self.game.player.money -= v
                        self.game.player.current_bet += v

            self.game.update([event])

    def test_dado_usuario_hace_apuesta_cuando_reparte_cartas_entonces_estado_juego_cambia(
        self,
    ):
        # Given
        self.assertEqual(self.game.state, "BETTING")
        self.assertEqual(self.game.player.current_bet, 0)

        self.game.shoe.cards = [
            Card("♠", "10"),
            Card("♥", "10"),
            Card("♦", "9"),
            Card("♣", "9"),
        ]

        # When
        # Simular click en la ficha de $10 (x=50, y=st.HEIGHT-220 = 380 aprox)
        ficha_10_rect = self.game.chip_rects[0][0]
        self.simulate_click(ficha_10_rect.centerx, ficha_10_rect.centery)

        # Simular click en DEAL
        self.simulate_click(
            self.game.btn_deal.rect.centerx, self.game.btn_deal.rect.centery
        )

        # Then
        self.assertEqual(self.game.player.current_bet, 10)
        self.assertEqual(self.game.state, "PLAYING")
        self.assertEqual(len(self.game.player.hand), 2)
        self.assertEqual(len(self.game.dealer.hand), 2)

    def test_dado_jugador_con_manos_bajas_cuando_pide_carta_y_se_pasa_entonces_pierde_inmediatamente(
        self,
    ):
        # Given
        self.game.player.current_bet = 50  # Forzamos una apuesta válida
        self.game.state = "BETTING"

        # Preparamos las cartas
        # Deal: Player 10, Dealer 9, Player 10, Dealer 9 -> Player tiene 20
        # Hit: Player (5) -> Player tiene 25 (Bust)
        self.game.shoe.cards = [
            Card("♠", "5"),  # Carta extra para el Hit
            Card("♠", "9"),  # Dealer 2
            Card("♥", "10"),  # Player 2
            Card("♦", "9"),  # Dealer 1
            Card("♣", "10"),  # Player 1
        ]

        self.simulate_click(
            self.game.btn_deal.rect.centerx, self.game.btn_deal.rect.centery
        )
        self.assertEqual(self.game.state, "PLAYING")

        # When
        self.simulate_click(
            self.game.btn_hit.rect.centerx, self.game.btn_hit.rect.centery
        )

        # Then
        self.assertEqual(len(self.game.player.hand), 3)  # Tomo una carta
        self.assertEqual(self.game.state, "RESULT")  # Termino el juego
        self.assertEqual(self.game.msg_main, "DEALER WINS")  # Perdio por Bust

    def test_dado_jugador_se_planta_cuando_dealer_tiene_menos_entonces_jugador_gana(
        self,
    ):
        # Given
        self.game.player.current_bet = 100
        self.game.player.money = 900  # Refleja el dinero tras apostar 100 de 1000
        self.game.state = "BETTING"

        # Preparamos cartas:
        # Player saca 20 (10, 10), Dealer saca 17 (10, 7)
        self.game.shoe.cards = [
            Card("♠", "7"),  # Dealer 2
            Card("♥", "10"),  # Player 2
            Card("♦", "10"),  # Dealer 1
            Card("♣", "10"),  # Player 1
        ]

        # Repartir
        self.simulate_click(
            self.game.btn_deal.rect.centerx, self.game.btn_deal.rect.centery
        )

        # When presionar Stand
        self.simulate_click(
            self.game.btn_stand.rect.centerx, self.game.btn_stand.rect.centery
        )

        event_dummy = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (0, 0)})
        self.game.update([event_dummy])

        # Then
        self.assertEqual(self.game.state, "RESULT")
        self.assertEqual(self.game.msg_main, "YOU WIN!")
        self.assertEqual(self.game.player.money, 1100)


if __name__ == "__main__":
    unittest.main()
