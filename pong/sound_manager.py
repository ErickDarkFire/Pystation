import pygame
import os


class Sonidos:
    def __init__(self):
        self.habilitado = True

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            self.habilitado = False

        self.sonido_rebote = self.cargar_sonido("pong/sound/rebote.ogg")
        self.sonido_punto = self.cargar_sonido("pong/sound/punto.wav")
        self.sonido_ganador = self.cargar_sonido("pong/sound/ganador.wav")

    def cargar_sonido(self, ruta):
        if not self.habilitado:
            return None

        if not os.path.exists(ruta):
            return None

        try:
            return pygame.mixer.Sound(ruta)
        except Exception:
            return None

    def reproducir(self, sonido):
        if sonido is not None:
            sonido.play()

    def reproducir_rebote(self):
        self.reproducir(self.sonido_rebote)

    def reproducir_punto(self):
        self.reproducir(self.sonido_punto)

    def reproducir_ganador(self):
        self.reproducir(self.sonido_ganador)
