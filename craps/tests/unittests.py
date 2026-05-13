import unittest
import os
import sys

# Añadir directorio raíz al path para importar el juego
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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


if __name__ == "__main__":
    unittest.main()
