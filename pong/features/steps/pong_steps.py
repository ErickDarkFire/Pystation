"""
Pruebas de sistema del juego Pong usando BDD con Behave y PyDirectInput.
"""

import atexit
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pydirectinput
from behave import given, then, when

PROCESOS_ABIERTOS = []


def esperar_archivo_estado(ruta, timeout=8):
    """
    Espera a que se cree el archivo JSON donde el juego guarda su estado actual.
    """
    inicio = time.time()

    while time.time() - inicio < timeout:
        if ruta.exists():
            return True

        time.sleep(0.1)

    return False


def enfocar_ventana_pong():
    """
    Busca y activa la ventana del juego para que reciba las teclas simuladas.
    """
    try:
        import pygetwindow as gw

        ventanas = gw.getWindowsWithTitle("Pong")

        if ventanas:
            ventanas[0].activate()
            time.sleep(0.5)
    except Exception:
        pass


def cerrar_proceso(proceso):
    """
    Cierra la ventana del juego.
    """
    if proceso and proceso.poll() is None:
        proceso.terminate()

        try:
            proceso.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proceso.kill()


def cerrar_todos_los_procesos():
    """
    Cierra todos los procesos del juego que se abrieron durante las pruebas.
    """
    for proceso in PROCESOS_ABIERTOS:
        cerrar_proceso(proceso)


atexit.register(cerrar_todos_los_procesos)


def leer_estado(context):
    """
    Lee el archivo JSON del estado del juego y lo convierte en diccionario.
    """
    for _ in range(10):
        try:
            with open(context.archivo_estado, "r", encoding="utf-8") as archivo:
                contenido = archivo.read().strip()

                if not contenido:
                    time.sleep(0.05)
                    continue

                return json.loads(contenido)

        except json.JSONDecodeError:
            time.sleep(0.05)

        except FileNotFoundError:
            time.sleep(0.05)

    raise AssertionError("No se pudo leer el estado del juego correctamente.")


def esperar_condicion(context, condicion, timeout=4):
    """
    Espera hasta que una condición del estado del juego se cumpla.
    """
    inicio = time.time()

    while time.time() - inicio < timeout:
        estado = leer_estado(context)

        if condicion(estado):
            return estado

        time.sleep(0.1)

    raise AssertionError("La condición esperada no se cumplió.")


def obtener_posicion_jugador(estado, jugador):
    """
    Obtiene la posición vertical del jugador indicado.
    """
    if jugador == "jugador1":
        return estado["jugador1_y"]

    if jugador == "jugador2":
        return estado["jugador2_y"]

    raise ValueError(f"Jugador no válido: {jugador}")


def validar_movimiento_vertical(posicion_anterior, posicion_actual, direccion):
    """
    Valida si un jugador se movió hacia arriba o hacia abajo.
    """
    if direccion == "arriba":
        assert posicion_actual < posicion_anterior
        return

    if direccion == "abajo":
        assert posicion_actual > posicion_anterior
        return

    raise ValueError(f"Dirección no válida: {direccion}")


@given("que abro el juego Pong")
def step_abrir_juego(context):
    """
    Ejecuta el juego Pong como un proceso independiente.
    """
    raiz = Path(__file__).resolve().parents[2]
    archivo_juego = raiz / "pong.py"

    context.archivo_estado = (
        Path(tempfile.gettempdir()) / f"pong_estado_{os.getpid()}_{time.time_ns()}.json"
    )

    env = os.environ.copy()
    env["PONG_STATE_FILE"] = str(context.archivo_estado)
    env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    context.proceso = subprocess.Popen(
        [sys.executable, str(archivo_juego)], cwd=raiz, env=env
    )

    PROCESOS_ABIERTOS.append(context.proceso)

    if hasattr(context, "add_cleanup"):
        context.add_cleanup(cerrar_proceso, context.proceso)

    if not esperar_archivo_estado(context.archivo_estado):
        cerrar_proceso(context.proceso)
        raise AssertionError("El juego abrió, pero no generó el archivo de estado.")

    enfocar_ventana_pong()

    assert context.proceso.poll() is None


@when('presiono la tecla "{tecla}"')
def step_presionar_tecla(context, tecla):
    """
    Presiona una tecla dentro de la ventana del juego.
    """
    enfocar_ventana_pong()
    pydirectinput.press(tecla)
    time.sleep(0.4)


@when('mantengo presionada la tecla "{tecla}" por {segundos:f} segundos')
def step_mantener_tecla(context, tecla, segundos):
    """
    Mantiene presionada una tecla durante cierta cantidad de segundos.
    """
    enfocar_ventana_pong()

    context.estado_anterior = leer_estado(context)

    pydirectinput.keyDown(tecla)
    time.sleep(segundos)
    pydirectinput.keyUp(tecla)

    time.sleep(0.4)


@then("el juego debe quedar pausado")
def step_juego_pausado(context):
    """
    Verifica que el juego quede pausado.
    """
    esperar_condicion(context, lambda estado: estado["pausado"] is True)


@then("el juego debe continuar")
def step_juego_continua(context):
    """
    Verifica que el juego no esté pausado.
    """
    esperar_condicion(context, lambda estado: estado["pausado"] is False)


@then("el marcador debe estar en 0 para ambos jugadores")
def step_marcador_cero(context):
    """
    Verifica que ambos marcadores estén en cero.
    """
    estado = leer_estado(context)

    assert estado["score1"] == 0
    assert estado["score2"] == 0


@then('el "{jugador}" debe moverse hacia "{direccion}"')
def step_jugador_debe_moverse(context, jugador, direccion):
    """
    Verifica que el jugador indicado se haya movido hacia la dirección esperada.
    """
    estado_actual = leer_estado(context)

    posicion_anterior = obtener_posicion_jugador(context.estado_anterior, jugador)
    posicion_actual = obtener_posicion_jugador(estado_actual, jugador)

    validar_movimiento_vertical(posicion_anterior, posicion_actual, direccion)
