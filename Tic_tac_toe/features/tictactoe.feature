Feature: Juego de Tic-tac-toe
  Como jugador
  Quiero marcar una fila completa
  Para ganar la partida

  Scenario: Ganar por fila superior
    Given que el juego esta abierto
    When el Jugador 1 hace clic en la celda (0,0)
    And el Jugador 2 hace clic en la celda (1,0)
    And el Jugador 1 hace clic en la celda (0,1)
    And el Jugador 2 hace clic en la celda (1,1)
    And el Jugador 1 hace clic en la celda (0,2)
    Then deberia mostrarse el mensaje de victoria "Gano el jugador 1!"
  
  Scenario: Jugador 2 gana por diagonal inversa
    Given que el juego esta abierto
    When el Jugador 1 hace clic en la celda (0,0)
    And el Jugador 2 hace clic en la celda (0,2)
    And el Jugador 1 hace clic en la celda (0,1)
    And el Jugador 2 hace clic en la celda (1,1)
    And el Jugador 1 hace clic en la celda (1,0)
    And el Jugador 2 hace clic en la celda (2,0)
    Then deberia mostrarse el mensaje de victoria "Gano el jugador 2!"

  Scenario: Empate tras llenar el tablero
    Given que el juego esta abierto
    When el Jugador 1 hace clic en la celda (0,0)
    And el Jugador 2 hace clic en la celda (0,1)
    And el Jugador 1 hace clic en la celda (0,2)
    And el Jugador 2 hace clic en la celda (1,1)
    And el Jugador 1 hace clic en la celda (1,0)
    And el Jugador 2 hace clic en la celda (1,2)
    And el Jugador 1 hace clic en la celda (2,1)
    And el Jugador 2 hace clic en la celda (2,0)
    And el Jugador 1 hace clic en la celda (2,2)
    Then no deberia mostrarse ningun mensaje de victoria
  
  Scenario: Reiniciar el juego despues de una victoria
    Given que el juego esta abierto
    And el Jugador 1 ha ganado una partida
    When el usuario presiona la tecla "space"
    Then el tablero deberia estar limpio para una nueva partida