"""Hooks de entorno para las pruebas de sistema BDD de Snake Deluxe.

Gestiona el ciclo de vida completo de cada escenario:
    - Lanza el juego como proceso real con ventana visible (headless=False)
    - Conecta al servidor de control por socket para posicionamiento determinista
    - Enfoca la ventana antes de enviar inputs de teclado
    - Termina el proceso limpiamente al finalizar cada escenario

El servidor de control corre dentro del proceso del juego (snake_test_launcher.py)
y expone comandos como PLACE_FRUIT, PLACE_SNAKE, GET_SCORE y GET_LENGTH.
"""

import os
import sys
import socket
import subprocess
import time

try:
    import pydirectinput
except AttributeError as exc:
    raise RuntimeError(
        "Ejecuta las pruebas en un entorno Windows con display real."
    ) from exc


LAUNCHER_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "snake_test_launcher.py"
)

CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 15123

GAME_STARTUP_WAIT = 3.5
WINDOW_FOCUS_WAIT = 0.6
SOCKET_CONNECT_TIMEOUT = 8.0
SOCKET_RECV_TIMEOUT = 3.0
BETWEEN_SCENARIOS_WAIT = 0.8

READY_SIGNAL = "SNAKE_READY"


def _launch_game(context):
    """Lanza el proceso de Snake Deluxe usando el launcher de pruebas.

    Elimina variables de entorno de SDL que fuerzan modo headless para garantizar
    que se abra una ventana real y visible de Pygame.
    """
    launcher = os.path.abspath(LAUNCHER_SCRIPT)
    game_dir = os.path.dirname(launcher)
    env = os.environ.copy()
    env.pop("SDL_VIDEODRIVER", None)
    env.pop("SDL_AUDIODRIVER", None)

    context.game_process = subprocess.Popen(
        [sys.executable, launcher],
        cwd=game_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _wait_for_ready_signal(context):
    """Bloquea hasta que el proceso del juego emite la señal SNAKE_READY en stdout.

    El launcher escribe esta señal cuando el servidor de control ya está
    escuchando y el juego está a punto de entrar al loop principal.
    """
    deadline = time.time() + SOCKET_CONNECT_TIMEOUT
    while time.time() < deadline:
        if context.game_process.poll() is not None:
            raise RuntimeError("El proceso del juego terminó antes de emitir READY")
        line = context.game_process.stdout.readline()
        if line and READY_SIGNAL in line:
            return
        time.sleep(0.1)
    raise RuntimeError(
        f"El juego no emitió '{READY_SIGNAL}' en {SOCKET_CONNECT_TIMEOUT}s"
    )


def _connect_control_socket(context):
    """Establece la conexión TCP con el servidor de control del juego.

    Reintenta la conexión durante SOCKET_CONNECT_TIMEOUT segundos para dar
    tiempo al proceso recién lanzado de inicializar el socket.
    """
    deadline = time.time() + SOCKET_CONNECT_TIMEOUT
    last_error = None
    while time.time() < deadline:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_RECV_TIMEOUT)
            sock.connect((CONTROL_HOST, CONTROL_PORT))
            context.control_socket = sock
            return
        except (ConnectionRefusedError, OSError) as err:
            last_error = err
            time.sleep(0.2)
    raise RuntimeError(
        f"No se pudo conectar al socket de control en {SOCKET_CONNECT_TIMEOUT}s: {last_error}"
    )


def send_command(context, command):
    """Envía un comando de texto al servidor de control y retorna la respuesta.

    El protocolo es una línea de texto terminada en newline.
    Lanza RuntimeError si la respuesta indica un error o hay timeout.
    """
    sock = context.control_socket
    sock.sendall((command + "\n").encode("utf-8"))
    response = ""
    while "\n" not in response:
        chunk = sock.recv(256).decode("utf-8")
        if not chunk:
            raise RuntimeError("Socket de control cerrado inesperadamente")
        response += chunk
    result = response.split("\n")[0].strip()
    if result.startswith("ERROR"):
        raise RuntimeError(f"Comando '{command}' falló: {result}")
    return result


def _focus_game_window():
    """Enfoca la ventana del juego usando herramientas del sistema operativo.

    Intenta en orden: pygetwindow (Windows), xdotool (Linux), wmctrl (Linux).
    Como fallback hace click en el centro estimado de la ventana.
    """
    title = "Snake Deluxe v2.0"

    try:
        import pygetwindow as gw

        wins = gw.getWindowsWithTitle(title)
        if wins:
            wins[0].activate()
            time.sleep(WINDOW_FOCUS_WAIT)
            return
    except (ImportError, Exception):
        pass

    try:
        result = subprocess.run(
            ["xdotool", "search", "--name", title, "windowactivate", "--sync"],
            capture_output=True,
            timeout=3,
        )
        if result.returncode == 0:
            time.sleep(WINDOW_FOCUS_WAIT)
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ["wmctrl", "-a", title],
            capture_output=True,
            timeout=3,
        )
        if result.returncode == 0:
            time.sleep(WINDOW_FOCUS_WAIT)
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    pydirectinput.moveTo(400, 400)
    time.sleep(0.15)
    pydirectinput.click()
    time.sleep(WINDOW_FOCUS_WAIT)


def _close_game(context):
    """Termina el proceso del juego y cierra el socket de control.

    Usa terminate() con espera de 5 segundos antes de forzar kill().
    """
    if hasattr(context, "control_socket") and context.control_socket:
        try:
            context.control_socket.close()
        except OSError:
            pass
        context.control_socket = None

    if context.game_process and context.game_process.poll() is None:
        context.game_process.terminate()
        try:
            context.game_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            context.game_process.kill()
    context.game_process = None


def before_all(context):
    """Configura parámetros globales de la suite antes de cualquier escenario.

    Establece la pausa automática de pydirectinput para que cada keystroke
    tenga un delay mínimo que evita saturar el event queue de Pygame.
    """
    pydirectinput.PAUSE = 0.08
    context.game_process = None
    context.control_socket = None


def after_all(context):
    """Garantiza que no queden procesos del juego colgados al terminar la suite."""
    _close_game(context)


def before_scenario(context, scenario):
    """Inicia el juego, conecta el socket de control y enfoca la ventana.

    Secuencia de arranque:
        1. Lanza snake_test_launcher.py como subprocess
        2. Espera la señal SNAKE_READY en stdout
        3. Conecta al servidor de control TCP
        4. Deja que Pygame termine de renderizar el primer frame
        5. Enfoca la ventana para que pydirectinput llegue a Pygame
    """
    _launch_game(context)
    _wait_for_ready_signal(context)
    _connect_control_socket(context)
    time.sleep(GAME_STARTUP_WAIT)
    _focus_game_window()

    context.initial_score = None
    context.initial_length = None
    context.initial_fruit_pos = None
    context.game_started = False


def after_scenario(context, scenario):
    """Cierra el juego y espera entre escenarios para evitar conflictos de puerto."""
    _close_game(context)
    time.sleep(BETWEEN_SCENARIOS_WAIT)
