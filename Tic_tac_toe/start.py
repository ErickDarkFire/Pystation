import pygame, sys, random, os

pygame.init()

# Colores
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLACK = (0,0,0)
GREY = (150,150,150)
PURPLE = (255,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)
ORANGE = (255,165,0)
PINK = (255,192,203)
BROWN = (165,42,42)
DARK_GREEN = (0,100,0)
NAVY = (0,0,128)
GOLD = (255,215,0)
SILVER = (192,192,192)

colores = [
    WHITE,
    BLUE,
    GREEN,
    RED,
    BLACK,
    GREY,
    PURPLE,
    YELLOW,
    CYAN,
    ORANGE,
    PINK,
    BROWN,
    DARK_GREEN,
    NAVY,
    GOLD,
    SILVER
]

#Medidas de la ventana
alto = 500
ancho = 800
size = (ancho, alto)

#Visibilidad del mouse
pygame.mouse.set_visible(False)

#Obtener tamaño de cuadricula
ancho_grid = ancho/3
alto_grid = alto/3

#crear ventana
screen = pygame.display.set_mode(size)

#Cargar imagen del logo
logo = pygame.image.load(os.path.join('Tic_tac_toe','img','logo_gato.png')).convert()

#Quitar fondo negro a la imagen
logo.set_colorkey(BLACK)

#Establecer el icono de la ventana
pygame.display.set_icon(logo)

#Título de la ventana
pygame.display.set_caption("PyStation - Tic-tac-toe")

#Reloj para controlar los FPS
clock = pygame.time.Clock()

#lista de coordenadas
coord_list = []
#Obtenemos nuestra lista de coordenadas para animar el fondo
for i in range(60):
    x = random.randint(0,ancho)
    y = random.randint(0,alto)
    coord_list.append([x,y])

#velocidad del fondo en x
vel_x_lluvia = 0.2

#Tamaño de las formas para rellenar la cuadricula
fig_size = 70

#Dimensiones cuadrada del icono del cursor
dim_icon = 40

#Tamaño del ancho de las lineas del circulo del jugador 2
circle_width = 15

#Centros para dibujar circulos dependiendo la posicion del mouse
#Centros en X
col1_centro = ancho_grid/2
col2_centro = (ancho_grid + ancho_grid*2)/2
col3_centro = (ancho_grid*2 + ancho)/2
#Centro en Y
fila1_centro = alto_grid/2
fila2_centro = (alto_grid + alto_grid*2)/2
fila3_centro = (alto_grid*2 + alto)/2

centers_list = [
    [(col1_centro,fila1_centro), (col2_centro,fila1_centro), (col3_centro,fila1_centro)],
    [(col1_centro,fila2_centro), (col2_centro,fila2_centro), (col3_centro,fila2_centro)],
    [(col1_centro,fila3_centro), (col2_centro,fila3_centro), (col3_centro,fila3_centro)],
]

#Puntos donde deben de iniciar las lineas para formar una X
#Linea 1, empieza en -x -y y termina en +x +y
(col1_centro-fig_size,fila1_centro-fig_size),(col1_centro+fig_size,fila1_centro+fig_size)
#Linea 2, empieza en -x +y y termina en +x -y
(col1_centro-fig_size,fila1_centro+fig_size),(col1_centro+fig_size,fila1_centro-fig_size)

#Generamos los puntos donde deben de iniciar las lineas para formar una X usando los centros
#lista de puntos para formar la cruz:
#p1 siendo los puntos de arriba-izquierda
p1_list = []
#p2 siendo los puntos de abajo-derecha
p2_list = []
#p3 siendo los puntos de arriba-derecha
p3_list = []
#p4 siendo los puntos de abajo-izquierda
p4_list = []

#contador para manejar el formato de matriz
k = 0
#Listas que nos van a ayudar a hacer el formato de matriz
l1 = []
l2 = []
l3 = []
l4 = []

#Color de fondo animado por default
color_selec = RED

for array in centers_list:
    for centros in array:
        ajuste = fig_size/1.15
        #Linea 1, empieza en -x -y(p1) y termina en +x +y (p2)
        p1 = (centros[0]-ajuste, centros[1]-ajuste)
        p2 = (centros[0]+ajuste , centros[1]+ajuste)
        #Linea 2, empieza en -x +y y termina en +x -y
        p3 = (centros[0]-ajuste , centros[1]+ajuste)
        p4 = (centros[0]+ajuste , centros[1]-ajuste)
        #Siempre agregamos a la lista auxiliares hasta que se completen 3 coordenadas
        l1.append(p1)
        l2.append(p2)
        l3.append(p3)
        l4.append(p4)
        # Si ya hay 3 puntos agregados en la lista, la metemos a la matriz
        if k == 2:
            #Agregamos a la matriz
            p1_list.append(l1.copy())
            p2_list.append(l2.copy())
            p3_list.append(l3.copy())
            p4_list.append(l4.copy())
            #limpiamos las listas para respetar el formato
            l1.clear()
            l2.clear()
            l3.clear()
            l4.clear()
            #reiniciamos contador
            k = 0
        else:
            k+=1 

