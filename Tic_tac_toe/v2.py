import pygame, sys, random, os

#Inicializamos pygame
pygame.init()

#Colores
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLACK = (0,0,0)

#Medidas de la ventana
alto = 500
ancho = 800
size = (ancho, alto)

#Obtener tamaño de cuadricula
ancho_grid = ancho/3
alto_grid = alto/3

#crear ventana
screen = pygame.display.set_mode(size)

#lista de coordenadas
coord_list = []
#Obtenemos nuestra lista de coordenadas para animar el fondo
for i in range(60):
    x = random.randint(0,ancho)
    y = random.randint(0,alto)
    coord_list.append([x,y])

#Contador para que el efecto de fondo haga el pandeo
pandeo_cont = 0
#velocidad del fondo en x
vel_x_lluvia = 0.2

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

#Tamaño de las formas para rellenar la cuadricula
fig_size = 70

#Representacion del tablero en matriz
tablero = [
    ["","",""],
    ["","",""],
    ["","",""]
]

#Bandera de control de turnos
turno = 0

#Elemento a dibujar en la matriz
fig = "X"

#bandera que indica si se hizo clic o no
clic = False

#Bandera que controla el fin del juego
win = False

#Variable para controlar el color en cada turno y que funcione en el hover
c = RED

#Dimensiones cuadrada del icono del cursor
dim_icon = 40

#Imagen a usar para el fondo
fondo = pygame.image.load(os.path.join('Tic_tac_toe','img','gato_bg2.jpg')).convert()

#Iconos de los cursores de cada jugador
p1_cursor = pygame.image.load(os.path.join('Tic_tac_toe','img','p1_cursor.png')).convert()
p2_cursor = pygame.image.load(os.path.join('Tic_tac_toe','img','p2_cursor.png')).convert()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = p1_cursor
        #Color a ignorar en el cursor
        self.image.set_colorkey(WHITE)  
        self.rect = self.image.get_rect()
    
    def update(self):
        #Obtener posicion/coordenadas del mouse
        mouse_pos = pygame.mouse.get_pos()
        self.rect.x = mouse_pos[0]
        self.rect.y = mouse_pos[1]

class Game(object):   
    def __init__(self):
        self.p1_score = 0
        self.p2_score = 0
        #Creamos una lista para tener todo lo que vamos a dibujar en pantalla
        self.all_sprite_list = pygame.sprite.Group()

        #Creamos una instancia para controlar el cursor
        self.cursor = Player()

        #Lo agregamos en una lista para dibujar todos los sprites que necesitemos
        self.all_sprite_list.add(self.cursor)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                return True

            if event.type == pygame.KEYDOWN:
                #Con tecla space se reinicia el juego
                if event.key == pygame.K_SPACE:
                    #Reinicio del juego
                    self.__init__()
        return False

    def run_logic(self):
        self.all_sprite_list.update()
        #Cambiar imgen del cursor dependiendo quien juegue
        if turno == 0:
            self.cursor.image = pygame.transform.scale(p1_cursor,(dim_icon,dim_icon))
        elif turno == 1:
            self.cursor.image = pygame.transform.scale(p2_cursor,(dim_icon,dim_icon))  

        if pandeo_cont > 50:
            pandeo_cont = 0
            vel_x_lluvia =  vel_x_lluvia * (-1)
        pandeo_cont+=1

        #Revisamos quien gano
        win = Check()
        if win == True:
            if turno == 1:
                print("El ganador es: Player 1!!")
                self.p1_score +=1
            elif turno == 0:
                print("El ganador es: Player 2!!")
                self.p2_score +=1


    def display_frame(self,screen,clic):
    
    ### ----- ZONA DE DIBUJO
        #Usar imagen de fondo
        bg = pygame.transform.scale(fondo,(ancho,alto))
        screen.blit(bg,(0,0))
        #Color de fondo
        screen.fill(WHITE)
        
        Draw_figs(screen)

        #Fondo animado
        for coord in coord_list:
            pygame.draw.circle(screen,BLUE,coord,2)
            coord[1] +=1
            coord[0] += vel_x_lluvia
            
            if coord[1] > alto:
                coord[1] = 0

        #Dibujar cuadricula (grid) del juego
        for i in range(1,3):
            pygame.draw.line(screen,BLACK,(ancho_grid*i,0),(ancho_grid*i,alto),5)
            pygame.draw.line(screen,BLACK,(0,alto_grid*i),(ancho,alto_grid*i),5)

        coord_tablero = Hover(screen,self.cursor.rect.x,self.cursor.rect.y,c)
        if clic == True:
            print(tablero[coord_tablero[0]][coord_tablero[1]])
            clic = False
            if tablero[coord_tablero[0]][coord_tablero[1]] == "":
                #Despues de escoger, cambian los turnos
                if turno == 0:
                    fig = "X"
                    turno = 1
                    c = GREEN
                elif turno == 1:
                    fig = "O"
                    turno = 0
                    c = RED
                tablero[coord_tablero[0]][coord_tablero[1]] = fig
                print(tablero)
            else:
                print("ERROR, Lugar ocupado")

        #Usar imagen en cursor, les restamos ajus para que quede centrado (Lo ultimo que pintamos para que quede encimado)
        ajus = dim_icon/2
        screen.blit(self.cursor.image,(self.cursor.rect.x-ajus,self.cursor.rect.y-ajus))
    ### ----- ZONA DE DIBUJO      

        #actualizar pantalla (refrescar)
        pygame.display.flip()



