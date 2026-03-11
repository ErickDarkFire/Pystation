# Casino Poker — Juego de Ante

Un juego de póker de casino desarrollado en Python/Pygame donde juegas tu mano contra el crupier usando una estructura de apuesta de ante y cartas comunitarias compartidas.

---

## Requisitos

- Python 3.10 o superior
- pygame 2.1+

Instala todas las dependencias con:

```bash
pip install -r requirements.txt
```

---

## Cómo Ejecutar

```bash
python main.py
```

Presiona **Escape** o cierra la ventana para salir en cualquier momento.

---

## Cómo Jugar

### Objetivo
Forma la mejor mano de póker de 5 cartas usando tus 2 cartas privadas combinadas con las 5 cartas comunitarias. Gana al crupier para llevarte las fichas.

---

### Flujo de una Ronda

**1. Establece tu ante**
Usa los botones **−** y **+** (o escribe un número con el teclado) para elegir cuánto apostar. Luego presiona **DEAL**.

**2. El flop**
Recibes 2 cartas privadas (hole cards). El crupier también recibe 2 cartas, pero quedan boca abajo. Las primeras 3 cartas comunitarias (el flop) se revelan.

**3. Apostar o Retirarse**
- **BET** — Paga una cantidad adicional igual a tu ante para continuar. Las 2 cartas comunitarias restantes (turn y river) serán reveladas.
- **FOLD** — Te retiras y pierdes tu ante. La ronda termina de inmediato.

**4. Showdown** 
Todas las cartas se revelan. La mejor mano de 5 cartas de cada jugador, formada con sus 2 cartas privadas y las 5 comunitarias, determina al ganador.

---

### Regla de Calificación del Crupier
El crupier debe tener **al menos un Par** para calificar.

- **El crupier no califica** → Tu ante paga 1:1. Tu apuesta se devuelve (empate técnico).
- **El crupier califica y tú ganas** → Tanto tu ante como tu apuesta pagan 1:1.
- **El crupier califica y gana** → Pierdes tanto el ante como la apuesta.
- **Empate** → Ambas apuestas se devuelven.

---

### Ranking de Manos (de mayor a menor)

| Mano | Descripción |
|------|-------------|
| Escalera Real | A K Q J 10 del mismo palo |
| Escalera de Color | Cinco cartas consecutivas del mismo palo |
| Póker | Cuatro cartas del mismo valor |
| Full House | Trío + par |
| Color (Flush) | Cinco cartas cualesquiera del mismo palo |
| Escalera (Straight) | Cinco cartas consecutivas |
| Trío | Tres cartas del mismo valor |
| Doble Par | Dos pares distintos |
| Par | Dos cartas del mismo valor |
| Carta Alta | Sin combinación — gana la carta más alta |

---

### Resumen de Pagos

| Resultado | Ante | Apuesta |
|-----------|------|---------|
| Ganas (crupier califica) | 1:1 | 1:1 |
| Crupier no califica | 1:1 | Devuelta (push) |
| Gana el crupier | Perdida | Perdida |
| Empate | Devuelta | Devuelta |

---

## Controles

| Acción | Cómo |
|--------|------|
| Ajustar el ante | Clic en **−** / **+** o escribe dígitos con el teclado |
| Borrar dígito | Retroceso (Backspace) |
| Repartir cartas | Clic en **DEAL** |
| Continuar tras el flop | Clic en **BET** |
| Retirarse | Clic en **FOLD** |
| Iniciar nueva ronda | Clic en **NEW ROUND** |
| Recargar fichas | Clic en **RECHARGE ($500)** |
| Salir | Presiona **Escape** o cierra la ventana |

---



## Fichas Iniciales

Cada sesión comienza con **$500**. Si te quedas sin fichas, presiona **RECHARGE ($500)** para recargar y seguir jugando. El botón de recarga solo está disponible cuando tu contador de fichas llega a cero.