# Pong en Pygame
<img src="https://i.imgur.com/ZEK1fBQ.png" alt="Menú de inicio" width="500">

## Descripción del proyecto
Este pequeño proyecto es un juego sencillo de Pong realizado con Python y Pygame.  
Dos jugadores controlan una barra cada uno y deben evitar que la pelota salga de su lado de la pantalla.

## Capturas de Pantalla

| Partida en Curso | Resultado de la Partida |
| :---: | :---: |
| <img src="https://i.imgur.com/hvRpFZS.png" alt="Tablero de Juego" width="350"> | <img src="https://i.imgur.com/VeIKa6B.png" alt="Pantalla de Victoria/Derrota" width="350"> |
| *Interfaz mostrando la partida en curso.* | *Validación de la lógica de victoria/derrota.* |

## Controles

- **Jugador izquierdo:** `W` y `S`
- **Jugador derecho:** `flecha arriba` y `flecha abajo`
- **Reiniciar partida:** `R`

## Reglas

- Cada vez que la pelota sale por un lado, el jugador contrario gana un punto.
- El primer jugador en llegar a **5 puntos** gana la partida.
- Cuando termina el juego, se puede reiniciar presionando `R`.

## Requisitos

- Python 3
- Pygame

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal empleado
- **Pygame**: Biblioteca utilizada para el motor gráfico
- **Pytest / Coverage**: Herramientas para la ejecución de pruebas unitarias y garantizar una alta cobertura de código en el proyecto.

## Instalación

Primero instala Pygame con:

```bash
pip install pygame