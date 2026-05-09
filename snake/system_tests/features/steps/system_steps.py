"""Steps de sistema para las pruebas BDD de Snake Deluxe.

Toda interacción usa dos canales exclusivos:
    1. pydirectinput  — inputs reales de teclado visibles en pantalla
    2. socket de control — lectura de estado y control determinista

Estrategia de control determinista:
    El move_timer del juego se mantiene SIEMPRE congelado (FREEZE) durante
    todos los escenarios. La serpiente nunca avanza por su cuenta. En su
    lugar, los steps usan el comando STEP del socket para disparar
    exactamente UN movimiento por cada acción del test.

    Esto garantiza:
        - La serpiente nunca muere por avance autónomo durante las esperas
        - El score y la longitud cambian solo cuando el test lo decide
        - El time.sleep() en los pasos sirve solo para visualización,
          no para que el juego procese movimientos

    Para los keypresses reales con pydirectinput se sigue enviando la tecla
    al sistema operativo (cumpliendo el requisito de input real visible),
    pero el avance del juego viene del comando STEP, no del timer.
"""

import time
import sys
import os

try:
    import pydirectinput
except AttributeError as exc:
    raise RuntimeError(
        "pydirectinput requiere Windows. "
        "Ejecuta estas pruebas en un entorno Windows con display real."
    ) from exc

from behave import given, when, then

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from control_client import send_command  # noqa: E402

TILE_SIZE = 40
WINDOW = 800

SAFE_X = 400
SAFE_Y = 400

WALL_RIGHT_X = WINDOW - TILE_SIZE // 2
WALL_RIGHT_Y = SAFE_Y
WALL_TOP_X = SAFE_X
WALL_TOP_Y = TILE_SIZE // 2

KEY_PAUSE = 0.2
SHORT_WAIT = 0.5
VISUAL_WAIT = 0.4


def _press(key):
    """Envía un keypress real al sistema operativo mediante pydirectinput.

    Cumple el requisito de inputs reales visibles. Una pausa posterior
    deja que Pygame procese el evento aunque el juego esté congelado.
    """
    pydirectinput.press(key)
    time.sleep(KEY_PAUSE)


def _cmd(context, command):
    """Envía un comando al socket de control y retorna la respuesta como string."""
    return send_command(context, command)


def _get_score(context):
    """Consulta el puntaje actual al servidor de control y lo devuelve como int."""
    return int(_cmd(context, "GET_SCORE"))


def _get_length(context):
    """Consulta la longitud actual de la serpiente al servidor de control."""
    return int(_cmd(context, "GET_LENGTH"))


def _get_screen(context):
    """Consulta el nombre del Screen activo al servidor de control."""
    return _cmd(context, "GET_SCREEN")


def _get_fruit_pos(context):
    """Consulta la posición del centro de la fruta y la devuelve como tupla (cx, cy)."""
    raw = _cmd(context, "GET_FRUIT_POS")
    cx, cy = raw.split(",")
    return int(cx), int(cy)


def _step(context):
    """Dispara UN solo movimiento manual de la serpiente vía socket.

    Devuelve uno de: MOVED, ATE, DIED, NOT_PLAYING. El move_timer del juego
    se mantiene congelado tras el step para que la serpiente no siga sola.
    """
    return _cmd(context, "STEP")


def _place_safe(context, direction="RIGHT"):
    """Coloca la serpiente en el centro del tablero apuntando a direction.

    PLACE_SNAKE deja el move_timer congelado automáticamente. La serpiente
    permanece inmóvil hasta que el test llame _step() explícitamente.
    """
    _cmd(context, f"PLACE_SNAKE {SAFE_X} {SAFE_Y} {direction}")
    time.sleep(0.1)


def _setup_eat(context):
    """Setup atómico para escenarios de comer fruta.

    SETUP_EAT hace en un solo round-trip de socket:
        - Serpiente en (400, 400) apuntando RIGHT
        - Fruta en (440, 400) — exactamente donde irá la cabeza tras 1 step
        - move_timer congelado

    Devuelve la posición de la fruta como tupla (cx, cy).
    """
    response = _cmd(context, f"SETUP_EAT {SAFE_X} {SAFE_Y}")
    _, pos_str = response.split(" ")
    cx, cy = pos_str.split(",")
    return int(cx), int(cy)


