import unittest
import os
import sys
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
ruta_raiz_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ruta_raiz_proyecto)
sys.path.append(ruta_raiz_proyecto)

from craps_game import CrapsGame  # noqa: E402


class TestCrapsGame(unittest.TestCase):
    def setUp(self):
        # Inicialización mínima para tests
        self.game = CrapsGame()

    def test_initial_state(self):
        self.assertEqual(self.game.saldo, 500)
        self.assertEqual(self.game.apuesta, 10)
        self.assertIsNone(self.game.punto)

    def test_apuesta_increment(self):
        initial_apuesta = self.game.apuesta
        self.game.apuesta += 10
        self.assertEqual(self.game.apuesta, initial_apuesta + 10)

    @patch("random.randint")
    @patch("pygame.time.delay")
    def test_procesar_tiro_natural_ganador(self, mock_delay, mock_randint):
        """Verifica que un tiro inicial de 7 otorgue una victoria."""
        # 30 valores para el ciclo de animación + 2 valores finales (3 + 4 = 7)
        valores_animacion = [1] * 30
        valores_finales = [3, 4]
        mock_randint.side_effect = valores_animacion + valores_finales
        self.game.procesar_tiro()
        self.assertEqual(self.game.ganadas, 1)
        self.assertEqual(self.game.saldo, 510)
        self.assertIsNone(self.game.punto)

    @patch("random.randint")
    @patch("pygame.time.delay")
    def test_procesar_tiro_craps_perdedor(self, mock_delay, mock_randint):
        """Verifica que un tiro inicial de 3 sume una derrota."""
        valores_animacion = [1] * 30
        valores_finales = [1, 2]
        mock_randint.side_effect = valores_animacion + valores_finales
        self.game.procesar_tiro()
        self.assertEqual(self.game.perdidas, 1)
        self.assertEqual(self.game.saldo, 490)
        self.assertIsNone(self.game.punto)

    @patch("random.randint")
    @patch("pygame.time.delay")
    def test_procesar_tiro_establece_punto(self, mock_delay, mock_randint):
        """Verifica que un tiro inicial de 4 establezca el punto."""
        valores_animacion = [1] * 30
        valores_finales = [2, 2]
        mock_randint.side_effect = valores_animacion + valores_finales
        self.game.procesar_tiro()
        self.assertEqual(self.game.punto, 4)
        self.assertEqual(self.game.ganadas, 0)
        self.assertEqual(self.game.perdidas, 0)

    @patch("random.randint")
    @patch("pygame.time.delay")
    def test_lograr_punto_ganado(self, mock_delay, mock_randint):
        """Verifica que igualar el punto establecido otorgue la victoria."""
        self.game.punto = 4
        valores_animacion = [1] * 30
        valores_finales = [2, 2]
        mock_randint.side_effect = valores_animacion + valores_finales
        self.game.procesar_tiro()
        self.assertEqual(self.game.ganadas, 1)
        self.assertEqual(self.game.saldo, 510)
        self.assertIsNone(self.game.punto)

    @patch("random.randint")
    @patch("pygame.time.delay")
    def test_siete_fuera_pierde_punto(self, mock_delay, mock_randint):
        """Verifica que sacar 7 teniendo un punto activo resulte en derrota."""
        self.game.punto = 4
        valores_animacion = [1] * 30
        valores_finales = [3, 4]
        mock_randint.side_effect = valores_animacion + valores_finales
        self.game.procesar_tiro()
        self.assertEqual(self.game.perdidas, 1)
        self.assertEqual(self.game.saldo, 490)
        self.assertIsNone(self.game.punto)

    @patch("pygame.time.delay")
    def test_bancarrota_recarga_saldo(self, mock_delay):
        """Verifica que si el saldo es menor a la apuesta, se recarguen $500."""
        self.game.saldo = 5
        self.game.apuesta = 10
        self.game.procesar_tiro()
        self.assertEqual(self.game.saldo, 505)
        self.assertIn("Bancarrota", self.game.mensaje)


if __name__ == "__main__":
    unittest.main()
