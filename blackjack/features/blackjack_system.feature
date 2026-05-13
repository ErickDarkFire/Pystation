Feature: Pruebas de sistema e interfaz de Blackjack
  Como jugador de Blackjack
  Quiero interactuar con la interfaz gráfica
  Para poder apostar, pedir cartas, plantarme y ver si gano o pierdo

  Scenario: Usuario hace apuesta y reparte cartas
    Given el estado del juego es "BETTING" y la apuesta actual es 0
    And el mazo tiene las cartas preparadas para repartir inicialmente
    When el usuario hace clic en la ficha de $10
    And hace clic en el botón DEAL
    Then la apuesta actual es 10
    And el estado del juego cambia a "PLAYING"
    And el jugador tiene 2 cartas
    And el crupier tiene 2 cartas

  Scenario: Jugador pide carta y se pasa de 21 perdiendo inmediatamente
    Given una apuesta válida de 50
    And el mazo está preparado para que el jugador saque un 20 y luego un 5
    When se reparten las cartas
    And el jugador hace clic en el botón HIT
    Then el jugador tiene 3 cartas
    And el estado del juego cambia a "RESULT"
    And el mensaje principal es "DEALER WINS"

  Scenario: Jugador se planta y el crupier tiene menos, ganando el jugador
    Given una apuesta válida de 100 y saldo de 900
    And el mazo está preparado para que el jugador tenga 20 y el crupier 17
    When se reparten las cartas
    And el jugador hace clic en el botón STAND
    Then el estado del juego cambia a "RESULT"
    And el mensaje principal es "YOU WIN!"
    And el saldo del jugador aumenta a 1100
