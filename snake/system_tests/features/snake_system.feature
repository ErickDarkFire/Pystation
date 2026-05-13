Feature: Snake Deluxe — Pruebas de sistema
  Como jugador de Snake Deluxe
  Quiero que el juego responda correctamente a mis acciones de teclado
  Para poder disfrutar de una experiencia de juego fluida y predecible

  Background:
    Given el juego está abierto y en el menú principal
    And la ventana del juego tiene el foco

  Scenario: 01 - Inicio del juego desde el menú principal
    When el usuario presiona Enter para iniciar
    Then el juego entra en modo de juego activo
    And la serpiente aparece en el tablero

  Scenario: 02 - La serpiente responde a la tecla de flecha derecha
    Given el juego está en modo de juego activo
    When el usuario presiona la flecha derecha
    And espera 1.5 segundos
    Then la serpiente se está moviendo hacia la derecha

  Scenario: 03 - La serpiente cambia de dirección con WASD
    Given el juego está en modo de juego activo
    When el usuario presiona la tecla W para moverse hacia arriba
    And espera 1 segundo
    And el usuario presiona la tecla D para moverse hacia la derecha
    And espera 1 segundo
    Then la serpiente cambió de dirección correctamente

  Scenario: 04 - La serpiente avanza de forma continua sin input adicional
    Given el juego está en modo de juego activo
    When el usuario presiona la flecha arriba para iniciar el movimiento
    And espera 3 segundos sin presionar ninguna tecla
    Then la serpiente ha avanzado de forma continua

  Scenario: 05 - La serpiente come la fruta y aumenta de tamaño
    Given el juego está en modo de juego activo
    And la fruta está posicionada a la derecha de la serpiente
    And se registra la longitud inicial de la serpiente
    When el usuario presiona la flecha derecha para comer la fruta
    And espera 1.5 segundos para que el movimiento se complete
    Then la longitud de la serpiente aumentó en al menos 1

  Scenario: 06 - El puntaje aumenta al comer la fruta
    Given el juego está en modo de juego activo
    And la fruta está posicionada a la derecha de la serpiente
    And se registra el puntaje inicial
    When el usuario presiona la flecha derecha para comer la fruta
    And espera 1.5 segundos para que el movimiento se complete
    Then el puntaje del jugador aumentó

  Scenario: 07 - Una nueva fruta aparece tras comer la anterior
    Given el juego está en modo de juego activo
    And la fruta está posicionada a la derecha de la serpiente
    And se registra la posición inicial de la fruta
    When el usuario presiona la flecha derecha para comer la fruta
    And espera 1.5 segundos para que el movimiento se complete
    Then una nueva fruta aparece en el tablero en una posición diferente

  Scenario: 08 - Colisión con la pared provoca Game Over
    Given el juego está en modo de juego activo
    And la serpiente está posicionada cerca del borde derecho
    When el usuario presiona la flecha derecha hacia la pared
    And espera 2 segundos para que ocurra la colisión
    Then el juego muestra la pantalla de Game Over

  Scenario: 09 - La pantalla de Game Over se muestra tras colisión
    Given el juego está en modo de juego activo
    When el usuario dirige la serpiente hacia la pared superior
    And espera 4 segundos para que colisione
    Then el juego muestra la pantalla de Game Over
    And el puntaje final es visible en pantalla

  Scenario: 10 - Reinicio del juego después de Game Over
    Given el juego está en modo de juego activo
    When el usuario dirige la serpiente hacia la pared superior
    And espera 4 segundos para que colisione
    And el juego muestra la pantalla de Game Over
    And el usuario espera 1 segundo
    And el usuario presiona Enter para reiniciar
    And espera 2 segundos para que el juego reinicie
    Then el juego entra en modo de juego activo
    And la serpiente aparece en el tablero
