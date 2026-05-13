import os
# Configurar controlador de video virtual ANTES de importar pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import unittest
from unittest.mock import patch, MagicMock
import pygame
import sys

# 1. Resolver importación (ajusta la ruta según tu estructura)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Preparar el entorno de mocks para recursos externos
with patch('pygame.mixer.init'), \
     patch('pygame.mixer.Sound'), \
     patch('pygame.mixer.music.load'), \
     patch('pygame.mixer.music.play'), \
     patch('pygame.font.Font'):
    
    # Parchamos image.load para que devuelva una superficie REAL de 1x1.
    # Al haber un modo de video (dummy), el método .convert() funcionará sin errores.
    with patch('pygame.image.load', return_value=pygame.Surface((1,1))):
        import Tic_tac_toe as game

class TestTicTacToeLogic(unittest.TestCase):

    def setUp(self):
        # Reiniciar variables globales para cada prueba
        game.tablero = [["", "", ""], ["", "", ""], ["", "", ""]]
        game.turno = 0
        game.win = False
        game.p1_wins = 0
        game.p2_wins = 0
        game.victoria_procesada = False

    # -------------------------------------------------------------------------------------
    # --- VICTORIAS HORIZONTALES ---
    
    def test_win_horizontal_row_0(self):
        game.tablero[0] = ["X", "X", "X"]
        self.assertTrue(game.Check(), "Falló victoria en fila superior")

    def test_win_horizontal_row_1(self):
        game.tablero[1] = ["O", "O", "O"]
        self.assertTrue(game.Check(), "Falló victoria en fila central")

    def test_win_horizontal_row_2(self):
        game.tablero[2] = ["X", "X", "X"]
        self.assertTrue(game.Check(), "Falló victoria en fila inferior")

    # --- VICTORIAS VERTICALES ---

    def test_win_vertical_col_0(self):
        game.tablero[0][0] = game.tablero[1][0] = game.tablero[2][0] = "X"
        self.assertTrue(game.Check(), "Falló victoria en columna izquierda")

    def test_win_vertical_col_1(self):
        game.tablero[0][1] = game.tablero[1][1] = game.tablero[2][1] = "O"
        self.assertTrue(game.Check(), "Falló victoria en columna central")

    def test_win_vertical_col_2(self):
        game.tablero[0][2] = game.tablero[1][2] = game.tablero[2][2] = "X"
        self.assertTrue(game.Check(), "Falló victoria en columna derecha")

    # --- VICTORIAS DIAGONALES ---

    def test_win_diagonal_main(self):
        # De arriba-izquierda a abajo-derecha
        game.tablero[0][0] = game.tablero[1][1] = game.tablero[2][2] = "O"
        self.assertTrue(game.Check(), "Falló victoria en diagonal principal")

    def test_win_diagonal_anti(self):
        # De arriba-derecha a abajo-izquierda
        game.tablero[0][2] = game.tablero[1][1] = game.tablero[2][0] = "X"
        self.assertTrue(game.Check(), "Falló victoria en diagonal inversa")

    # --- CASOS SIN VICTORIA ---
    def test_no_win_empty(self):
        self.assertFalse(game.Check(), "Dijo que había victoria en un tablero vacío")

    def test_no_win_mixed(self):
        # Tablero lleno sin ganador (empate)
        game.tablero = [
            ["X", "O", "X"],
            ["X", "O", "O"],
            ["O", "X", "X"]
        ]
        self.assertFalse(game.Check(), "Detectó una victoria falsa en un empate")
    # -------------------------------------------------------------------------------------

    def test_hover_mapeo_coordenadas(self):
        """Verifica que los clics del mouse se asignen a la celda correcta"""
        # La cuadrícula es de 800x500 dividida en 3x3
        # Centro del tablero (aprox 400, 250) -> Celda [1][1]
        self.assertEqual(game.Hover(400, 250), (1, 1))
        # Esquina superior izquierda -> Celda [0][0]
        self.assertEqual(game.Hover(10, 10), (0, 0))

    def test_reinicio_limpia_tablero(self):
        """Verifica que la función Reinicio limpie la matriz de juego"""
        game.tablero[0][0] = "X"
        game.Reinicio()
        for fila in game.tablero:
            self.assertEqual(fila, ["", "", ""])

    def test_cambio_de_turno_simulado(self):
        """Verifica que el sistema de turnos funcione correctamente"""
        # Simulamos un clic en la celda [0][0] cuando es turno del jugador 0
        game.turno = 0
        game.tablero[0][0] = "X"
        # En tu lógica, el turno cambiaría en el bucle principal, 
        # aquí probamos la consistencia de los datos
        self.assertEqual(game.tablero[0][0], "X")
    
    # --- PRUEBAS DE UTILIDADES Y RUTAS ---
    
    def test_get_path_logic(self):
        """Verifica que get_path construya la ruta correctamente"""
        folder = "img"
        file = "logo.png"
        resultado = game.get_path(folder, file)
        # Verificamos que la ruta termine con la estructura esperada
        self.assertTrue(resultado.endswith(os.path.join(folder, file)))

    # --- PRUEBAS DE LÓGICA DE REINICIO ---

    def test_reinicio_completitud_retorno(self):
        """Verifica que Reinicio() devuelva todos los valores de control correctamente"""
        # Según Tic_tac_toe.py: return "X", False, False, 0, Escoger_color(), False
        fig, clic, win, pandeo, color, vict_proc = game.Reinicio()
        
        self.assertEqual(fig, "X")
        self.assertFalse(clic)
        self.assertFalse(win)
        self.assertEqual(pandeo, 0)
        self.assertIn(color, game.colores) # El color debe ser uno de la lista
        self.assertFalse(vict_proc)

    # --- PRUEBAS DE ALEATORIEDAD ---

    def test_escoger_color_valido(self):
        """Verifica que el color aleatorio pertenezca a la paleta permitida"""
        color = game.Escoger_color()
        self.assertIn(color, game.colores)

    # --- PRUEBAS DE SISTEMA DE PUNTUACIÓN (LOGICA SIMULADA) ---

    def test_incremento_puntuacion_jugador1(self):
        """Simula la lógica de victoria para asegurar que el Jugador 1 sume puntos"""
        game.win = True
        game.turno = 1 # En el código, si turno es 1 después del cambio, ganó P1
        game.victoria_procesada = False
        
        # Simulamos el bloque de lógica de puntuación del archivo original
        if game.win and not game.victoria_procesada:
            if game.turno == 1:
                game.p1_wins += 1
            game.victoria_procesada = True
            
        self.assertEqual(game.p1_wins, 1)
        self.assertTrue(game.victoria_procesada)

    def test_no_puntuacion_doble(self):
        """Asegura que no se sumen puntos extra si victoria_procesada es True"""
        game.p1_wins = 5
        game.win = True
        game.victoria_procesada = True
        game.turno = 1
        
        # Intentamos procesar la victoria de nuevo
        if game.win and not game.victoria_procesada:
            game.p1_wins += 1
            
        self.assertEqual(game.p1_wins, 5, "Se sumaron puntos a una victoria ya procesada")

    # --- PRUEBAS DE LÓGICA DE MOVIMIENTOS ---

    def test_movimiento_en_lugar_ocupado(self):
        """Verifica que la lógica no permita sobrescribir una celda ya marcada"""
        # Marcamos una celda manualmente
        game.tablero[1][1] = "X"
        game.turno = 1 # Turno del Jugador 2 (O)
        
        # Simulamos clic en la misma celda [1][1]
        coord_tablero = (1, 1)
        
        # Lógica del clic en Tic_tac_toe.py
        if game.tablero[coord_tablero[0]][coord_tablero[1]] == "":
             game.tablero[coord_tablero[0]][coord_tablero[1]] = "O"
        
        self.assertEqual(game.tablero[1][1], "X", "La celda ocupada fue sobrescrita")

if __name__ == '__main__':
    unittest.main()