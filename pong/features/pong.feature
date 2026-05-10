Feature: Pruebas de sistema del juego Pong
  Como usuario
  Quiero interactuar con el juego Pong
  Para verificar que las teclas principales funcionen correctamente

  Scenario: Pausar y continuar el juego
    Given que abro el juego Pong
    When presiono la tecla "p"
    Then el juego debe quedar pausado
    When presiono la tecla "p"
    Then el juego debe continuar

  Scenario: Reiniciar el juego
    Given que abro el juego Pong
    When presiono la tecla "r"
    Then el marcador debe estar en 0 para ambos jugadores
    And el juego debe continuar

  Scenario Outline: Mover jugadores
    Given que abro el juego Pong
    When mantengo presionada la tecla "<tecla>" por 0.4 segundos
    Then el "<jugador>" debe moverse hacia "<direccion>"

    Examples:
      | jugador  | tecla | direccion |
      | jugador1 | up    | arriba    |
      | jugador1 | down  | abajo     |
      | jugador2 | w     | arriba    |
      | jugador2 | s     | abajo     |
