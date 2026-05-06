import pygame
import sys
import subprocess
import os

# Inicialización
pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyStation OS - Matrix Menu")

# Colores y Estilo
BLACK = (15, 15, 15)
WHITE = (240, 240, 240)
GOLD = (255, 215, 0)
GRAY = (50, 50, 50)

# Fuentes
font_name = pygame.font.SysFont("Segoe UI", 28, bold=True)
font_title = pygame.font.SysFont("Segoe UI", 45, bold=True)

# Configuración de la Matriz
COLUMNAS = 3
FILAS = 2
MARGIN_X = 60
MARGIN_Y = 150
SPACING_X = 280
SPACING_Y = 250
LOGO_SIZE = (180, 180)

# Lista de juegos (según carpetas en image_67622c.png)
nombres_juegos = ["blackjack", "craps", "poker", "snake", "Tic_tac_toe", "pong"]
juegos_data = []

def cargar_recursos():
    """Carga nombres e imágenes dinámicamente."""
    data = []
    for nombre in nombres_juegos:
        # Ruta: juego/img/logo.png
        ruta_logo = os.path.join(nombre, "img", "logo.png")
        
        if os.path.exists(ruta_logo):
            img = pygame.image.load(ruta_logo).convert_alpha()
            img = pygame.transform.smoothscale(img, LOGO_SIZE)
        else:
            # Placeholder si no hay logo
            img = pygame.Surface(LOGO_SIZE)
            img.fill(GRAY)
            
        data.append({"nombre": nombre, "logo": img, "rect": None})
    return data

juegos_data = cargar_recursos()
seleccionado = 0

def lanzar_juego(nombre_carpeta):
    """Ejecuta el script principal del juego."""
    # Busca cualquier .py en la raíz de la carpeta del juego
    archivos = [f for f in os.listdir(nombre_carpeta) if f == f"{nombre_carpeta}.py"]
    if archivos:
        archivo_py = os.path.join(nombre_carpeta, archivos[0])
        try:
            subprocess.run([sys.executable, archivo_py])
            pygame.display.set_mode((WIDTH, HEIGHT)) # Re-enfocar menú al volver
        except Exception as e:
            print(f"Error al lanzar {nombre_carpeta}: {e}")

def dibujar_menu():
    screen.fill(BLACK)
    
    # Título Principal
    titulo = font_title.render("PYSTATION", True, WHITE)
    screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 30))

    for i, juego in enumerate(juegos_data):
        col = i % COLUMNAS
        fila = i // COLUMNAS
        
        x = MARGIN_X + col * SPACING_X
        y = MARGIN_Y + fila * SPACING_Y
        
        # Crear un rect para detección de mouse
        area_rect = pygame.Rect(x, y, LOGO_SIZE[0], LOGO_SIZE[1] + 40)
        juegos_data[i]["rect"] = area_rect
        
        # Efecto de selección (Visual)
        es_hover = (i == seleccionado)
        color_texto = GOLD if es_hover else WHITE
        
        if es_hover:
            # Brillo detrás del logo
            pygame.draw.rect(screen, (40, 40, 40), area_rect.inflate(10, 10), border_radius=10)

        # Dibujar Nombre (Arriba)
        txt = font_name.render(juego["nombre"].replace("_", " ").title(), True, color_texto)
        screen.blit(txt, (x + LOGO_SIZE[0]//2 - txt.get_width()//2, y - 40))
        
        # Dibujar Logo (Debajo)
        screen.blit(juego["logo"], (x, y))

    pygame.display.flip()

# Bucle Principal
while True:
    dibujar_menu()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Selección con Mouse (Hover)
        if event.type == pygame.MOUSEMOTION:
            for i, juego in enumerate(juegos_data):
                if juego["rect"] and juego["rect"].collidepoint(mouse_pos):
                    seleccionado = i

        # Click para lanzar
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Click izquierdo
                lanzar_juego(juegos_data[seleccionado]["nombre"])

        # Selección con Teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                seleccionado = (seleccionado + 1) % len(juegos_data)
            elif event.key == pygame.K_LEFT:
                seleccionado = (seleccionado - 1) % len(juegos_data)
            elif event.key == pygame.K_DOWN:
                if seleccionado + COLUMNAS < len(juegos_data):
                    seleccionado += COLUMNAS
            elif event.key == pygame.K_UP:
                if seleccionado - COLUMNAS >= 0:
                    seleccionado -= COLUMNAS
            elif event.key == pygame.K_RETURN:
                lanzar_juego(juegos_data[seleccionado]["nombre"])