"""Cliente del socket de control para las pruebas de sistema de Snake Deluxe.

Provee la función send_command que los steps y los hooks de environment
usan para comunicarse con el servidor de control que corre dentro del
proceso del juego (snake_test_launcher.py).

Este módulo es independiente de la jerarquía de paquetes de behave para
poder importarse tanto desde features/environment.py como desde
features/steps/system_steps.py sin errores de ModuleNotFoundError.
"""

import socket  # noqa: F401

SOCKET_RECV_TIMEOUT = 3.0


def send_command(context, command):
    """Envía un comando de texto al servidor de control y retorna la respuesta.

    Lee del socket hasta encontrar un newline, luego devuelve la primera línea
    de la respuesta sin espacios. Lanza RuntimeError si la respuesta comienza
    con ERROR o si el socket se cierra inesperadamente.
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