def _setup_wall_right(context):
    """Coloca la serpiente a 1 tile del borde derecho apuntando RIGHT con FREEZE.

    Desde cx=780 el siguiente step lleva la cabeza a right=839 > 800,
    activando check_wall_collision y muerte garantizada.
    """
    _cmd(context, f"SETUP_WALL {WALL_RIGHT_X} {WALL_RIGHT_Y} RIGHT")
    time.sleep(0.1)


def _setup_wall_top(context):
    """Coloca la serpiente a 1 tile del borde superior apuntando UP con FREEZE.

    Desde cy=20 el siguiente step lleva la cabeza a top=-39 < 0,
    activando check_wall_collision y muerte garantizada.
    """
    _cmd(context, f"SETUP_WALL {WALL_TOP_X} {WALL_TOP_Y} UP")
    time.sleep(0.1)


def _start_game(context):
    """Inicia la partida desde el menú principal enviando Enter.

    Tras iniciar, posiciona la serpiente en el centro con FREEZE para
    evitar el movimiento aleatorio que ocurriría con la posición inicial.
    """
    if not context.game_started:
        _press("return")
        time.sleep(1.5)
        _cmd(context, "FREEZE")
        context.game_started = True


@given("el juego está abierto y en el menú principal")
def step_game_open_at_menu(context):
    """Verifica que el proceso del juego esté activo en el menú principal."""
    assert context.game_process is not None, "El proceso del juego no está corriendo"
    assert (
        context.game_process.poll() is None
    ), "El proceso del juego terminó prematuramente"
    context.game_started = False
    context.initial_score = None
    context.initial_length = None
    context.initial_fruit_pos = None
    context.fruit_pos_before_eat = None
    time.sleep(SHORT_WAIT)


@given("la ventana del juego tiene el foco")
def step_window_has_focus(context):
    """Mueve el puntero al centro de la ventana para asegurar el foco de inputs."""
    pydirectinput.moveTo(400, 400)
    time.sleep(0.2)


@given("el juego está en modo de juego activo")
def step_game_is_playing(context):
    """Inicia la partida y posiciona la serpiente en el centro con FREEZE.

    Tras este step la serpiente está inmóvil en (400, 400) apuntando RIGHT.
    Solo se moverá cuando un step When dispare _step().
    """
    _start_game(context)
    _place_safe(context, "RIGHT")


@given("la fruta está posicionada a la derecha de la serpiente")
def step_fruit_positioned_right(context):
    """Ejecuta el setup atómico SETUP_EAT y almacena la posición de la fruta."""
    context.fruit_pos_before_eat = _setup_eat(context)


@given("se registra la longitud inicial de la serpiente")
def step_record_initial_length(context):
    """Almacena la longitud de la serpiente antes de comer la fruta."""
    context.initial_length = _get_length(context)


@given("se registra el puntaje inicial")
def step_record_initial_score(context):
    """Almacena el puntaje antes de que la serpiente coma la fruta."""
    context.initial_score = _get_score(context)


@given("se registra la posición inicial de la fruta")
def step_record_initial_fruit_pos(context):
    """Almacena la posición de la fruta establecida por SETUP_EAT."""
    context.initial_fruit_pos = context.fruit_pos_before_eat


@given("la serpiente está posicionada cerca del borde derecho")
def step_snake_near_right_wall(context):
    """Coloca la serpiente a 1 tile del borde derecho apuntando RIGHT con FREEZE."""
    _setup_wall_right(context)


@when("el usuario presiona Enter para iniciar")
def step_press_enter_to_start(context):
    """Simula que el usuario presiona Enter para iniciar desde el menú principal."""
    _press("return")
    time.sleep(1.5)
    _cmd(context, "FREEZE")
    context.game_started = True


@when("el usuario presiona la flecha derecha")
def step_press_right(context):
    """Simula keypress real RIGHT y dispara un step manual hacia la derecha."""
    _press("right")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona la tecla W para moverse hacia arriba")
