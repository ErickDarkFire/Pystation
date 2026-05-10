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
- **Pausar partida:** `P`
- **Reiniciar partida:** `R`

## Reglas

- Cada vez que la pelota sale por un lado, el jugador contrario gana un punto.
- El primer jugador en llegar a **5 puntos** gana la partida.
- Cuando termina el juego, se puede reiniciar presionando `R`.

## Requisitos

- Python 3
- Pygame

## Tecnologías Utilizadas

- **Python**: Lenguaje principal del proyecto.
- **Pygame**: Biblioteca utilizada para crear la ventana, gráficos, eventos y lógica del juego.
- **unittest**: Framework estándar de Python utilizado para las pruebas unitarias e integración.
- **coverage.py**: Herramienta utilizada para medir la cobertura de código.
- **Behave**: Herramienta utilizada para escribir pruebas de sistema con BDD.
- **PyDirectInput**: Herramienta utilizada para simular entradas de teclado en la ventana del juego.
- **Pylint**: Linter utilizado para análisis estático del código.
- **GitHub Actions**: Herramienta utilizada para ejecutar automáticamente pruebas y análisis en cada pull request.

## Instalación

Primero clona el repositorio:

```bash
git clone <link-del-repositorio>
cd pong
```

Luego instala las dependencias

```bash
pip install -r requirements.txt
```

"o" usa para instalar dependencias
```bash
pip install pygame coverage behave pydirectinput pygetwindow pylint
```

## Cómo correr la aplicación

Para ejecutar el juego:

```bash
py pong.py
```

## Pruebas

El proyecto cuenta con pruebas unitarias, pruebas de integración y pruebas de sistema.

### Pruebas unitarias e integración

Las pruebas unitarias validan funciones específicas del juego, como movimiento de jugadores, reinicio de marcador, pausa, rebotes, puntuación y declaración de ganador.

Para ejecutar las pruebas:

```bash
py -m coverage run -m unittest discover -s tests -p "test_*.py"
py -m coverage reportpy -m coverage report
```

### Para ejecutar las pruebas de sistema BDD:

```bash
py -m behave --no-capture
```

