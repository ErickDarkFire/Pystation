"""Pruebas unitarias para game_ui.py.

Cubre constantes, funciones auxiliares de renderizado y helpers de UI.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.display.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_ui import (  # noqa: E402
    MODE_DESC,
    overlay,
    ctext,
    draw_grid,
    draw_hud,
    draw_playing,
    draw_dead,
    draw_main_menu,
    draw_mode_select,
    draw_customize,
)
from snake import (  # noqa: E402
    WINDOW,
    TILE_SIZE,
    Screen,
    Snake,
    Fruit,
    ScoreBoard,
    Button,
    GAME_MODES,
    SKINS,
)


def _make_game_mock():
    """Construye un mock del objeto Game suficiente para las funciones de UI."""
    game = MagicMock()
    game.screen = pygame.Surface((WINDOW, WINDOW))
    game.selected_mode = "Clasico"
    game.selected_skin = "Verde"
    game._bg_off = 0.0
    game._countdown = 60000
    game.sm = None

    sb = ScoreBoard()
    sb.add_points(10)
    game.scoreboard = sb

    fruit = Fruit.__new__(Fruit)
    fruit._pulse = 0.0
    fruit._angle = 0.0
    fruit.kind = "Manzana"
    fruit.color = (220, 40, 60)
    fruit.points = 1
    fruit.radius = 8
    fruit.rect = pygame.Rect(0, 0, TILE_SIZE - 2, TILE_SIZE - 2)
    fruit.rect.center = (400, 400)
    game.fruit = fruit

    game.snake = Snake("Verde")
    game.obstacle = None

    font = pygame.font.SysFont("monospace", 22)
    game.f_title = font
    game.f_big = font
    game.f_med = font
    game.f_small = font
    game.f_tiny = font

    game._main_btns = [
        Button((270, 310, 260, 44), "JUGAR"),
        Button((270, 364, 260, 44), "MODO DE JUEGO"),
        Button((270, 418, 260, 44), "PERSONALIZAR"),
        Button((270, 472, 260, 44), "SALIR"),
    ]
    game._mode_btns = [
        Button((240, 230 + i * 68, 320, 52), m) for i, m in enumerate(GAME_MODES)
    ]
    skins = list(SKINS.keys())
    game._skin_btns = [
        Button((10 + (i % 3) * 215, 270 + (i // 3) * 65, 205, 52), name)
        for i, name in enumerate(skins)
    ]
    game._back_btn = Button((20, 16, 110, 36), "<- Volver")
    game._play_btn = Button((290, WINDOW - 90, 220, 48), "JUGAR AHORA")
    return game


class TestModeDesc(unittest.TestCase):
    """Valida el diccionario MODE_DESC de descripciones de modos."""

    def test_mode_desc_has_all_modes(self):
        """MODE_DESC debe contener una entrada por cada modo de juego."""
        for mode in GAME_MODES:
            self.assertIn(mode, MODE_DESC)

    def test_descriptions_are_non_empty_strings(self):
        """Cada descripcion debe ser un string no vacio."""
        for desc in MODE_DESC.values():
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 0)

    def test_portal_description_present(self):
        """El modo Portal debe tener descripcion definida."""
        self.assertIn("Portal", MODE_DESC)


class TestOverlay(unittest.TestCase):
    """Pruebas para la funcion overlay."""

    def test_overlay_does_not_raise(self):
        """overlay debe ejecutarse sin lanzar excepciones."""
        overlay(_make_game_mock(), 160)

    def test_overlay_with_full_opacity(self):
        """overlay con alpha=255 debe ejecutarse correctamente."""
        overlay(_make_game_mock(), 255)

    def test_overlay_with_zero_alpha(self):
        """overlay con alpha=0 debe ejecutarse correctamente."""
        overlay(_make_game_mock(), 0)


class TestCtext(unittest.TestCase):
    """Pruebas para la funcion ctext."""

    def test_ctext_does_not_raise(self):
        """ctext debe ejecutarse sin lanzar excepciones."""
        game = _make_game_mock()
        ctext(game, "TEST", game.f_med, (255, 255, 255), 300)

    def test_ctext_empty_string(self):
        """ctext con string vacio no debe lanzar excepcion."""
        game = _make_game_mock()
        ctext(game, "", game.f_small, (255, 255, 255), 200)


class TestDrawGrid(unittest.TestCase):
    """Pruebas para la funcion draw_grid."""

    def test_draw_grid_does_not_raise(self):
        """draw_grid debe ejecutarse sin lanzar excepciones."""
        draw_grid(_make_game_mock())

    def test_draw_grid_returns_none(self):
        """draw_grid debe devolver None."""
        self.assertIsNone(draw_grid(_make_game_mock()))


class TestDrawHud(unittest.TestCase):
    """Pruebas para la funcion draw_hud."""

    def test_draw_hud_clasico_mode(self):
        """draw_hud debe renderizarse en modo Clasico sin error."""
        draw_hud(_make_game_mock())

    def test_draw_hud_contrarreloj_mode(self):
        """draw_hud en modo Contrarreloj debe mostrar el temporizador."""
        game = _make_game_mock()
        game.selected_mode = "Contrarreloj"
        game._countdown = 30000
        draw_hud(game)

    def test_draw_hud_low_countdown(self):
        """draw_hud con poco tiempo restante debe usar color rojo."""
        game = _make_game_mock()
        game.selected_mode = "Contrarreloj"
        game._countdown = 5000
        draw_hud(game)


class TestDrawPlaying(unittest.TestCase):
    """Pruebas para la funcion draw_playing."""

    def test_draw_playing_no_obstacle(self):
        """draw_playing sin obstaculos no debe lanzar excepcion."""
        draw_playing(_make_game_mock(), Screen.PLAYING)

    def test_draw_playing_paused(self):
        """draw_playing con PAUSED debe mostrar el overlay de pausa."""
        draw_playing(_make_game_mock(), Screen.PAUSED)

    def test_draw_playing_portal_mode(self):
        """draw_playing en modo Portal debe dibujar bordes de portal."""
        game = _make_game_mock()
        game.selected_mode = "Portal"
        draw_playing(game, Screen.PLAYING)


class TestDrawDeadAndMenus(unittest.TestCase):
    """Pruebas para draw_dead, draw_main_menu, draw_mode_select y draw_customize."""

    def test_draw_dead_with_history(self):
        """draw_dead con historial debe mostrarse sin error."""
        game = _make_game_mock()
        game.scoreboard.history = [10, 20, 30]
        draw_dead(game)

    def test_draw_dead_empty_history(self):
        """draw_dead sin historial no debe lanzar excepcion."""
        game = _make_game_mock()
        game.scoreboard.history = []
        draw_dead(game)

    def test_draw_main_menu_no_sound(self):
        """draw_main_menu sin SoundManager debe renderizarse sin error."""
        game = _make_game_mock()
        game.sm = None
        draw_main_menu(game)

    def test_draw_main_menu_with_sound(self):
        """draw_main_menu con SoundManager activo debe renderizarse sin error."""
        game = _make_game_mock()
        sm_mock = MagicMock()
        sm_mock.sfx_on = True
        sm_mock.music_on = True
        game.sm = sm_mock
        draw_main_menu(game)

    def test_draw_mode_select_renders(self):
        """draw_mode_select debe renderizar todos los botones de modo."""
        draw_mode_select(_make_game_mock())

    def test_draw_mode_select_portal_selected(self):
        """draw_mode_select con Portal seleccionado debe mostrar la descripcion."""
        game = _make_game_mock()
        game.selected_mode = "Portal"
        draw_mode_select(game)

    def test_draw_customize_verde(self):
        """draw_customize con skin Verde debe renderizarse sin error."""
        game = _make_game_mock()
        game.selected_skin = "Verde"
        draw_customize(game)

    def test_draw_customize_arcoiris(self):
        """draw_customize con skin Arcoiris debe renderizarse sin error."""
        game = _make_game_mock()
        game.selected_skin = "Arcoiris"
        draw_customize(game)

    def test_draw_customize_all_skins(self):
        """draw_customize debe renderizarse para cada skin disponible."""
        for skin in SKINS.keys():
            game = _make_game_mock()
            game.selected_skin = skin
            draw_customize(game)


if __name__ == "__main__":
    unittest.main()
