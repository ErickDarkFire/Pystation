import pygame
import sys
import random
from sound_manager import Sonidos

pygame.init()

# Ventana
ANCHO = 800
ALTO = 600
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)

JUGADOR_ANCHO = 20
JUGADOR_ALTO = 120
VEL_JUGADOR = 7

PELOTA_SIZE = 30
PUNTOS_GANAR = 5

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pong")

fuente = pygame.font.SysFont("Arial", 40)
fuente_ganador = pygame.font.SysFont("Arial", 50)
fuente_pausa = pygame.font.SysFont("Arial", 45)

clock = pygame.time.Clock()
sonidos = Sonidos()

jugador1 = pygame.Rect(
    700,
    ALTO // 2 - JUGADOR_ALTO // 2,
    JUGADOR_ANCHO,
    JUGADOR_ALTO
)

jugador2 = pygame.Rect(
    40,
    ALTO // 2 - JUGADOR_ALTO // 2,
    JUGADOR_ANCHO,
    JUGADOR_ALTO
)

pelota = pygame.Rect(
    ANCHO // 2,
    ALTO // 2,
    PELOTA_SIZE,
    PELOTA_SIZE
)

vel_pelota_x = random.choice([5, -5])
vel_pelota_y = random.choice([5, -5])

score1 = 0
score2 = 0

game_over = False
pausado = False

ganador = ""
color_ganador = BLANCO


def obtener_posicion_centro_jugador():
    return ALTO // 2 - JUGADOR_ALTO // 2


def obtener_velocidad_aleatoria():
    return random.choice([5, -5])


def centrar_jugadores():
    jugador1.y = obtener_posicion_centro_jugador()
    jugador2.y = obtener_posicion_centro_jugador()


def centrar_pelota():
    pelota.x = ANCHO // 2
    pelota.y = ALTO // 2


def reiniciar_velocidad_pelota():
    global vel_pelota_x, vel_pelota_y

    vel_pelota_x = obtener_velocidad_aleatoria()
    vel_pelota_y = obtener_velocidad_aleatoria()


def reiniciar_pelota():
    centrar_pelota()
    reiniciar_velocidad_pelota()


def reiniciar_marcador():
    global score1, score2

    score1 = 0
    score2 = 0


def reiniciar_estado_juego():
    global game_over, pausado, ganador, color_ganador

    game_over = False
    pausado = False
    ganador = ""
    color_ganador = BLANCO


def reiniciar_juego():
    reiniciar_marcador()
    reiniciar_estado_juego()
    centrar_jugadores()
    reiniciar_pelota()


def alternar_pausa():
    global pausado

    if not game_over:
        pausado = not pausado


def mover_jugador_arriba(jugador):
    if jugador.y > 0:
        jugador.y -= VEL_JUGADOR


def mover_jugador_abajo(jugador):
    if jugador.y < ALTO - JUGADOR_ALTO:
        jugador.y += VEL_JUGADOR


def mover_jugadores():
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_UP]:
        mover_jugador_arriba(jugador1)

    if teclas[pygame.K_DOWN]:
        mover_jugador_abajo(jugador1)

    if teclas[pygame.K_w]:
        mover_jugador_arriba(jugador2)

    if teclas[pygame.K_s]:
        mover_jugador_abajo(jugador2)


def mover_posicion_pelota():
    pelota.x += vel_pelota_x
    pelota.y += vel_pelota_y


def pelota_toca_borde_superior():
    return pelota.top <= 0


def pelota_toca_borde_inferior():
    return pelota.bottom >= ALTO


def pelota_toca_borde_vertical():
    return pelota_toca_borde_superior() or pelota_toca_borde_inferior()


def rebotar_pelota_y():
    global vel_pelota_y

    vel_pelota_y *= -1
    sonidos.reproducir_rebote()


def rebotar_pelota_x():
    global vel_pelota_x

    vel_pelota_x *= -1
    sonidos.reproducir_rebote()


def verificar_rebote_pared():
    if pelota_toca_borde_vertical():
        rebotar_pelota_y()


def pelota_choca_jugador1():
    return pelota.colliderect(jugador1) and vel_pelota_x > 0


def pelota_choca_jugador2():
    return pelota.colliderect(jugador2) and vel_pelota_x < 0


