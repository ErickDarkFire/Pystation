"""Pruebas de integración para Snake Deluxe v2.0.

Valida la interacción entre los componentes del juego usando el modo headless
de la clase Game. Cubre flujos completos de juego, transiciones de pantalla,
manejo de eventos y comportamiento por modo de juego.
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
    Game,
    Screen,
    Direction,
    Snake,
    Fruit,
    Obstacle,
    ScoreBoard,
    WINDOW,
    TILE_SIZE,
    BASE_SPEED,
    CHAOS_INTERVAL,
)


class TestGameInitialization(unittest.TestCase):
    """Valida el estado inicial del juego en modo headless."""

    def setUp(self):
        """Crea una instancia del juego en modo headless."""
        self.game = Game(headless=True)

    def test_initial_screen_is_main_menu(self):
        """El juego debe iniciar en la pantalla MAIN_MENU."""
        self.assertEqual(self.game.screen_id, Screen.MAIN_MENU)

    def test_initial_skin_is_verde(self):
        """El skin inicial debe ser Verde."""
        self.assertEqual(self.game.selected_skin, "Verde")

    def test_initial_mode_is_clasico(self):
        """El modo inicial debe ser Clasico."""
        self.assertEqual(self.game.selected_mode, "Clasico")

    def test_snake_is_created(self):
        """El juego debe tener una instancia de Snake."""
        self.assertIsInstance(self.game.snake, Snake)

    def test_fruit_is_created(self):
        """El juego debe tener una instancia de Fruit."""
        self.assertIsInstance(self.game.fruit, Fruit)

    def test_scoreboard_is_created(self):
        """El juego debe tener una instancia de ScoreBoard."""
        self.assertIsInstance(self.game.scoreboard, ScoreBoard)

    def test_frame_count_starts_at_zero(self):
        """El contador de frames debe iniciar en cero."""
        self.assertEqual(self.game.frame_count, 0)


class TestGameScreenTransitions(unittest.TestCase):
    """Valida las transiciones entre pantallas del juego."""

    def setUp(self):
        """Crea una instancia headless y llama _reset_game para ir a PLAYING."""
        self.game = Game(headless=True)
        self.game._reset_game()

    def test_reset_game_goes_to_playing(self):
        """_reset_game debe cambiar la pantalla a PLAYING."""
        self.assertEqual(self.game.screen_id, Screen.PLAYING)

    def test_go_to_menu_returns_to_main_menu(self):
        """_go_to_menu debe cambiar la pantalla a MAIN_MENU."""
        self.game._go_to_menu()
        self.assertEqual(self.game.screen_id, Screen.MAIN_MENU)

    def test_key_escape_from_playing_pauses(self):
        """Presionar ESC en PLAYING debe pausar el juego."""
        self.game.screen_id = Screen.PLAYING
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.game._key(event.key)
        self.assertEqual(self.game.screen_id, Screen.PAUSED)

    def test_key_escape_from_paused_resumes(self):
        """Presionar ESC en PAUSED debe reanudar el juego."""
        self.game.screen_id = Screen.PAUSED
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.game._key(event.key)
        self.assertEqual(self.game.screen_id, Screen.PLAYING)

    def test_key_p_toggles_pause(self):
        """Presionar P en PLAYING debe cambiar a PAUSED."""
        self.game.screen_id = Screen.PLAYING
        self.game._key(pygame.K_p)
        self.assertEqual(self.game.screen_id, Screen.PAUSED)

    def test_key_return_from_menu_starts_game(self):
        """Presionar RETURN en MAIN_MENU debe iniciar el juego."""
        self.game.screen_id = Screen.MAIN_MENU
        self.game._key(pygame.K_RETURN)
        self.assertEqual(self.game.screen_id, Screen.PLAYING)

    def test_key_space_from_dead_restarts(self):
        """Presionar SPACE en DEAD debe reiniciar el juego."""
        self.game.screen_id = Screen.DEAD
        self.game._key(pygame.K_SPACE)
        self.assertEqual(self.game.screen_id, Screen.PLAYING)


class TestSnakeMovementIntegration(unittest.TestCase):
    """Valida el movimiento de la serpiente integrado con el ciclo de juego."""

    def setUp(self):
        """Prepara el juego en PLAYING con la serpiente orientada a la derecha."""
        self.game = Game(headless=True)
        self.game._reset_game()
        self.game.snake.set_direction(Direction.RIGHT)
        self.game.snake.direction = Direction.RIGHT

    def test_snake_moves_after_interval(self):
        """La serpiente debe moverse al superar el intervalo de movimiento."""
        initial_center = list(self.game.snake.head.center)
        self.game._move_timer = BASE_SPEED + 1
        self.game._update_playing(BASE_SPEED + 1)
        new_center = list(self.game.snake.head.center)
        self.assertNotEqual(initial_center, new_center)

    def test_snake_does_not_move_before_interval(self):
        """La serpiente no debe moverse antes de cumplir el intervalo."""
        initial_center = list(self.game.snake.head.center)
        self.game._move_timer = 0
        self.game._update_playing(10)
        new_center = list(self.game.snake.head.center)
        self.assertEqual(initial_center, new_center)

    def test_key_right_sets_direction(self):
        """Presionar RIGHT debe actualizar la dirección de la serpiente."""
        self.game.screen_id = Screen.PLAYING
        self.game.snake.direction = Direction.UP
        self.game._key(pygame.K_RIGHT)
        self.assertEqual(self.game.snake.next_direction, Direction.RIGHT)

    def test_key_wasd_sets_direction_up(self):
        """Presionar W debe orientar la serpiente hacia arriba."""
        self.game.screen_id = Screen.PLAYING
        self.game.snake.direction = Direction.RIGHT
        self.game._key(pygame.K_w)
        self.assertEqual(self.game.snake.next_direction, Direction.UP)


class TestSnakeObstacleIntegration(unittest.TestCase):
    """Valida la detección de colisión entre Snake y Obstacle."""

    def test_snake_dies_on_obstacle_collision(self):
        """La serpiente debe morir al colisionar con un obstáculo."""
        game = Game(headless=True)
        game._reset_game()
        obs = Obstacle([(game.snake.head.centerx, game.snake.head.centery)])
        game.obstacle = obs
        result = game.snake.is_dead(portal=False, obstacle=obs)
        self.assertTrue(result)

    def test_no_collision_with_far_obstacle(self):
        """Un obstáculo lejano no debe causar muerte."""
        game = Game(headless=True)
        game._reset_game()
        obs = Obstacle([(20, 20)])
        game.snake.segments[0].center = (700, 700)
        result = game.snake.is_dead(portal=False, obstacle=obs)
        self.assertFalse(result)


class TestScoreBoardIntegration(unittest.TestCase):
    """Valida la integración entre ScoreBoard y el ciclo de juego."""

    def setUp(self):
        """Prepara el juego y posiciona la serpiente sobre la fruta."""
        self.game = Game(headless=True)
        self.game._reset_game()
        self.game.snake.set_direction(Direction.RIGHT)
        self.game.snake.direction = Direction.RIGHT

    def test_score_increases_on_fruit_eaten(self):
        """El puntaje debe aumentar cuando la serpiente come una fruta."""
        self.game.fruit.rect.center = self.game.snake.head.center
        self.game.fruit.points = 3
        initial_score = self.game.scoreboard.get_score()
        self.game.snake.eats_fruit(self.game.fruit)
        self.game.scoreboard.add_points(self.game.fruit.points)
        self.assertEqual(self.game.scoreboard.get_score(), initial_score + 3)

    def test_snake_grows_when_fruit_eaten(self):
        """La longitud de la serpiente debe aumentar al comer una fruta."""
        initial_length = self.game.snake.length
        self.game.snake.grow()
        self.assertEqual(self.game.snake.length, initial_length + 1)

    def test_speed_increases_with_score(self):
        """El intervalo de movimiento debe disminuir al acumular puntaje."""
        initial_interval = self.game._move_interval
        self.game.scoreboard.add_points(20)
        self.game._move_interval = max(45, BASE_SPEED - self.game.scoreboard.score * 2)
        self.assertLessEqual(self.game._move_interval, initial_interval)


class TestGameModeObstaculos(unittest.TestCase):
    """Valida el comportamiento específico del modo Obstaculos."""

    def test_obstaculos_mode_creates_obstacle(self):
        """El modo Obstaculos debe crear una instancia de Obstacle."""
        game = Game(headless=True)
        game.selected_mode = "Obstaculos"
        game._reset_game()
        self.assertIsNotNone(game.obstacle)
        self.assertIsInstance(game.obstacle, Obstacle)

    def test_clasico_mode_has_no_obstacle(self):
        """El modo Clasico no debe tener obstáculos."""
        game = Game(headless=True)
        game.selected_mode = "Clasico"
        game._reset_game()
        self.assertIsNone(game.obstacle)


class TestGameModeContrarreloj(unittest.TestCase):
    """Valida el modo Contrarreloj: cuenta regresiva y transición a DEAD."""

    def setUp(self):
        """Inicia el juego en modo Contrarreloj."""
        self.game = Game(headless=True)
        self.game.selected_mode = "Contrarreloj"
        self.game._reset_game()

    def test_countdown_decreases(self):
        """El countdown debe disminuir al llamar _update_playing."""
        initial = self.game._countdown
        self.game._update_playing(500)
        self.assertLess(self.game._countdown, initial)

    def test_game_ends_when_countdown_reaches_zero(self):
        """El juego debe terminar cuando el countdown llega a cero."""
        self.game._countdown = 10
        self.game._update_playing(100)
        self.assertEqual(self.game.screen_id, Screen.DEAD)


class TestGameModeCaos(unittest.TestCase):
    """Valida el modo Caos: reposicionamiento automático de la fruta."""

    def test_fruit_repositions_after_chaos_interval(self):
        """La fruta debe reposicionarse al cumplirse CHAOS_INTERVAL ms."""
        game = Game(headless=True)
        game.selected_mode = "Caos"
        game._reset_game()
        found_change = False
        for _ in range(20):
            game._chaos_timer = CHAOS_INTERVAL + 1
            game.fruit.rect.center = (200, 200)
            game._update_playing(1)
            if tuple(game.fruit.rect.center) != (200, 200):
                found_change = True
                break
        self.assertTrue(found_change or game._chaos_timer == 0)


class TestGameModePortal(unittest.TestCase):
    """Valida el modo Portal: wrapping en los bordes del tablero."""

    def test_portal_mode_detected_correctly(self):
        """_is_portal debe devolver True en modo Portal."""
        game = Game(headless=True)
        game.selected_mode = "Portal"
        self.assertTrue(game._is_portal())

    def test_clasico_mode_not_portal(self):
        """_is_portal debe devolver False en modo Clasico."""
        game = Game(headless=True)
        game.selected_mode = "Clasico"
        self.assertFalse(game._is_portal())

    def test_snake_wraps_through_right_wall_in_portal(self):
        """La serpiente debe aparecer al lado izquierdo al salir por la derecha."""
        game = Game(headless=True)
        game.selected_mode = "Portal"
        game._reset_game()
        game.snake.segments[0].center = (WINDOW - TILE_SIZE // 2, 400)
        game.snake.set_direction(Direction.RIGHT)
        game.snake.direction = Direction.RIGHT
        game.snake.next_direction = Direction.RIGHT
        game.snake.move(portal=True)
        head_x = game.snake.head.centerx
        self.assertLess(head_x, WINDOW // 2)


class TestFrameCountIntegration(unittest.TestCase):
    """Valida que el contador de frames avance correctamente."""

    def test_frame_count_increments_on_update(self):
        """frame_count debe incrementarse en cada llamada a update."""
        game = Game(headless=True)
        initial = game.frame_count
        game.update(16)
        self.assertEqual(game.frame_count, initial + 1)

    def test_frame_count_increments_multiple_times(self):
        """frame_count debe incrementarse en cada llamada sucesiva a update."""
        game = Game(headless=True)
        for _ in range(5):
            game.update(16)
        self.assertEqual(game.frame_count, 5)


if __name__ == "__main__":
    unittest.main()
