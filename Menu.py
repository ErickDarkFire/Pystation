import pygame
import sys
import subprocess
import os

# Inicialización de Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyStation Launcher")

# Configuración de estética
WHITE = (240, 240, 240)
BLACK = (18, 18, 18)
HIGHLIGHT = (255, 204, 0) # Un tono dorado/amarillo
font = pygame.font.SysFont("Consolas", 35, bold=True)

# Lista de carpetas de juegos (según tu captura image_67622c.png)
# Asegúrate de que el nombre coincida exactamente con la carpeta
juegos = ["blackjack", "craps", "poker", "snake", "Tic_tac_toe"]
seleccionado = 0

def lanzar_juego(nombre_carpeta):
    """Lanza el archivo .py dentro de la carpeta como un proceso nuevo."""
    # Buscamos el archivo .py principal dentro de la carpeta. 
    # Si tus archivos se llaman distinto (ej: snake.py dentro de /snake), 
    # podrías ajustar esto para que busque cualquier .py
    archivo_py = os.path.join(nombre_carpeta, f"{nombre_carpeta}.py")
    
    # Si el nombre del archivo no coincide con la carpeta, 
    # podrías intentar buscar el primer .py que encuentres en esa carpeta.
    if not os.path.exists(archivo_py):
        # Intento alternativo: buscar cualquier archivo .py en la carpeta
        archivos = [f for f in os.listdir(nombre_carpeta) if f.endswith('.py')]
        if archivos:
            archivo_py = os.path.join(nombre_carpeta, archivos[0])

    try:
        print(f"Lanzando: {archivo_py}...")
        # Ejecuta el script de Python y espera a que termine
        subprocess.run([sys.executable, archivo_py])
    except Exception as e:
        print(f"No se pudo ejecutar el juego: {e}")

def dibujar_interfaz():
    screen.fill(BLACK)
    
    # Dibujar título
    titulo_txt = font.render("PYSTATION SELECTOR", True, WHITE)
    screen.blit(titulo_txt, (WIDTH//2 - titulo_txt.get_width()//2, 50))
    
    # Dibujar opciones
    for i, juego in enumerate(juegos):
        es_el_seleccionado = (i == seleccionado)
        color = HIGHLIGHT if es_el_seleccionado else WHITE
        prefijo = "> " if es_el_seleccionado else "  "
        
        texto = font.render(f"{prefijo}{juego.replace('_', ' ').upper()}", True, color)
        rect = texto.get_rect(center=(WIDTH // 2, 180 + i * 60))
        screen.blit(texto, rect)

    pygame.display.flip()

# Bucle principal
running = True
while running:
    dibujar_interfaz()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                seleccionado = (seleccionado - 1) % len(juegos)
            elif event.key == pygame.K_DOWN:
                seleccionado = (seleccionado + 1) % len(juegos)
            elif event.key == pygame.K_RETURN:
                # Ocultamos la ventana del menú momentáneamente (opcional)
                pygame.display.iconify() 
                lanzar_juego(juegos[seleccionado])
                # Al cerrar el juego, restauramos la ventana
                screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.quit()
sys.exit()