"""Pruebas unitarias para snake.py.

Cubre funciones puras, enums, y clases clave del modulo principal del juego.
"""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.display.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snake import (  # noqa: E402
    WINDOW,
    TILE_SIZE,
    RANGE,
    SKINS,
    GAME_MODES,
    Direction,
    Screen,
    Obstacle,
    Snake,
    ScoreBoard,
    Button,
    make_obstacles,
    snap_to_grid,
    lerp_color,
    rainbow_color,
    random_pos,
)


class TestConstants(unittest.TestCase):
    """Valida que las constantes globales tengan los valores esperados."""

    def test_window_size(self):
        """WINDOW debe ser 800 pixeles."""
        self.assertEqual(WINDOW, 800)

    def test_tile_size(self):
        """TILE_SIZE debe ser 40 pixeles."""
        self.assertEqual(TILE_SIZE, 40)

    def test_range_structure(self):
        """RANGE debe ser una tupla de tres elementos."""
        self.assertEqual(len(RANGE), 3)

    def test_skins_keys(self):
        """SKINS debe contener los seis temas de skin definidos."""
        expected = {"Verde", "Fuego", "Hielo", "Arcoiris", "Dorado", "Neon"}
        self.assertEqual(set(SKINS.keys()), expected)

    def test_game_modes_count(self):
        """GAME_MODES debe contener exactamente cinco modos."""
        self.assertEqual(len(GAME_MODES), 5)


class TestPureFunctions(unittest.TestCase):
    """Pruebas para las funciones puras de calculo del modulo."""

    def test_snap_to_grid_returns_int(self):
        """snap_to_grid debe devolver un entero alineado al grid."""
        self.assertIsInstance(snap_to_grid(55), int)

    def test_lerp_color_at_zero(self):
        """lerp_color con t=0 debe devolver el color a."""
        self.assertEqual(lerp_color((0, 0, 0), (255, 255, 255), 0), (0, 0, 0))

    def test_lerp_color_at_one(self):
        """lerp_color con t=1 debe devolver el color b."""
        self.assertEqual(lerp_color((0, 0, 0), (255, 255, 255), 1), (255, 255, 255))

    def test_lerp_color_midpoint(self):
        """lerp_color con t=0.5 debe devolver el color intermedio."""
        self.assertEqual(lerp_color((0, 0, 0), (100, 100, 100), 0.5), (50, 50, 50))

    def test_rainbow_color_returns_rgb_tuple(self):
        """rainbow_color debe devolver una tupla RGB de tres componentes."""
        self.assertEqual(len(rainbow_color(0, 6)), 3)

    def test_random_pos_in_valid_range(self):
        """random_pos debe devolver coordenadas dentro del rango del tablero."""
        x, y = random_pos()
        self.assertGreaterEqual(x, RANGE[0])
        self.assertLessEqual(x, RANGE[1])


class TestDirection(unittest.TestCase):
    """Pruebas para el enum Direction."""

    def test_opposite_up_is_down(self):
        """El opuesto de UP debe ser DOWN."""
        self.assertEqual(Direction.UP.opposite(), Direction.DOWN)

    def test_opposite_left_is_right(self):
        """El opuesto de LEFT debe ser RIGHT."""
        self.assertEqual(Direction.LEFT.opposite(), Direction.RIGHT)

    def test_opposite_none_is_none(self):
        """El opuesto de NONE debe ser NONE."""
        self.assertEqual(Direction.NONE.opposite(), Direction.NONE)

    def test_to_pixels_right(self):
        """RIGHT debe convertirse en desplazamiento positivo en X."""
        self.assertEqual(Direction.RIGHT.to_pixels(), (TILE_SIZE, 0))

    def test_to_pixels_up(self):
        """UP debe convertirse en desplazamiento negativo en Y."""
        self.assertEqual(Direction.UP.to_pixels(), (0, -TILE_SIZE))


class TestScoreBoard(unittest.TestCase):
    """Pruebas para la clase ScoreBoard."""

    def setUp(self):
        """Inicializa un ScoreBoard limpio antes de cada prueba."""
        self.sb = ScoreBoard()

    def test_initial_score_is_zero(self):
        """El puntaje inicial debe ser cero."""
        self.assertEqual(self.sb.get_score(), 0)

    def test_add_points_increments_score(self):
        """add_points debe incrementar el puntaje correctamente."""
        self.sb.add_points(5)
        self.assertEqual(self.sb.get_score(), 5)

    def test_high_score_updates(self):
        """El high score debe actualizarse al superar el anterior."""
        self.sb.add_points(100)
        self.assertEqual(self.sb.get_high_score(), 100)

    def test_reset_archives_score(self):
        """reset debe archivar el puntaje en el historial."""
        self.sb.add_points(42)
        self.sb.reset()
        self.assertIn(42, self.sb.history)

    def test_reset_zeroes_score(self):
        """reset debe reiniciar el puntaje a cero."""
        self.sb.add_points(10)
        self.sb.reset()
        self.assertEqual(self.sb.get_score(), 0)

    def test_high_score_persists_after_reset(self):
        """El high score debe mantenerse despues del reset."""
        self.sb.add_points(50)
        self.sb.reset()
        self.assertEqual(self.sb.get_high_score(), 50)


class TestSnakeAndObstacle(unittest.TestCase):
    """Pruebas para las clases Snake, Obstacle y Button."""

    def setUp(self):
        """Inicializa una serpiente Verde y un obstaculo en (200,200)."""
        self.snake = Snake("Verde")
        self.obs = Obstacle([(200, 200)])

    def test_snake_initial_length(self):
        """La longitud inicial de la serpiente debe ser 1."""
        self.assertEqual(self.snake.length, 1)

    def test_snake_set_direction(self):
        """set_direction debe actualizar next_direction."""
        self.snake.set_direction(Direction.RIGHT)
        self.assertEqual(self.snake.next_direction, Direction.RIGHT)

    def test_snake_no_reverse(self):
        """La serpiente no debe invertir su direccion."""
        self.snake.direction = Direction.RIGHT
        self.snake.set_direction(Direction.LEFT)
        self.assertNotEqual(self.snake.next_direction, Direction.LEFT)

    def test_snake_grow(self):
        """grow debe incrementar la longitud objetivo."""
        self.snake.grow()
        self.assertEqual(self.snake.length, 2)

    def test_obstacle_collision_hit(self):
        """collides_with debe detectar colision cuando hay solapamiento."""
        r = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        r.center = (200, 200)
        self.assertTrue(self.obs.collides_with(r))

    def test_obstacle_no_collision_far(self):
        """collides_with debe devolver False cuando no hay solapamiento."""
        r = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        r.center = (600, 600)
        self.assertFalse(self.obs.collides_with(r))

    def test_button_hit_inside(self):
        """Button.hit debe devolver True para clic dentro del boton."""
        btn = Button((50, 75, 100, 50), "OK")
        self.assertTrue(btn.hit((100, 100)))

    def test_make_obstacles_returns_list_of_tuples(self):
        """make_obstacles debe devolver una lista de tuplas de dos elementos."""
        result = make_obstacles()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(result[0]), 2)

    def test_screen_enum_states(self):
        """Deben existir los estados MAIN_MENU, PLAYING, DEAD y PAUSED."""
        names = {s.name for s in Screen}
        for required in ("MAIN_MENU", "PLAYING", "DEAD", "PAUSED"):
            self.assertIn(required, names)


if __name__ == "__main__":
    unittest.main()