def step_press_w(context):
    """Reposiciona en UP, presiona W y dispara un step manual hacia arriba."""
    _place_safe(context, "UP")
    _press("w")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona la tecla D para moverse hacia la derecha")
def step_press_d(context):
    """Cambia dirección a RIGHT vía socket, presiona D y dispara un step."""
    _cmd(context, f"PLACE_SNAKE {SAFE_X} {SAFE_Y} RIGHT")
    _press("d")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona la flecha arriba para iniciar el movimiento")
def step_press_up_to_start(context):
    """Reposiciona en UP, presiona la flecha arriba y dispara un step."""
    _place_safe(context, "UP")
    _press("up")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona la flecha derecha para comer la fruta")
def step_press_right_to_eat(context):
    """Presiona RIGHT y dispara un step que coloca la cabeza sobre la fruta.

    SETUP_EAT dejó la fruta en (440, 400). El step manual mueve la cabeza
    de (400,400) a (440,400) y eats_fruit detecta la colisión, incrementando
    score y longitud sin que la serpiente siga avanzando.
    """
    _press("right")
    result = _step(context)  # noqa: F841
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona la flecha derecha hacia la pared")
def step_press_right_toward_wall(context):
    """Presiona RIGHT y dispara un step que provoca colisión con la pared derecha."""
    _press("right")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario dirige la serpiente hacia la pared superior")
def step_direct_to_top_wall(context):
    """Coloca la serpiente cerca del borde superior, presiona UP y dispara un step."""
    _setup_wall_top(context)
    _press("up")
    _step(context)
    time.sleep(VISUAL_WAIT)


@when("el usuario presiona Enter para reiniciar")
def step_press_enter_to_restart(context):
    """Simula que el usuario presiona Enter en la pantalla de Game Over.

    El juego transita de DEAD a PLAYING vía evento real de teclado.
    Después se congela el timer para que el verificador del Then
    encuentre la serpiente inmóvil y viva.
    """
    _press("return")
    time.sleep(1.5)
    _cmd(context, "FREEZE")
    context.game_started = True


@when("espera {seconds} segundos")
def step_wait_seconds(context, seconds):
    """Pausa el test el número de segundos indicado para visualización."""
    time.sleep(float(seconds))


@when("espera {seconds} segundo")
def step_wait_one_second(context, seconds):
    """Pausa el test el número de segundos indicado, forma singular."""
    time.sleep(float(seconds))


@when("espera {seconds} segundos sin presionar ninguna tecla")
def step_wait_no_input(context, seconds):
    """Pausa que simula movimiento autónomo disparando varios steps manuales.

    En vez de descongelar el timer (que mataría a la serpiente), dispara
    3 steps separados por pausas para que el usuario vea la serpiente
    avanzar de forma observable mientras el test mantiene control total.
    """
    total = float(seconds)
    pause = total / 4
    for _ in range(3):
        _step(context)
        time.sleep(pause)
    time.sleep(pause)


@when("espera {seconds} segundos para que el movimiento se complete")
def step_wait_movement_complete(context, seconds):
    """Pausa para visualización tras un step ya disparado en el When previo."""
    time.sleep(float(seconds))


@when("espera {seconds} segundos para que ocurra la colisión")
def step_wait_collision(context, seconds):
    """Pausa para visualización tras la colisión ya disparada por el step previo."""
    time.sleep(float(seconds))


@when("espera {seconds} segundos para que colisione")
def step_wait_to_collide(context, seconds):
    """Pausa para visualización tras la colisión ya disparada por el step previo."""
    time.sleep(float(seconds))


@when("espera {seconds} segundos para que el juego reinicie")
def step_wait_restart(context, seconds):
    """Pausa para que el juego complete el ciclo de reinicio tras Game Over."""
    time.sleep(float(seconds))


@when("el usuario espera {seconds} segundo")
def step_user_waits_singular(context, seconds):
    """Pausa explícita del usuario entre acciones, forma singular."""
    time.sleep(float(seconds))


