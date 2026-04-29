import pygame
import sys
import random

pygame.init()

# Ventana
ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pong")
fuente = pygame.font.SysFont("Arial", 40)
fuente_ganador = pygame.font.SysFont("Arial", 50)
clock = pygame.time.Clock()
# Jugadoress
jugador_ancho = 20
jugador_alto = 120

jugador1 = pygame.Rect(700, ALTO // 2 - jugador_alto // 2, jugador_ancho, jugador_alto)
jugador2 = pygame.Rect(40, ALTO // 2 - jugador_alto // 2, jugador_ancho, jugador_alto)
vel_jugador = 7

# Pelota
pelota_size = 30
pelota = pygame.Rect(ANCHO // 2, ALTO // 2, pelota_size, pelota_size)
vel_pelota_x = random.choice([5, -5])
vel_pelota_y = random.choice([5, -5])

# Marcador
score1 = 0
score2 = 0

game_over = False
ganador = ""
colorGanador = BLANCO


def reiniciar_pelota():
    global vel_pelota_x, vel_pelota_y
    pelota.x = ANCHO // 2
    pelota.y = ALTO // 2
    vel_pelota_x = random.choice([5, -5])
    vel_pelota_y = random.choice([5, -5])


def reiniciar_juego():
    global score1, score2, game_over, ganador
    score1 = 0
    score2 = 0
    game_over = False
    ganador = ""

    jugador1.y = ALTO // 2 - jugador_alto // 2
    jugador2.y = ALTO // 2 - jugador_alto // 2
    reiniciar_pelota()


def mover_jugadores():
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_UP] and jugador1.y > 0:
        jugador1.y -= vel_jugador
    if teclas[pygame.K_DOWN] and jugador1.y < ALTO - jugador_alto:
        jugador1.y += vel_jugador
    if teclas[pygame.K_w] and jugador2.y > 0:
        jugador2.y -= vel_jugador
    if teclas[pygame.K_s] and jugador2.y < ALTO - jugador_alto:
        jugador2.y += vel_jugador


def mover_pelota():
    global vel_pelota_x, vel_pelota_y, score1, score2, game_over, ganador, colorGanador
    pelota.x += vel_pelota_x
    pelota.y += vel_pelota_y

    if pelota.top <= 0 or pelota.bottom >= ALTO:
        vel_pelota_y *= -1
    if pelota.colliderect(jugador1) and vel_pelota_x > 0:
        vel_pelota_x *= -1
    if pelota.colliderect(jugador2) and vel_pelota_x < 0:
        vel_pelota_x *= -1
    if pelota.left <= 0:
        score1 += 1
        reiniciar_pelota()
    if pelota.right >= ANCHO:
        score2 += 1
        reiniciar_pelota()
    if score1 == 5:
        game_over = True
        ganador = "Jugador 1 gana"
        colorGanador = ROJO
    if score2 == 5:
        game_over = True
        ganador = "Jugador 2 gana"
        colorGanador = AZUL


def dibujar():
    ventana.fill(NEGRO)
    pygame.draw.line(ventana, BLANCO, (ANCHO // 2, 0), (ANCHO // 2, ALTO), 3)
    pygame.draw.rect(ventana, ROJO, jugador1)
    pygame.draw.rect(ventana, AZUL, jugador2)
    pygame.draw.rect(ventana, BLANCO, pelota)

    texto1 = fuente.render(str(score1), True, BLANCO)
    texto2 = fuente.render(str(score2), True, BLANCO)
    ventana.blit(texto1, (ANCHO // 2 + 50, 20))
    ventana.blit(texto2, (ANCHO // 2 - 80, 20))

    if game_over:
        texto_ganador = fuente_ganador.render(ganador, True, colorGanador)
        texto_reinicio = fuente.render("Presiona tecla R para reiniciar", True, BLANCO)
        ventana.blit(
            texto_ganador, (ANCHO // 2 - texto_ganador.get_width() // 2, ALTO // 2 - 50)
        )
        ventana.blit(
            texto_reinicio,
            (ANCHO // 2 - texto_reinicio.get_width() // 2, ALTO // 2 + 20),
        )
    pygame.display.update()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reiniciar_juego()

    if not game_over:
        mover_jugadores()
        mover_pelota()

    dibujar()
    clock.tick(60)
