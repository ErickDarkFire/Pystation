import os
import unittest
from unittest.mock import MagicMock, patch

os.environ["SDL_AUDIODRIVER"] = "dummy"

from sound_manager import Sonidos  # noqa: E402


class TestSoundManager(unittest.TestCase):

    @patch("pygame.mixer.get_init", return_value=True)
    @patch("os.path.exists", return_value=False)
    def test_cargar_sonido_inexistente_regresa_none(self, mock_exists, mock_get_init):
        sonidos = Sonidos()

        resultado = sonidos.cargar_sonido("sound/no_existe.wav")

        self.assertIsNone(resultado)

    @patch("pygame.mixer.get_init", return_value=True)
    @patch("os.path.exists", return_value=True)
    @patch("pygame.mixer.Sound")
    def test_cargar_sonido_existente_regresa_sonido(
        self, mock_sound, mock_exists, mock_get_init
    ):
        sonido_mock = MagicMock()
        mock_sound.return_value = sonido_mock

        sonidos = Sonidos()

        resultado = sonidos.cargar_sonido("sound/rebote.ogg")

        self.assertEqual(resultado, sonido_mock)

    def test_reproducir_con_none_no_falla(self):
        sonidos = Sonidos()

        sonidos.reproducir(None)

    def test_reproducir_sonido_valido(self):
        sonidos = Sonidos()
        sonido_mock = MagicMock()

        sonidos.reproducir(sonido_mock)

        sonido_mock.play.assert_called_once()

    def test_reproducir_rebote(self):
        sonidos = Sonidos()
        sonidos.sonido_rebote = MagicMock()

        sonidos.reproducir_rebote()

        sonidos.sonido_rebote.play.assert_called_once()

    def test_reproducir_punto(self):
        sonidos = Sonidos()
        sonidos.sonido_punto = MagicMock()

        sonidos.reproducir_punto()

        sonidos.sonido_punto.play.assert_called_once()

    def test_reproducir_ganador(self):
        sonidos = Sonidos()
        sonidos.sonido_ganador = MagicMock()

        sonidos.reproducir_ganador()

        sonidos.sonido_ganador.play.assert_called_once()


if __name__ == "__main__":
    unittest.main()