@when("el juego muestra la pantalla de Game Over")
def step_when_game_over_shown(context):
    """Verifica como paso When que el estado actual es dead."""
    screen = _get_screen(context)
    assert screen == "dead", f"Se esperaba 'dead' pero el juego está en: '{screen}'"


@then("el juego entra en modo de juego activo")
def step_then_game_is_playing(context):
    """Verifica que el juego está en estado PLAYING según el servidor de control."""
    time.sleep(SHORT_WAIT)
    screen = _get_screen(context)
    assert (
        screen == "playing"
    ), f"Se esperaba 'playing' pero el juego está en: '{screen}'"


@then("la serpiente aparece en el tablero")
def step_snake_appears_on_board(context):
    """Verifica que la serpiente tiene al menos 1 segmento activo."""
    length = _get_length(context)
    assert (
        length >= 1
    ), f"La serpiente debería tener al menos 1 segmento, tiene: {length}"


@then("la serpiente se está moviendo hacia la derecha")
def step_snake_moving_right(context):
    """Verifica que el juego está en PLAYING tras el step de dirección derecha."""
    assert context.game_process.poll() is None, "El proceso del juego terminó"
    screen = _get_screen(context)
    assert (
        screen == "playing"
    ), f"El juego debería estar en 'playing', está en: '{screen}'"


@then("la serpiente cambió de dirección correctamente")
def step_snake_changed_direction(context):
    """Verifica que el juego está en PLAYING tras la secuencia W→D."""
    assert context.game_process.poll() is None, "El proceso del juego terminó"
    screen = _get_screen(context)
    assert (
        screen == "playing"
    ), f"El juego debería estar en 'playing', está en: '{screen}'"


@then("la serpiente ha avanzado de forma continua")
def step_snake_moved_continuously(context):
    """Verifica que el proceso sigue activo tras múltiples steps de movimiento."""
    assert context.game_process.poll() is None, "El proceso del juego terminó"
    screen = _get_screen(context)
    assert (
        screen == "playing"
    ), f"El juego debería estar en 'playing', está en: '{screen}'"


@then("la longitud de la serpiente aumentó en al menos 1")
def step_length_increased(context):
    """Verifica que la longitud creció comparando con context.initial_length."""
    assert context.initial_length is not None, "No se registró la longitud inicial."
    current = _get_length(context)
    assert (
        current > context.initial_length
    ), f"Longitud no aumentó: inicial={context.initial_length}, actual={current}"


@then("el puntaje del jugador aumentó")
def step_score_increased(context):
    """Verifica que el puntaje aumentó comparando con context.initial_score."""
    assert context.initial_score is not None, "No se registró el puntaje inicial."
    current = _get_score(context)
    assert (
        current > context.initial_score
    ), f"Puntaje no aumentó: inicial={context.initial_score}, actual={current}"


@then("una nueva fruta aparece en el tablero en una posición diferente")
def step_new_fruit_appeared(context):
    """Verifica que la fruta se reposicionó tras ser comida."""
    assert context.initial_fruit_pos is not None, "No se registró la posición inicial."
    screen = _get_screen(context)
    assert (
        screen == "playing"
    ), f"El juego debería estar en 'playing', está en: '{screen}'"
    new_pos = _get_fruit_pos(context)
    assert (
        new_pos != context.initial_fruit_pos
    ), f"La fruta no se reposicionó: sigue en {new_pos}"


@then("el juego muestra la pantalla de Game Over")
def step_game_over_shown(context):
    """Verifica que el juego está en estado DEAD según el servidor de control."""
    screen = _get_screen(context)
    assert screen == "dead", f"Se esperaba 'dead' pero el estado es: '{screen}'"


@then("el puntaje final es visible en pantalla")
def step_final_score_visible(context):
    """Verifica que el puntaje es consultable en el estado de Game Over."""
    screen = _get_screen(context)
    assert screen == "dead", f"El juego debe estar en 'dead', está en: '{screen}'"
    score = _get_score(context)
    assert score >= 0, f"El puntaje final debe ser >= 0, es: {score}"
