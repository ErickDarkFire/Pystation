# Blackjack - Pystation

## Descripción del Proyecto
Este proyecto es una implementación clásica del juego de cartas Blackjack (también conocido como 21). El objetivo principal del juego es sumar un valor lo más cercano posible a 21 en tus cartas sin pasarte de dicho número y logrando un puntaje superior al del crupier (dealer).

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

## Mejoras Futuras
En futuras versiones, el proyecto tiene como meta implementar las siguientes mejoras:
- **Rediseño Moderno de la Interfaz**: Se espera actualizar y modernizar la experiencia visual para ofrecer una interfaz gráfica (UI) más limpia, dinámica y atractiva, incluyendo posibles animaciones y mejores componentes.
- **Mayor Cobertura y Nuevas Pruebas**: Se busca potenciar la robustez y fiabilidad del software incrementando la cantidad de pruebas unitarias, abarcando más casos borde y componentes de la interfaz de usuario.
