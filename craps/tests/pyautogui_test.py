import subprocess
import pyautogui
import time
import os
import sys


def probar_juego():
    try:
        # 1. Obtener la ruta de la carpeta raíz
        dir_tests = os.path.dirname(os.path.abspath(__file__))
        raiz_proyecto = os.path.abspath(os.path.join(dir_tests, ".."))

        # 2. Apuntar al archivo exacto del juego
        ruta_juego = os.path.join(raiz_proyecto, "craps.py")

        print("Iniciando el juego...")
        # 3. Ejecutar subproceso
        subprocess.Popen([sys.executable, ruta_juego], cwd=raiz_proyecto)

        # Esperamos a que cargue la ventana
        time.sleep(2.5)

        # 4. Automatización
        print("Pulsando Flecha Arriba 14 veces...")
        for _ in range(14):
            pyautogui.press("up")
            time.sleep(0.1)

        print("Pulsando Espacio 40 veces...")
        for _ in range(40):
            pyautogui.press("space")
            time.sleep(0.5)

        print("Pulsando Esc para salir del juego")
        time.sleep(3)
        pyautogui.press("esc")

        print("Prueba completada con éxito.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    probar_juego()