def verificar_colision_jugadores():
    if pelota_choca_jugador1():
        rebotar_pelota_x()

    if pelota_choca_jugador2():
        rebotar_pelota_x()


def pelota_sale_por_izquierda():
    return pelota.left <= 0


def pelota_sale_por_derecha():
    return pelota.right >= ANCHO


def sumar_punto_jugador1():
    global score1

    score1 += 1
    sonidos.reproducir_punto()
    reiniciar_pelota()


def sumar_punto_jugador2():
    global score2

    score2 += 1
    sonidos.reproducir_punto()
    reiniciar_pelota()


def verificar_punto():
    if pelota_sale_por_izquierda():
        sumar_punto_jugador1()

    if pelota_sale_por_derecha():
        sumar_punto_jugador2()


def jugador1_gano():
    return score1 >= PUNTOS_GANAR


def jugador2_gano():
    return score2 >= PUNTOS_GANAR


def declarar_ganador_jugador1():
    global game_over, ganador, color_ganador

    game_over = True
    ganador = "Jugador 1 gana"
    color_ganador = ROJO
    sonidos.reproducir_ganador()


def declarar_ganador_jugador2():
    global game_over, ganador, color_ganador

    game_over = True
    ganador = "Jugador 2 gana"
    color_ganador = AZUL
    sonidos.reproducir_ganador()


def verificar_ganador():
    if jugador1_gano():
        declarar_ganador_jugador1()

    if jugador2_gano():
        declarar_ganador_jugador2()


def mover_pelota():
    mover_posicion_pelota()
    verificar_rebote_pared()
    verificar_colision_jugadores()
    verificar_punto()
    verificar_ganador()


def dibujar_cancha():
    ventana.fill(NEGRO)
    pygame.draw.line(
        ventana,
        BLANCO,
        (ANCHO // 2, 0),
        (ANCHO // 2, ALTO),
        3
    )


def dibujar_jugadores():
    pygame.draw.rect(ventana, ROJO, jugador1)
    pygame.draw.rect(ventana, AZUL, jugador2)


def dibujar_pelota():
    pygame.draw.rect(ventana, BLANCO, pelota)


def dibujar_marcador():
    texto1 = fuente.render(str(score1), True, BLANCO)
    texto2 = fuente.render(str(score2), True, BLANCO)

    ventana.blit(texto1, (ANCHO // 2 + 50, 20))
    ventana.blit(texto2, (ANCHO // 2 - 80, 20))


def dibujar_game_over():
    texto_ganador = fuente_ganador.render(ganador, True, color_ganador)
    texto_reinicio = fuente.render("Presiona R para reiniciar", True, BLANCO)

    ventana.blit(
        texto_ganador,
        (ANCHO // 2 - texto_ganador.get_width() // 2, ALTO // 2 - 50)
    )

    ventana.blit(
        texto_reinicio,
        (ANCHO // 2 - texto_reinicio.get_width() // 2, ALTO // 2 + 20)
    )


def dibujar_pausa():
    texto_pausa = fuente_pausa.render("PAUSA", True, BLANCO)
    texto_continuar = fuente.render("Presiona P para continuar", True, BLANCO)

    ventana.blit(
        texto_pausa,
        (ANCHO // 2 - texto_pausa.get_width() // 2, ALTO // 2 - 50)
    )

    ventana.blit(
        texto_continuar,
        (ANCHO // 2 - texto_continuar.get_width() // 2, ALTO // 2 + 20)
    )


def dibujar():
    dibujar_cancha()
    dibujar_jugadores()
    dibujar_pelota()
    dibujar_marcador()

    if game_over:
        dibujar_game_over()

    if pausado:
        dibujar_pausa()

    pygame.display.update()


def manejar_evento_salir(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


def manejar_evento_teclado(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            reiniciar_juego()

        if event.key == pygame.K_p:
            alternar_pausa()


def manejar_eventos():
    for event in pygame.event.get():
        manejar_evento_salir(event)
        manejar_evento_teclado(event)


def actualizar_juego():
    if not game_over and not pausado:
        mover_jugadores()
        mover_pelota()


def ejecutar_juego():
    while True:
        manejar_eventos()
        actualizar_juego()
        dibujar()
        clock.tick(60)


if __name__ == "__main__":
    ejecutar_juego()
    