def Check():
    Ganador = ""
    if tablero[0][0] == tablero[0][1] and tablero[0][1] == tablero[0][2]:
        Ganador = tablero[0][0]
    elif tablero[0][0] == tablero[1][0] and tablero[1][0] == tablero[2][0]:
        Ganador = tablero[0][0]
    elif tablero[0][0] == tablero[1][1] and tablero[1][1] == tablero[2][2]:
        Ganador = tablero[0][0]
    elif tablero[0][1] == tablero[1][1] and tablero[1][1] == tablero[2][1]:
        Ganador = tablero[0][1]
    elif tablero[0][2] == tablero[1][2] and tablero[1][2] == tablero[2][2]:
        Ganador = tablero[0][2]
    elif tablero[2][0] == tablero[1][1] and tablero[1][1] == tablero[0][2]:
        Ganador = tablero[2][0]
    elif tablero[1][0] == tablero[1][1] and tablero[1][1] == tablero[1][2]:
        Ganador = tablero[1][0]
    elif tablero[2][0] == tablero[2][1] and tablero[2][1] == tablero[2][2]:
        Ganador = tablero[2][0]
    
    if Ganador != "":
        return True
    else:
        return False

def Draw_figs(screen):
    for i in range(3):
        for j in range(3):
            if tablero[i][j] == "X":
                pygame.draw.circle(screen,RED,centers_list[i][j],fig_size)
            elif tablero[i][j] == "O":
                pygame.draw.circle(screen,GREEN,centers_list[i][j],fig_size)

def Hover(screen,x_mouse,y_mouse,COLOR):
    #Donde se va a dibujar cada elemento
    current_x = 0
    current_y = 0
    #Primera columna
    if x_mouse < ancho_grid:
        current_y = 0
        #Primera fila [0][0]
        if y_mouse < alto_grid and tablero[0][0] == "":
            pygame.draw.circle(screen,COLOR,centers_list[0][0],fig_size)
            current_x = 0
        #Segunda fila [1][0]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid and tablero[1][0] == "":
            pygame.draw.circle(screen,COLOR,centers_list[1][0],fig_size)
            current_x = 1
        #Tercera fila [2][0]
        elif y_mouse > (alto_grid*2) and tablero[2][0] == "":
            pygame.draw.circle(screen,COLOR,centers_list[2][0],fig_size)
            current_x = 2
    
    #segunda columna
    elif x_mouse < (ancho_grid*2) and x_mouse > ancho_grid:
        current_y = 1
        #Primera fila [0][1]
        if y_mouse < alto_grid and tablero[0][1] == "":
            pygame.draw.circle(screen,COLOR,centers_list[0][1],fig_size)
            current_x = 0
        #Segunda fila [1][1]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid and tablero[1][1] == "":
            pygame.draw.circle(screen,COLOR,centers_list[1][1],fig_size)
            current_x = 1
        #Tercera fila [2][1]
        elif y_mouse > (alto_grid*2) and tablero[2][1] == "":
            pygame.draw.circle(screen,COLOR,centers_list[2][1],fig_size)
            current_x = 2
    
    #Tercera columna
    elif x_mouse > (ancho_grid*2) and x_mouse > ancho_grid:
        current_y = 2
        #Primera fila [0][2]
        if y_mouse < alto_grid and tablero[0][2] == "":
            pygame.draw.circle(screen,COLOR,centers_list[0][2],fig_size)
            current_x = 0
        #Segunda fila [1][2]
        elif y_mouse < (alto_grid*2) and y_mouse > alto_grid and tablero[1][2] == "":
            pygame.draw.circle(screen,COLOR,centers_list[1][2],fig_size)
            current_x = 1
        #Tercera fila [2][2]
        elif y_mouse > (alto_grid*2) and tablero[2][2] == "":
            pygame.draw.circle(screen,COLOR,centers_list[2][2],fig_size)
            current_x = 2
    
    return current_x,current_y


def main():
    #Visibilidad del mouse
    pygame.mouse.set_visible(False)

    #Reloj para controlar los FPS
    clock = pygame.time.Clock()

    game = Game()

    while True:  
        clic = game.process_events()

        game.run_logic()

        game.display_frame(screen,clic)
    
        clock.tick(60)

    #Salimos del programa
    pygame.quit()
    


if __name__ == "__main__":
    main()