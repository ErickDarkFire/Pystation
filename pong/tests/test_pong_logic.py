import os
import json
import tempfile
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest  # noqa: E402
import pygame  # noqa: E402
import pong as juego  # noqa: E402


class SonidosTest:
    def reproducir_rebote(self):
        pass

    def reproducir_punto(self):
        pass

    def reproducir_ganador(self):
        pass


class TeclasFake:
    def __init__(self, teclas_presionadas):
        self.teclas_presionadas = teclas_presionadas

    def __getitem__(self, tecla):
        return tecla in self.teclas_presionadas


class TestPongLogic(unittest.TestCase):

    def setUp(self):
        juego.sonidos = SonidosTest()
        juego.reiniciar_juego()
        juego.vel_pelota_x = 5
        juego.vel_pelota_y = 5

    def test_obtener_posicion_centro_jugador(self):
        esperado = juego.ALTO // 2 - juego.JUGADOR_ALTO // 2
        self.assertEqual(juego.obtener_posicion_centro_jugador(), esperado)

    def test_reiniciar_marcador(self):
        juego.score1 = 3
        juego.score2 = 4
        juego.reiniciar_marcador()

        self.assertEqual(juego.score1, 0)
        self.assertEqual(juego.score2, 0)

    def test_alternar_pausa_activa_y_desactiva(self):
        self.assertFalse(juego.pausado)
        juego.alternar_pausa()
        self.assertTrue(juego.pausado)
        juego.alternar_pausa()
        self.assertFalse(juego.pausado)

    def test_que_no_puede_pausar_si_game_over_es_true(self):
        juego.game_over = True
        juego.pausado = False
        juego.alternar_pausa()

        self.assertFalse(juego.pausado)

    def test_mover_jugador_arriba(self):
        posicion_inicial = juego.jugador1.y
        juego.mover_jugador_arriba(juego.jugador1)

        self.assertEqual(juego.jugador1.y, posicion_inicial - juego.VEL_JUGADOR)

    def test_mover_jugador_arriba_no_sale_de_pantalla(self):
        juego.jugador1.y = 0
        juego.mover_jugador_arriba(juego.jugador1)
        self.assertEqual(juego.jugador1.y, 0)

    def test_mover_jugador_abajo(self):
        posicion_inicial = juego.jugador1.y
        juego.mover_jugador_abajo(juego.jugador1)

        self.assertEqual(juego.jugador1.y, posicion_inicial + juego.VEL_JUGADOR)

    def test_mover_jugador_abajo_no_sale_de_pantalla(self):
        juego.jugador1.y = juego.ALTO - juego.JUGADOR_ALTO
        juego.mover_jugador_abajo(juego.jugador1)

        self.assertEqual(juego.jugador1.y, juego.ALTO - juego.JUGADOR_ALTO)

    def test_mover_posicion_pelota_x(self):
        juego.pelota.x = 100
        juego.vel_pelota_x = 5
        juego.mover_posicion_pelota()

        self.assertEqual(juego.pelota.x, 105)

    def test_mover_posicion_pelota_y(self):
        juego.pelota.y = 100
        juego.vel_pelota_y = -5
        juego.mover_posicion_pelota()

        self.assertEqual(juego.pelota.y, 95)

    def test_rebote_pelota_y(self):
        juego.vel_pelota_y = 5
        juego.rebotar_pelota_y()

        self.assertEqual(juego.vel_pelota_y, -5)

    def test_rebote_pelota_x(self):
        juego.vel_pelota_x = 5
        juego.rebotar_pelota_x()

        self.assertEqual(juego.vel_pelota_x, -5)

    def test_pelota_toca_borde_superior(self):
        juego.pelota.top = 0

        self.assertTrue(juego.pelota_toca_borde_superior())

    def test_pelota_toca_borde_inferior(self):
        juego.pelota.bottom = juego.ALTO

        self.assertTrue(juego.pelota_toca_borde_inferior())

    def test_sumar_punto_jugador1(self):
        juego.score1 = 0
        juego.sumar_punto_jugador1()

        self.assertEqual(juego.score1, 1)
        self.assertEqual(juego.pelota.x, juego.ANCHO // 2)
        self.assertEqual(juego.pelota.y, juego.ALTO // 2)

    def test_sumar_punto_jugador2(self):
        juego.score2 = 0
        juego.sumar_punto_jugador2()

        self.assertEqual(juego.score2, 1)
        self.assertEqual(juego.pelota.x, juego.ANCHO // 2)
        self.assertEqual(juego.pelota.y, juego.ALTO // 2)

    def test_jugador1_gano(self):
        juego.score1 = juego.PUNTOS_GANAR

        self.assertTrue(juego.jugador1_gano())

    def test_jugador2_gano(self):
        juego.score2 = juego.PUNTOS_GANAR

        self.assertTrue(juego.jugador2_gano())

    def test_declarar_ganador_jugador1(self):
        juego.declarar_ganador_jugador1()

        self.assertTrue(juego.game_over)
        self.assertEqual(juego.ganador, "Jugador 1 gana")
        self.assertEqual(juego.color_ganador, juego.ROJO)

    def test_declarar_ganador_jugador2(self):
        juego.declarar_ganador_jugador2()

        self.assertTrue(juego.game_over)
        self.assertEqual(juego.ganador, "Jugador 2 gana")
        self.assertEqual(juego.color_ganador, juego.AZUL)

    def test_actualizar_juego_no_mueve_si_esta_pausado(self):
        juego.pausado = True
        juego.pelota.x = 100
        juego.pelota.y = 100
        juego.actualizar_juego()

        self.assertEqual(juego.pelota.x, 100)
        self.assertEqual(juego.pelota.y, 100)

    def test_obtener_velocidad_aleatoria_regresa_5_o_menos_5(self):
        velocidad = juego.obtener_velocidad_aleatoria()

        self.assertIn(velocidad, [5, -5])

    def test_centrar_jugadores(self):
        juego.jugador1.y = 10
        juego.jugador2.y = 20

        juego.centrar_jugadores()

        esperado = juego.ALTO // 2 - juego.JUGADOR_ALTO // 2
        self.assertEqual(juego.jugador1.y, esperado)
        self.assertEqual(juego.jugador2.y, esperado)

    def test_centrar_pelota(self):
        juego.pelota.x = 50
        juego.pelota.y = 80

        juego.centrar_pelota()

        self.assertEqual(juego.pelota.x, juego.ANCHO // 2)
        self.assertEqual(juego.pelota.y, juego.ALTO // 2)

    def test_reiniciar_estado_juego(self):
        juego.game_over = True
        juego.pausado = True
        juego.ganador = "Jugador 1 gana"
        juego.color_ganador = juego.ROJO

        juego.reiniciar_estado_juego()

        self.assertFalse(juego.game_over)
        self.assertFalse(juego.pausado)
        self.assertEqual(juego.ganador, "")
        self.assertEqual(juego.color_ganador, juego.BLANCO)

    def test_reiniciar_juego_restablece_valores_principales(self):
        juego.score1 = 4
        juego.score2 = 3
        juego.game_over = True
        juego.pausado = True
        juego.ganador = "Jugador 2 gana"
        juego.jugador1.y = 0
        juego.jugador2.y = 0
        juego.pelota.x = 10
        juego.pelota.y = 10

        juego.reiniciar_juego()

        self.assertEqual(juego.score1, 0)
        self.assertEqual(juego.score2, 0)
        self.assertFalse(juego.game_over)
        self.assertFalse(juego.pausado)
        self.assertEqual(juego.ganador, "")
        self.assertEqual(juego.jugador1.y, juego.obtener_posicion_centro_jugador())
        self.assertEqual(juego.jugador2.y, juego.obtener_posicion_centro_jugador())
        self.assertEqual(juego.pelota.x, juego.ANCHO // 2)
        self.assertEqual(juego.pelota.y, juego.ALTO // 2)

    def test_reiniciar_velocidad_pelota(self):
        with patch.object(juego, "obtener_velocidad_aleatoria", side_effect=[5, -5]):
            juego.reiniciar_velocidad_pelota()

        self.assertEqual(juego.vel_pelota_x, 5)
        self.assertEqual(juego.vel_pelota_y, -5)

    def test_reiniciar_pelota_centra_la_pelota(self):
        juego.pelota.x = 123
        juego.pelota.y = 456

        with patch.object(juego, "reiniciar_velocidad_pelota"):
            juego.reiniciar_pelota()

        self.assertEqual(juego.pelota.x, juego.ANCHO // 2)
        self.assertEqual(juego.pelota.y, juego.ALTO // 2)

    def test_pelota_no_toca_borde_superior(self):
        juego.pelota.top = 10

        self.assertFalse(juego.pelota_toca_borde_superior())

    def test_pelota_no_toca_borde_inferior(self):
        juego.pelota.bottom = juego.ALTO - 10

        self.assertFalse(juego.pelota_toca_borde_inferior())

    def test_pelota_toca_borde_vertical_superior(self):
        juego.pelota.top = 0

        self.assertTrue(juego.pelota_toca_borde_vertical())

    def test_pelota_toca_borde_vertical_inferior(self):
        juego.pelota.bottom = juego.ALTO

        self.assertTrue(juego.pelota_toca_borde_vertical())

    def test_pelota_no_toca_borde_vertical(self):
        juego.pelota.y = 200

        self.assertFalse(juego.pelota_toca_borde_vertical())

    def test_verificar_rebote_pared_invierte_velocidad_y(self):
        juego.pelota.top = 0
        juego.vel_pelota_y = 5

        juego.verificar_rebote_pared()

        self.assertEqual(juego.vel_pelota_y, -5)

    def test_verificar_rebote_pared_no_invierte_si_no_toca_borde(self):
        juego.pelota.y = 200
        juego.vel_pelota_y = 5

        juego.verificar_rebote_pared()

        self.assertEqual(juego.vel_pelota_y, 5)

    def test_pelota_choca_jugador1(self):
        juego.pelota.center = juego.jugador1.center
        juego.vel_pelota_x = 5

        self.assertTrue(juego.pelota_choca_jugador1())

    def test_pelota_no_choca_jugador1_si_va_hacia_izquierda(self):
        juego.pelota.center = juego.jugador1.center
        juego.vel_pelota_x = -5

        self.assertFalse(juego.pelota_choca_jugador1())

    def test_pelota_choca_jugador2(self):
        juego.pelota.center = juego.jugador2.center
        juego.vel_pelota_x = -5

        self.assertTrue(juego.pelota_choca_jugador2())

    def test_pelota_no_choca_jugador2_si_va_hacia_derecha(self):
        juego.pelota.center = juego.jugador2.center
        juego.vel_pelota_x = 5

        self.assertFalse(juego.pelota_choca_jugador2())

    def test_verificar_colision_jugador1_invierte_x(self):
        juego.pelota.center = juego.jugador1.center
        juego.vel_pelota_x = 5

        juego.verificar_colision_jugadores()

        self.assertEqual(juego.vel_pelota_x, -5)

    def test_verificar_colision_jugador2_invierte_x(self):
        juego.pelota.center = juego.jugador2.center
        juego.vel_pelota_x = -5

        juego.verificar_colision_jugadores()

        self.assertEqual(juego.vel_pelota_x, 5)

    def test_verificar_colision_sin_choque_no_cambia_velocidad(self):
        juego.pelota.x = juego.ANCHO // 2
        juego.pelota.y = juego.ALTO // 2
        juego.vel_pelota_x = 5

        juego.verificar_colision_jugadores()

        self.assertEqual(juego.vel_pelota_x, 5)

    def test_pelota_sale_por_izquierda(self):
        juego.pelota.left = 0

        self.assertTrue(juego.pelota_sale_por_izquierda())

    def test_pelota_no_sale_por_izquierda(self):
        juego.pelota.left = 100

        self.assertFalse(juego.pelota_sale_por_izquierda())

    def test_pelota_sale_por_derecha(self):
        juego.pelota.right = juego.ANCHO

        self.assertTrue(juego.pelota_sale_por_derecha())

    def test_pelota_no_sale_por_derecha(self):
        juego.pelota.right = juego.ANCHO - 100

        self.assertFalse(juego.pelota_sale_por_derecha())

    def test_verificar_punto_por_izquierda_suma_a_jugador1(self):
        juego.score1 = 0
        juego.pelota.left = -1

        juego.verificar_punto()

        self.assertEqual(juego.score1, 1)

    def test_verificar_punto_por_derecha_suma_a_jugador2(self):
        juego.score2 = 0
        juego.pelota.right = juego.ANCHO + 1

        juego.verificar_punto()

        self.assertEqual(juego.score2, 1)

    def test_verificar_punto_no_suma_si_pelota_sigue_en_cancha(self):
        juego.score1 = 0
        juego.score2 = 0
        juego.pelota.x = juego.ANCHO // 2
        juego.pelota.y = juego.ALTO // 2

        juego.verificar_punto()

        self.assertEqual(juego.score1, 0)
        self.assertEqual(juego.score2, 0)

    def test_verificar_ganador_jugador1(self):
        juego.score1 = juego.PUNTOS_GANAR
        juego.score2 = 0

        juego.verificar_ganador()

        self.assertTrue(juego.game_over)
        self.assertEqual(juego.ganador, "Jugador 1 gana")

    def test_verificar_ganador_jugador2(self):
        juego.score1 = 0
        juego.score2 = juego.PUNTOS_GANAR

        juego.verificar_ganador()

        self.assertTrue(juego.game_over)
        self.assertEqual(juego.ganador, "Jugador 2 gana")

    def test_actualizar_juego_no_mueve_si_game_over(self):
        juego.game_over = True
        juego.pausado = False
        juego.pelota.x = 100
        juego.pelota.y = 100

        juego.actualizar_juego()

        self.assertEqual(juego.pelota.x, 100)
        self.assertEqual(juego.pelota.y, 100)

    def test_actualizar_juego_mueve_pelota_si_esta_activo(self):
        juego.game_over = False
        juego.pausado = False
        juego.pelota.x = 300
        juego.pelota.y = 300
        juego.vel_pelota_x = 5
        juego.vel_pelota_y = 5

        juego.actualizar_juego()

        self.assertEqual(juego.pelota.x, 305)
        self.assertEqual(juego.pelota.y, 305)

    def test_manejar_evento_teclado_p_alterna_pausa(self):
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)

        juego.manejar_evento_teclado(evento)

        self.assertTrue(juego.pausado)

    def test_manejar_evento_teclado_r_reinicia_juego(self):
        juego.score1 = 3
        juego.score2 = 2
        juego.pausado = True
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)

        juego.manejar_evento_teclado(evento)

        self.assertEqual(juego.score1, 0)
        self.assertEqual(juego.score2, 0)
        self.assertFalse(juego.pausado)

    def test_manejar_evento_teclado_otra_tecla_no_cambia_pausa(self):
        juego.pausado = False
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)

        juego.manejar_evento_teclado(evento)

        self.assertFalse(juego.pausado)

    def test_manejar_evento_no_teclado_no_cambia_pausa(self):
        juego.pausado = False
        evento = pygame.event.Event(pygame.USEREVENT)

        juego.manejar_evento_teclado(evento)

        self.assertFalse(juego.pausado)

    def test_mover_jugadores_con_tecla_up_mueve_jugador1_arriba(self):
        posicion_inicial = juego.jugador1.y

        with patch("pygame.key.get_pressed", return_value=TeclasFake({pygame.K_UP})):
            juego.mover_jugadores()

        self.assertEqual(juego.jugador1.y, posicion_inicial - juego.VEL_JUGADOR)

    def test_mover_jugadores_con_tecla_down_mueve_jugador1_abajo(self):
        posicion_inicial = juego.jugador1.y

        with patch("pygame.key.get_pressed", return_value=TeclasFake({pygame.K_DOWN})):
            juego.mover_jugadores()

        self.assertEqual(juego.jugador1.y, posicion_inicial + juego.VEL_JUGADOR)

    def test_mover_jugadores_con_tecla_w_mueve_jugador2_arriba(self):
        posicion_inicial = juego.jugador2.y

        with patch("pygame.key.get_pressed", return_value=TeclasFake({pygame.K_w})):
            juego.mover_jugadores()

        self.assertEqual(juego.jugador2.y, posicion_inicial - juego.VEL_JUGADOR)

    def test_mover_jugadores_con_tecla_s_mueve_jugador2_abajo(self):
        posicion_inicial = juego.jugador2.y

        with patch("pygame.key.get_pressed", return_value=TeclasFake({pygame.K_s})):
            juego.mover_jugadores()

        self.assertEqual(juego.jugador2.y, posicion_inicial + juego.VEL_JUGADOR)

    def test_obtener_estado_juego_regresa_datos_actuales(self):
        juego.score1 = 2
        juego.score2 = 1
        juego.pausado = True
        juego.ganador = "Prueba"
        juego.pelota.x = 150
        juego.pelota.y = 250

        estado = juego.obtener_estado_juego()

        self.assertEqual(estado["score1"], 2)
        self.assertEqual(estado["score2"], 1)
        self.assertTrue(estado["pausado"])
        self.assertEqual(estado["ganador"], "Prueba")
        self.assertEqual(estado["pelota_x"], 150)
        self.assertEqual(estado["pelota_y"], 250)

    def test_guardar_estado_test_sin_archivo_no_falla(self):
        juego.ESTADO_TEST_FILE = None

        juego.guardar_estado_test()

    def test_guardar_estado_test_crea_json(self):
        archivo_temporal = tempfile.NamedTemporaryFile(delete=False)
        ruta = archivo_temporal.name
        archivo_temporal.close()

        try:
            juego.ESTADO_TEST_FILE = ruta
            juego.score1 = 4
            juego.score2 = 2
            juego.pausado = True

            juego.guardar_estado_test()

            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            self.assertEqual(datos["score1"], 4)
            self.assertEqual(datos["score2"], 2)
            self.assertTrue(datos["pausado"])

        finally:
            juego.ESTADO_TEST_FILE = None
            os.remove(ruta)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
