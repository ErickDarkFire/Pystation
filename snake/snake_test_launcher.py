"""Lanzador del juego Snake Deluxe para pruebas de sistema BDD.

Inicia el juego con ventana real (headless=False) e integra un servidor de
control por socket que permite a los hooks de behave forzar posiciones
deterministas y disparar movimientos individuales sin ceder el control
al timer interno del juego.

Comandos disponibles:
    OK                          — Ping de verificación
    GET_SCORE                   — Puntaje actual (int)
    GET_LENGTH                  — Longitud actual de la serpiente (int)
    GET_SCREEN                  — Nombre del Screen activo (string)
    GET_FRUIT_POS               — "cx,cy" del centro de la fruta
    PLACE_FRUIT <cx> <cy>       — Reposiciona la fruta
    PLACE_SNAKE <cx> <cy> <dir> — Reposiciona serpiente con dirección activa
    FREEZE                      — Congela move_timer (modo manual)
    UNFREEZE                    — Restaura move_timer normal
    STEP                        — Ejecuta UN solo movimiento manual de la
                                   serpiente sin descongelar el timer.
                                   Procesa colisiones y comer fruta.
    SETUP_EAT <cx> <cy>         — Atómico: serpiente en (cx,cy) RIGHT +
                                   fruta en (cx+TILE,cy) + FREEZE
    SETUP_WALL <cx> <cy> <dir>  — Atómico: serpiente en borde + FREEZE
"""

import os
import sys
import socket
import threading
import time

import pygame  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snake import Game, Screen, Direction, TILE_SIZE  # noqa: E402

CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 15123
READY_SIGNAL = "SNAKE_READY"

DIR_MAP = {
    "UP": Direction.UP,
    "DOWN": Direction.DOWN,
    "LEFT": Direction.LEFT,
    "RIGHT": Direction.RIGHT,
}


def _handle_control_connection(conn, game):
    """Procesa comandos de texto recibidos por el socket de control del juego.

    Lee líneas terminadas en newline y despacha cada una a _dispatch_command,
    enviando la respuesta de vuelta al cliente del socket.
    """
    with conn:
        data = b""
        while True:
            chunk = conn.recv(512)
            if not chunk:
                break
            data += chunk
            while b"\n" in data:
                line, data = data.split(b"\n", 1)
                command = line.decode("utf-8").strip()
                response = _dispatch_command(command, game)
                conn.sendall((response + "\n").encode("utf-8"))


def _place_snake_with_direction(game, cx, cy, direction):
    """Reposiciona la serpiente y activa la dirección de movimiento atómicamente.

    Mueve todos los segmentos al centro (cx, cy) y fuerza tanto direction
    como next_direction para que el próximo move() avance correctamente
    sin que move() sobreescriba la dirección con next_direction.
    """
    for seg in game.snake.segments:
        seg.center = (cx, cy)
    game.snake.direction = direction
    game.snake.next_direction = direction


def _manual_step(game):
    """Ejecuta UN solo tick de movimiento sin tocar el move_timer.

    Replica la lógica de _update_playing para movimiento, colisión y
    comer fruta, pero sin sumar al timer ni resetearlo a 0. Esto permite
    al test mantener FREEZE activo mientras dispara movimientos manuales.
    """
    if game.screen_id != Screen.PLAYING:
        return "NOT_PLAYING"

    portal = game._is_portal()
    game.snake.move(portal=portal)

    if game.snake.is_dead(portal=portal, obstacle=game.obstacle):
        game.scoreboard.reset()
        game.screen_id = Screen.DEAD
        return "DIED"

    if game.snake.eats_fruit(game.fruit):
        pts = game.fruit.points
        game.snake.grow()
        game.scoreboard.add_points(pts)
        excluded = game.snake.get_segment_centers()
        if game.obstacle:
            excluded += game.obstacle.get_centers()
        game.fruit.reposition(excluded)
        return "ATE"

    return "MOVED"


def _dispatch_command(command, game):
    """Mapea un comando de texto a la acción correspondiente sobre el juego.

    Devuelve la respuesta en texto para enviar de vuelta al cliente del socket.
    Todos los comandos son síncronos en el hilo del servidor de control.
    """
    parts = command.split()
    if not parts:
        return "ERROR empty command"

    cmd = parts[0].upper()

    if cmd == "OK":
        return "OK"

    if cmd == "GET_SCORE":
        return str(game.scoreboard.get_score())

    if cmd == "GET_LENGTH":
        return str(game.snake.length)

    if cmd == "GET_SCREEN":
        return game.screen_id.value

    if cmd == "GET_FRUIT_POS":
        cx, cy = game.fruit.rect.center
        return f"{cx},{cy}"

    if cmd == "FREEZE":
        game._move_timer = -999999
        return "OK"

    if cmd == "UNFREEZE":
        game._move_timer = 0
        return "OK"

    if cmd == "STEP":
        result = _manual_step(game)
        game._move_timer = -999999
        return result

    if cmd == "PLACE_FRUIT" and len(parts) == 3:
        try:
            cx, cy = int(parts[1]), int(parts[2])
            game.fruit.rect.center = (cx, cy)
            return "OK"
        except (ValueError, AttributeError):
            return "ERROR invalid coordinates"

    if cmd == "PLACE_SNAKE" and len(parts) >= 3:
        try:
            cx, cy = int(parts[1]), int(parts[2])
            direction = (
                DIR_MAP.get(parts[3].upper()) if len(parts) >= 4 else Direction.NONE
            )
            _place_snake_with_direction(game, cx, cy, direction or Direction.NONE)
            game._move_timer = -999999
            return "OK"
        except (ValueError, AttributeError, IndexError):
            return "ERROR invalid arguments"

    if cmd == "SETUP_EAT" and len(parts) == 3:
        try:
            cx, cy = int(parts[1]), int(parts[2])
            game._move_timer = -999999
            _place_snake_with_direction(game, cx, cy, Direction.RIGHT)
            fruit_cx = cx + TILE_SIZE
            fruit_cy = cy
            game.fruit.rect.center = (fruit_cx, fruit_cy)
            return f"FRUIT_AT {fruit_cx},{fruit_cy}"
        except (ValueError, AttributeError):
            return "ERROR invalid coordinates"

    if cmd == "SETUP_WALL" and len(parts) >= 4:
        try:
            cx, cy = int(parts[1]), int(parts[2])
            direction = DIR_MAP.get(parts[3].upper())
            if direction is None:
                return "ERROR unknown direction"
            game._move_timer = -999999
            _place_snake_with_direction(game, cx, cy, direction)
            return "OK"
        except (ValueError, AttributeError):
            return "ERROR invalid arguments"

    return f"ERROR unknown command: {cmd}"


def _run_control_server(game):
    """Ejecuta el servidor de control TCP en un hilo daemon de fondo.

    Acepta conexiones en CONTROL_HOST:CONTROL_PORT y despacha cada una
    a _handle_control_connection en un hilo separado.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((CONTROL_HOST, CONTROL_PORT))
    server.listen(8)
    server.settimeout(1.0)

    while True:
        try:
            conn, _ = server.accept()
            t = threading.Thread(
                target=_handle_control_connection,
                args=(conn, game),
                daemon=True,
            )
            t.start()
        except socket.timeout:
            continue
        except OSError:
            break


if __name__ == "__main__":
    game = Game(headless=False)

    server_thread = threading.Thread(
        target=_run_control_server,
        args=(game,),
        daemon=True,
    )
    server_thread.start()

    time.sleep(0.1)
    sys.stdout.write(READY_SIGNAL + "\n")
    sys.stdout.flush()

    game.run()
