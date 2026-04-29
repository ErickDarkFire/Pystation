import pygame
import random
import os


class CrapsGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Craps")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 26, bold=True)

        self.saldo = 500
        self.apuesta = 10
        self.punto = None
        self.ganadas = 0
        self.perdidas = 0
        self.mensaje = "Usa FLECHAS p/ Apostar | Usa ESPACIO p/ Tirar"

        self.dice_images = self.cargar_recursos()
        self.dados_actuales = [0, 0]
        self.mostrar_dados = False
        self.jugando = True

    def cargar_recursos(self):
        imagenes = []
        for i in range(1, 7):
            path = os.path.join("craps", "imagenes_craps", f"cube_{i}.jpg")
            img = pygame.image.load(path).convert_alpha()
            imagenes.append(pygame.transform.scale(img, (100, 100)))
        return imagenes

    def animar_dados(self):
        for _ in range(15):
            self.dados_actuales = [random.randint(0, 5), random.randint(0, 5)]
            self.dibujar()
            pygame.time.delay(40)

    def procesar_tiro(self):
        if self.saldo < self.apuesta:
            self.saldo += 500
            self.mensaje = "¡Bancarrota! Recargaste $500."
            return
        self.mostrar_dados = True
        self.animar_dados()
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        self.dados_actuales = [d1 - 1, d2 - 1]
        resultado = d1 + d2

        if self.punto is None:
            if resultado in (7, 11):
                self.mensaje = f"¡Natural! {resultado}. Ganaste ${self.apuesta}"
                self.ganadas += 1
                self.saldo += self.apuesta
            elif resultado in (2, 3, 12):
                self.mensaje = f"Craps {resultado}. Perdiste ${self.apuesta}"
                self.perdidas += 1
                self.saldo -= self.apuesta
            else:
                self.punto = resultado
                self.mensaje = f"Punto: {self.punto}. ¡Tira de nuevo!"
        else:
            if resultado == self.punto:
                self.mensaje = f"¡Lograste el {self.punto}! Ganaste ${self.apuesta}"
                self.ganadas += 1
                self.saldo += self.apuesta
                self.punto = None
            elif resultado == 7:
                self.mensaje = f"Siete fuera. Perdiste ${self.apuesta}"
                self.perdidas += 1
                self.saldo -= self.apuesta
                self.punto = None
            else:
                self.mensaje = f"Salió {resultado}. Buscas el {self.punto}."

    def dibujar(self):
        self.screen.fill((0, 100, 0))

        txt_m = self.font.render(self.mensaje, True, (255, 215, 0))
        self.screen.blit(txt_m, (self.WIDTH // 2 - txt_m.get_width() // 2, 450))

        txt_ap = self.font.render(f"Apuesta: ${self.apuesta}", True, (255, 255, 0))
        self.screen.blit(txt_ap, (self.WIDTH // 2 - txt_ap.get_width() // 2, 500))

        txt_s = self.font.render(f"Saldo: ${self.saldo}", True, (100, 255, 100))
        self.screen.blit(txt_s, (self.WIDTH - 180, 20))

        txt_st = self.font.render(
            f"G: {self.ganadas} | P: {self.perdidas}", True, (255, 255, 255)
        )
        self.screen.blit(txt_st, (20, 20))

        if self.mostrar_dados:
            self.screen.blit(
                self.dice_images[self.dados_actuales[0]], (self.WIDTH // 2 - 110, 200)
            )
            self.screen.blit(
                self.dice_images[self.dados_actuales[1]], (self.WIDTH // 2 + 10, 200)
            )

        pygame.display.flip()

    def run(self):
        while self.jugando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.jugando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.jugando = False
                    if self.punto is None:
                        if event.key == pygame.K_UP and self.saldo >= self.apuesta + 10:
                            self.apuesta += 10
                        if event.key == pygame.K_DOWN and self.apuesta > 10:
                            self.apuesta -= 10
                    if event.key == pygame.K_SPACE:
                        self.procesar_tiro()
            self.dibujar()
            self.clock.tick(60)
        pygame.quit()
