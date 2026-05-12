Feature: Flujo del juego de poker
  Como jugador de poker
  Quiero poder interactuar con la interfaz del juego
  Para poder apostar, jugar rondas y ver los resultados

  Scenario: Pantalla inicial del tablero
    Given el juego de poker está en ejecución
    Then el fondo de la mesa debe ser verde
    And el botón "DEAL" debe estar activo
    And el botón "BET" debe estar deshabilitado
    And el botón "FOLD" debe estar deshabilitado

  Scenario: Control del Ante con teclado y botones
    Given el juego de poker está en ejecución
    When hago clic en el centro para enfocar la ventana
    And escribo "50" con el teclado
    And hago clic en el botón "+" 2 veces
    Then la interfaz debe reflejar la interacción sin errores

  Scenario: Repartir cartas (Deal) e iniciar fase de apuesta
    Given el juego de poker está en ejecución
    When hago clic en el centro para enfocar la ventana
    And escribo "25" con el teclado
    And hago clic en el botón "DEAL"
    Then el botón "DEAL" debe estar deshabilitado
    And el botón "BET" debe estar activo
    And el botón "FOLD" debe estar activo

Scenario: Jugador decide foldear tras ver el Flop
    Given el juego de poker está en ejecución
    When hago clic en el centro para enfocar la ventana
    And escribo "10" con el teclado
    And hago clic en el botón "DEAL"
    And hago clic en el botón "FOLD"
    Then el botón "FOLD" debe estar deshabilitado
    And el botón "BET" debe estar deshabilitado
    And el botón "NEW_ROUND" debe estar activo

  Scenario: Jugador decide apostar tras ver el Flop
    Given el juego de poker está en ejecución
    When hago clic en el centro para enfocar la ventana
    And escribo "15" con el teclado
    And hago clic en el botón "DEAL"
    And hago clic en el botón "BET"
    Then el botón "BET" debe estar deshabilitado
    And el botón "FOLD" debe estar deshabilitado
    And el botón "NEW_ROUND" debe estar activo

  Scenario: Iniciar una nueva ronda después del Showdown
    Given el juego de poker está en ejecución
    When hago clic en el centro para enfocar la ventana
    And escribo "20" con el teclado
    And hago clic en el botón "DEAL"
    And hago clic en el botón "BET"
    And hago clic en el botón "NEW_ROUND"
    Then el botón "DEAL" debe estar activo
    And el botón "BET" debe estar deshabilitado
    And el botón "FOLD" debe estar deshabilitado
