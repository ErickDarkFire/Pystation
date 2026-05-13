"""Pruebas unitarias para sound_manager.py.

Cubre funciones de sintesis de audio, SoundManager y el singleton.
"""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sound_manager import (  # noqa: E402
    SAMPLE_RATE,
    CHANNELS,
    VOL_SFX,
    VOL_MUSIC,
    _make_tone,
    _make_chord,
    _make_noise_burst,
    _arr_to_sound,
    SoundManager,
    get_sound_manager,
)


class TestAudioConstants(unittest.TestCase):
    """Valida las constantes de configuracion de audio."""

    def test_sample_rate(self):
        """SAMPLE_RATE debe ser 44100 Hz."""
        self.assertEqual(SAMPLE_RATE, 44100)

    def test_channels(self):
        """CHANNELS debe ser 2 (estereo)."""
        self.assertEqual(CHANNELS, 2)

    def test_vol_sfx_in_range(self):
        """VOL_SFX debe estar entre 0 y 1."""
        self.assertGreater(VOL_SFX, 0)
        self.assertLessEqual(VOL_SFX, 1)

    def test_vol_music_in_range(self):
        """VOL_MUSIC debe estar entre 0 y 1."""
        self.assertGreater(VOL_MUSIC, 0)
        self.assertLessEqual(VOL_MUSIC, 1)


class TestMakeTone(unittest.TestCase):
    """Pruebas para la funcion _make_tone."""

    def test_returns_ndarray(self):
        """_make_tone debe devolver un ndarray de numpy."""
        self.assertIsInstance(_make_tone(440, 0.1), np.ndarray)

    def test_shape_is_stereo(self):
        """El array resultante debe tener dos columnas (estereo)."""
        self.assertEqual(_make_tone(440, 0.1).shape[1], 2)

    def test_duration_matches_sample_count(self):
        """El numero de muestras debe coincidir con duration * SAMPLE_RATE."""
        result = _make_tone(440, 0.2)
        self.assertEqual(result.shape[0], int(SAMPLE_RATE * 0.2))

    def test_sine_wave(self):
        """_make_tone con wave='sine' debe ejecutarse sin error."""
        self.assertIsNotNone(_make_tone(440, 0.05, wave="sine"))

    def test_square_wave(self):
        """_make_tone con wave='square' debe ejecutarse sin error."""
        self.assertIsNotNone(_make_tone(440, 0.05, wave="square"))

    def test_sawtooth_wave(self):
        """_make_tone con wave='sawtooth' debe ejecutarse sin error."""
        self.assertIsNotNone(_make_tone(440, 0.05, wave="sawtooth"))

    def test_triangle_wave(self):
        """_make_tone con wave='triangle' debe ejecutarse sin error."""
        self.assertIsNotNone(_make_tone(440, 0.05, wave="triangle"))

    def test_dtype_is_int16(self):
        """El dtype del resultado debe ser int16."""
        self.assertEqual(_make_tone(440, 0.1).dtype, np.int16)


class TestMakeChord(unittest.TestCase):
    """Pruebas para la funcion _make_chord."""

    def test_returns_ndarray(self):
        """_make_chord debe devolver un ndarray de numpy."""
        self.assertIsInstance(_make_chord([261, 329, 392], 0.1), np.ndarray)

    def test_shape_is_stereo(self):
        """El array de chord debe tener dos columnas (estereo)."""
        self.assertEqual(_make_chord([261, 329], 0.1).shape[1], 2)

    def test_dtype_is_int16(self):
        """El dtype del chord debe ser int16."""
        self.assertEqual(_make_chord([440, 550], 0.1).dtype, np.int16)

    def test_multiple_frequencies(self):
        """_make_chord con multiples frecuencias debe mezclarlas."""
        result = _make_chord([261, 329, 392, 523], 0.1)
        self.assertEqual(result.shape[1], 2)


class TestMakeNoiseBurst(unittest.TestCase):
    """Pruebas para la funcion _make_noise_burst."""

    def test_returns_ndarray(self):
        """_make_noise_burst debe devolver un ndarray de numpy."""
        self.assertIsInstance(_make_noise_burst(0.1), np.ndarray)

    def test_shape_is_stereo(self):
        """El ruido debe tener dos columnas (estereo)."""
        self.assertEqual(_make_noise_burst(0.1).shape[1], 2)

    def test_dtype_is_int16(self):
        """El dtype del ruido debe ser int16."""
        self.assertEqual(_make_noise_burst(0.1).dtype, np.int16)


class TestSoundManager(unittest.TestCase):
    """Pruebas para la clase SoundManager."""

    def setUp(self):
        """Crea una instancia de SoundManager antes de cada prueba."""
        self.sm = SoundManager()

    def test_sfx_on_by_default(self):
        """SFX debe estar habilitado por defecto."""
        self.assertTrue(self.sm.sfx_on)

    def test_music_on_by_default(self):
        """La musica debe estar habilitada por defecto."""
        self.assertTrue(self.sm.music_on)

    def test_toggle_sfx_disables(self):
        """toggle_sfx debe deshabilitar SFX si estaban activos."""
        self.sm.toggle_sfx()
        self.assertFalse(self.sm.sfx_on)

    def test_toggle_sfx_reenables(self):
        """toggle_sfx dos veces debe volver al estado original."""
        self.sm.toggle_sfx()
        self.sm.toggle_sfx()
        self.assertTrue(self.sm.sfx_on)

    def test_toggle_music_disables(self):
        """toggle_music debe deshabilitar la musica si estaba activa."""
        self.sm.toggle_music()
        self.assertFalse(self.sm.music_on)

    def test_toggle_music_returns_bool(self):
        """toggle_music debe devolver el nuevo estado como bool."""
        self.assertIsInstance(self.sm.toggle_music(), bool)

    def test_play_valid_sfx_no_error(self):
        """play con SFX valido no debe lanzar excepcion."""
        self.sm.play("eat")

    def test_play_unknown_sfx_no_error(self):
        """play con nombre desconocido no debe lanzar excepcion."""
        self.sm.play("sfx_inexistente")

    def test_stop_music_no_error(self):
        """stop_music debe ejecutarse sin lanzar excepcion."""
        self.sm.stop_music()

    def test_theme_builders_has_six_keys(self):
        """_THEME_BUILDERS debe contener los seis niveles de musica."""
        self.assertEqual(set(SoundManager._THEME_BUILDERS.keys()), {0, 1, 2, 3, 4, 5})

    def test_arr_to_sound_converts_array(self):
        """_arr_to_sound debe convertir un array en un pygame.Sound."""
        arr = _make_tone(440, 0.05)
        snd = _arr_to_sound(arr)
        self.assertIsInstance(snd, pygame.mixer.Sound)


class TestGetSoundManagerSingleton(unittest.TestCase):
    """Pruebas para el singleton get_sound_manager."""

    def test_returns_sound_manager_instance(self):
        """get_sound_manager debe devolver una instancia de SoundManager."""
        self.assertIsInstance(get_sound_manager(), SoundManager)

    def test_singleton_same_instance(self):
        """Dos llamadas consecutivas deben devolver el mismo objeto."""
        self.assertIs(get_sound_manager(), get_sound_manager())


if __name__ == "__main__":
    unittest.main()
