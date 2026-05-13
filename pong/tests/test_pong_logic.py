import os

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

    @classmethod
    def tearDownClass(cls):
        pygame.quit()


if __name__ == "__main__":
    unittest.main()