"""
Guardando cada posicion nuestra matriz de tuplas nos queda:
p1_list = [
    [(x1,y1), (x1,y1), (x1,y1)],
    [(x1,y1), (x1,y1), (x1,y1)],
    [(x1,y1), (x1,y1), (x1,y1)]
]

Para acceder a la informacion solo se ocupan 3 indicadores, i e j para el cuadrante donde esta el cursor
y K para indicar si es X o Y de esa coordenada:
p1[i][j][k]
Ejemplo:
p1[0][2][1] -> Nos referimos a cual es la coordenada y del cuadro que esta arriba a la derecha, en su punto 1 
(El inicio de la diagonal que va de izquierda a derecha de arriba a abajo \)

"""

#Representacion del tablero en matriz
tablero = [
    ["","",""],
    ["","",""],
    ["","",""]
]

#--------------Variables que si cambian durante el juego --------------------------------------
#Bandera de control de turnos
turno = 0

#Elemento a dibujar en la matriz
fig = "X"

#bandera que indica si se hizo clic o no
clic = False

#Bandera que controla el fin del juego
win = False

#Contador para que el efecto de fondo haga el pandeo
pandeo_cont = 0
#--------------Variables que si cambian durante el juego --------------------------------------

# Musica del juego
pygame.mixer.init()
pygame.mixer.music.load(os.path.join('Tic_tac_toe','musica','background.mp3'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)

sonido_escribir = pygame.mixer.Sound(os.path.join('Tic_tac_toe','musica','write.wav'))

#Imagen a usar para el fondo
fondo = pygame.image.load(os.path.join('Tic_tac_toe','img','gato_bg2.jpg')).convert()

#Iconos de los cursores de cada jugador
p1_cursor = pygame.image.load(os.path.join('Tic_tac_toe','img','p1_cursor.png')).convert()
p2_cursor = pygame.image.load(os.path.join('Tic_tac_toe','img','p2_cursor.png')).convert()


def Check():
    Ganador = ""
    if tablero[0][0] == tablero[0][1] and tablero[0][1] == tablero[0][2] and tablero[0][2] != "":
        Ganador = tablero[0][0]
    elif tablero[0][0] == tablero[1][0] and tablero[1][0] == tablero[2][0] and tablero[2][0] != "":
        Ganador = tablero[0][0]
    elif tablero[0][0] == tablero[1][1] and tablero[1][1] == tablero[2][2] and tablero[2][2] != "":
        Ganador = tablero[0][0]
    elif tablero[0][1] == tablero[1][1] and tablero[1][1] == tablero[2][1] and tablero[2][1] != "":
        Ganador = tablero[0][1]
    elif tablero[0][2] == tablero[1][2] and tablero[1][2] == tablero[2][2] and tablero[2][2] != "":
        Ganador = tablero[0][2]
    elif tablero[2][0] == tablero[1][1] and tablero[1][1] == tablero[0][2] and tablero[0][2] != "":
        Ganador = tablero[2][0]
    elif tablero[1][0] == tablero[1][1] and tablero[1][1] == tablero[1][2] and tablero[1][2] != "":
        Ganador = tablero[1][0]
    elif tablero[2][0] == tablero[2][1] and tablero[2][1] == tablero[2][2] and tablero[2][2] != "":
        Ganador = tablero[2][0]
    
    if Ganador != "":
        return True
    else:
        return False

#Funcion que dibuja como va el juego
def Draw_game():
    for i in range(3):
        for j in range(3):
            if tablero[i][j] == "X":
                pygame.draw.line(screen,RED,p1_list[i][j],p2_list[i][j],fig_size//3)
                pygame.draw.line(screen,RED,p3_list[i][j],p4_list[i][j],fig_size//3)

            elif tablero[i][j] == "O":
                pygame.draw.circle(screen,BLUE,centers_list[i][j],fig_size,circle_width)

def Hover(x_mouse,y_mouse):
    #Donde se va a dibujar cada elemento
    current_x = 0
    current_y = 0
    #Primera columna
    if x_mouse < ancho_grid:
        current_y = 0
        #Primera fila [0][0]
        if y_mouse < alto_grid:
            current_x = 0
        #Segunda fila [1][0]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid:
            current_x = 1
        #Tercera fila [2][0]
        elif y_mouse > (alto_grid*2):
            current_x = 2
    
    #segunda columna
    elif x_mouse < (ancho_grid*2) and x_mouse > ancho_grid:
        current_y = 1
        #Primera fila [0][1]
        if y_mouse < alto_grid:
            current_x = 0
        #Segunda fila [1][1]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid:
            current_x = 1
        #Tercera fila [2][1]
        elif y_mouse > (alto_grid*2):
            current_x = 2
    
    #Tercera columna
    elif x_mouse > (ancho_grid*2) and x_mouse > ancho_grid:
        current_y = 2
        #Primera fila [0][2]
        if y_mouse < alto_grid:
            current_x = 0
        #Segunda fila [1][2]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid:
            current_x = 1
        #Tercera fila [2][2]
        elif y_mouse > (alto_grid*2):
            current_x = 2
    
    if tablero[current_x][current_y] == "":
        if turno == 0:
            pygame.draw.line(screen,RED,p1_list[current_x][current_y],p2_list[current_x][current_y],fig_size//3)
            pygame.draw.line(screen,RED,p3_list[current_x][current_y],p4_list[current_x][current_y],fig_size//3)
        else:
            pygame.draw.circle(screen,BLUE,centers_list[current_x][current_y],fig_size,circle_width)
    
    return current_x,current_y

def Reinicio():
    for i in range(3):
        for j in range(3):
            tablero[i][j] = ""
    #Variables que si cambian durante el juego las reiniciamos
    #Bandera de control de turnos turno = 0
    #Elemento a dibujar en la matriz fig = "X"
    #bandera que indica si se hizo clic o no clic = False
    #Bandera que controla el fin del juego win = False
    #Contador para que el efecto de fondo haga el pandeo pandeo_cont = 0
    #Color de fondo animado
    return 0,"X", False, False, 0, Escoger_color()
    
def Escoger_color():
    #Obtenemos un numero random para asignarle el color al fondo
    cs = random.randint(0,len(colores)-1)
    return colores[cs]    

#Usamos la funcion para obtener un color de fondo random en cada partida
color_selec = Escoger_color()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONUP:
            print("click")
            clic = True

        if event.type == pygame.KEYDOWN:
                #Con tecla space se reinicia el juego
                if event.key == pygame.K_SPACE:
                    print("Reiniciando Juego")
                    #Reinicio del juego
                    turno,fig,clic,win,pandeo_cont,color_selec =Reinicio()

    #Obtener posicion/coordenadas del mouse
    mouse_pos = pygame.mouse.get_pos()
    x_mouse = mouse_pos[0]
    y_mouse = mouse_pos[1]
    
    #Color de fondo
    #screen.fill(WHITE)

    #Usar imagen de fondo
    bg = pygame.transform.scale(fondo,(ancho,alto))
    screen.blit(bg,(0,0))

    #Cambiar imgen del cursor dependiendo quien juegue
    if turno == 0:
        player_img = pygame.transform.scale(p1_cursor,(dim_icon,dim_icon))
    elif turno == 1:
        player_img = pygame.transform.scale(p2_cursor,(dim_icon,dim_icon))
    #Color a ignorar en el cursor
    player_img.set_colorkey(WHITE)    

    if pandeo_cont > 50:
        pandeo_cont = 0
        vel_x_lluvia =  vel_x_lluvia * (-1)
    pandeo_cont+=1

    ### ----- ZONA DE DIBUJO
    Draw_game()

    #Fondo animado
    for coord in coord_list:
        pygame.draw.circle(screen,color_selec,coord,4)
        coord[1] +=1
        coord[0] += vel_x_lluvia
        
        if coord[1] > alto:
            coord[1] = 0

    #Dibujar cuadricula (grid) del juego
    for i in range(1,3):
        pygame.draw.line(screen,BLACK,(ancho_grid*i,0),(ancho_grid*i,alto),5)
        pygame.draw.line(screen,BLACK,(0,alto_grid*i),(ancho,alto_grid*i),5)

    coord_tablero = Hover(x_mouse,y_mouse)
    if clic == True:
        print(tablero[coord_tablero[0]][coord_tablero[1]])
        clic = False
        if tablero[coord_tablero[0]][coord_tablero[1]] == "":
            #Despues de escoger, cambian los turnos
            if turno == 0:
                fig = "X"
                turno = 1
            elif turno == 1:
                fig = "O"
                turno = 0
            tablero[coord_tablero[0]][coord_tablero[1]] = fig
            print(tablero)
            sonido_escribir.play()
        else:
            print("ERROR, Lugar ocupado")

    #Usar imagen en cursor, les restamos ajus para que quede centrado (Lo ultimo que pintamos para que quede encimado)
    ajus = dim_icon/2
    screen.blit(player_img,(x_mouse-ajus,y_mouse-ajus))

    ### ----- ZONA DE DIBUJO

    #Revisamos quien gano
    win = Check()
    if win == True:
        if turno == 1:
            print("El ganador es: Player 1!!")
        elif turno == 0:
            print("El ganador es: Player 2!!")
        break    

    #actualizar pantalla (refrescar)
    pygame.display.flip()
    clock.tick(60)

#Salimos del programa
pygame.quit()