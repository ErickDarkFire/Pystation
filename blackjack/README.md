# Blackjack - Pystation
<img src="https://imgur.com/BHTANTm.png" alt="Menú de Inicio" width="500">


## Descripción del Proyecto
Este proyecto es una implementación clásica del juego de cartas Blackjack (también conocido como 21). El objetivo principal del juego es sumar un valor lo más cercano posible a 21 en tus cartas sin pasarte de dicho número y logrando un puntaje superior al del crupier (dealer).

## Capturas de Pantalla

| Partida en Curso | Resultado de la Partida |
| :---: | :---: |
| <img src="https://imgur.com/4V9TIx4.png" alt="Tablero de Juego" width="350"> | <img src="https://imgur.com/a14fugU.png" alt="Pantalla de Victoria/Derrota" width="350"> |
| *Interfaz principal mostrando las manos y controles.* | *Validación de la lógica de victoria/derrota.* |


## Lógica y Reglas del Juego
La lógica central sigue las reglas tradicionales del Blackjack:

1. **Valor de las Cartas**:
   - Las cartas del 2 al 10 valen su valor numérico.
   - Las figuras (J, Q, K) valen 10.
   - El As (A) puede valer 1 u 11, dependiendo de qué valor convenga más a la mano actual sin pasarse de 21.

2. **Mecánica de Turnos**:
   - Al inicio, tanto el jugador como el crupier reciben dos cartas.
   - El jugador juega primero y puede elegir pedir otra carta ("Pedir" o "Hit") o quedarse con su mano actual ("Plantarse" o "Stand").
   - Si el jugador supera los 21 puntos, pierde automáticamente la partida ("Bust").
   - Una vez que el jugador se planta, el crupier juega su turno revelando su carta oculta. El crupier está obligado por reglas de la casa a seguir pidiendo cartas hasta alcanzar un puntaje mínimo seguro (por lo general, 17 o más).

3. **Condiciones de Victoria**:
   - Conseguir exactamente 21 puntos con las dos primeras cartas (Blackjack natural) y que el crupier no lo tenga.
   - Plantarse con un puntaje final menor o igual a 21 que sea estrictamente mayor al del crupier.
   - Que el crupier pida cartas y se pase de 21 puntos mientras el jugador sigue vivo en la partida.

## Tecnologías Utilizadas
Este juego fue construido a partir de las siguientes tecnologías:
- **Python**: Lenguaje de programación principal empleado, utilizando Programación Orientada a Objetos (POO) para separar la lógica del juego, modelos (cartas, manos, jugadores) e interfaz.
- **Pygame**: Biblioteca utilizada para el motor gráfico, la recolección de eventos (clics, teclas) y el renderizado de los componentes visuales e interfaz gráfica.
- **Pytest / Coverage**: Herramientas para la ejecución de pruebas unitarias y garantizar una alta cobertura de código en el proyecto.

## Cómo Contribuir

Si deseas contribuir a la mejora de este minijuego o de PyStation en general:
1. Crea una rama desde `develop`: `git checkout -b feature/nueva-mejora`
2. Realiza tus cambios y asegúrate de agregar o actualizar las pruebas en la carpeta `tests/`.
3. Verifica que el código cumpla con los estándares ejecutando el linter: `flake8 .`
4. Sube tus cambios y abre un **Pull Request** hacia la rama `develop`.

Para más detalles sobre las reglas del proyecto, consulta la sección de contribución en el [README principal](../README.md).

## Otros Juegos en PyStation

Blackjack es parte de la colección de minijuegos **PyStation**. Puedes explorar los demás juegos y sus documentaciones aquí:

- 🎮 [Menú Principal / PyStation](../README.md)
- 🎲 [Craps](../craps/README.md)
- ♠️ [Poker](../poker/README.md)
- 🏓 [Pong](../pong/README.md)
- 🐍 [Snake](../snake/README.md)
- ❌⭕ Tic Tac Toe
