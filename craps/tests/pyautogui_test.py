import subprocess
import pyautogui
import time
import os
import sys
import pygame

def probar_juego():
    try:
        # 1. Obtener la ruta de la carpeta raíz ('craps') subiendo un nivel desde 'tests/'
        dir_tests = os.path.dirname(os.path.abspath(__file__))
        raiz_proyecto = os.path.abspath(os.path.join(dir_tests, ".."))
        
        # 2. Apuntar al archivo exacto del juego (craps.py o craps_game.py según tu estructura)
        ruta_juego = os.path.join(raiz_proyecto, 'craps.py')

        print("Iniciando el juego...")
        # 3. 'sys.executable' detecta automáticamente el comando correcto de Python de tu sistema
        # 4. 'cwd' asegura que el juego encuentre su carpeta de imágenes internas
        proceso_juego = subprocess.Popen(
            [sys.executable, ruta_juego],
            cwd=raiz_proyecto
        )
        # 2. TIEMPO DE ESPERA CRUCIAL
        # Esperamos 2.5 segundos para que Pygame cargue la ventana y tome el foco
        time.sleep(2.5)

        # 3. Pulsar la flecha hacia ARRIBA 14 veces para apostar $150
        print("Pulsando Flecha Arriba 14 veces...")
        for i in range(14):
            pyautogui.press('up')
            time.sleep(0.1)

        # 4. Pulsar la tecla ESPACIO 10 veces
        print("Pulsando Espacio 40 veces...")
        for i in range(40):
            pyautogui.press('space')
            time.sleep(0.5)

        # 5. Pulsar la tecla ESC para salir del juego
        print("Pulsando Esc para salir del juego")
        time.sleep(3)
        pyautogui.press('esc')

        print("Prueba completada con éxito.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    probar_juego()
