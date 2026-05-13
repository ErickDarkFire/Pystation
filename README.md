# PyStation 🎮

> Colección de minijuegos clásicos desarrollados en Python/Pygame con énfasis en pruebas de software.

**Materia:** Pruebas de Software — ITESO
**Equipo:** Luis Hernández · Alan Rodríguez · Benjamín Rodríguez · Erick Rodríguez · Alan Varela · Sergio Espinosa

---

## Descripción

PyStation es una estación de juegos que reúne seis minijuegos clásicos de casino y arcade en una sola aplicación. El proyecto fue desarrollado aplicando prácticas profesionales de aseguramiento de calidad: pruebas unitarias, de integración, de sistema (BDD), análisis estático con linter y medición de cobertura de código, todo integrado en pipelines de CI con GitHub Actions.

Cada juego es un módulo independiente con su propia lógica, interfaz gráfica y suite de pruebas.

---

## Requerimientos del sistema

| Requisito | Versión mínima |
|-----------|---------------|
| Python | 3.10 |
| pip | Incluido con Python |
| Sistema operativo | Windows 10 / macOS 12 / Ubuntu 22.04 |
| Pantalla | Resolución 800×600 o superior |

---

## Herramientas utilizadas

| Herramienta | Propósito |
|-------------|-----------|
| **Pygame** | Motor gráfico y de eventos para todos los juegos |
| `unittest` | Framework de pruebas unitarias e integración (Python estándar) |
| `pytest` | Framework de pruebas para Poker (fixtures, parametrización) |
| `coverage.py` | Medición y reporte de cobertura de código |
| `pytest-cov` | Plugin de cobertura integrado con pytest |
| `behave` | Framework BDD para pruebas de sistema (Blackjack y Snake) |
| `flake8` | Analizador estático / linter de código Python |
| `pre-commit` | Hooks que ejecutan linting antes de cada commit |
| **GitHub Actions** | CI/CD: linting, pruebas y cobertura en cada Pull Request |
| `Git` | Control de versiones |

---

## Dependencias

Instala las dependencias globales desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

```
# requirements.txt
pygame>=2.0.0
coverage>=7.0.0
```

Algunos juegos tienen dependencias adicionales:

```bash
# Poker
pip install pytest pytest-cov

# Snake (desarrollo y pruebas completas)
pip install -r snake/requirements-dev.txt

# Pong (pruebas de sistema)
pip install behave
```

---

## Cómo correr la aplicación

### 1. Clonar el repositorio

```bash
git clone https://github.com/ErickDarkFire/Pystation.git
cd Pystation
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 3. Lanzar el menú principal

```bash
python Menu.py
```

Desde el menú puedes seleccionar cualquier juego. También puedes ejecutar cada juego de forma individual:

```bash
python blackjack/blackjack.py
python craps/craps.py
python poker/poker.py
python pong/pong.py
python snake/snake.py
python Tic_tac_toe/Tic_tac_toe.py
```
---

## Cómo ejecutar las pruebas

### Todas las pruebas con cobertura (por juego)

```bash
# Blackjack — unittest
coverage run --source=blackjack -m unittest discover -s blackjack -t blackjack
coverage report -m

# Craps — unittest
cd craps
coverage run --source=. tests/unittests.py
coverage report -m
cd ..

# Poker — pytest
cd poker
pytest tests/ --cov=. --cov-report=term-missing
cd ..

# Pong — unittest (requiere SDL dummy en Linux/CI)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  coverage run --source=pong -m unittest discover -s pong/tests -t pong
coverage report -m

# Snake — unittest + integración
cd snake
coverage run --rcfile=.coveragerc -m unittest discover -s tests -t .
coverage run --rcfile=.coveragerc --append -m unittest discover -s integration_tests -t .
coverage report --rcfile=.coveragerc -m
cd ..
```

### Reporte HTML de cobertura

```bash
coverage html -d coverage_html/
# Abre coverage_html/index.html en el navegador
```

---

## Integración continua (CI)

El repositorio tiene cinco workflows de GitHub Actions que se ejecutan automáticamente en cada Pull Request:

| Workflow        | Archivo                                 | Cuándo se activa                  |
|-----------------|-----------------------------------------|-----------------------------------|
| CI principal    | `.github/workflows/ci.yaml`             | PRs a `main` o `develop`          |
| Snake CI        | `.github/workflows/snake-ci.yaml`       | PRs con cambios en `snake/`       |
| Poker CI        | `.github/workflows/poker-ci.yaml`       | PRs con cambios en `poker/`       |
| Tic tac toe CI  | `.github/workflows/tic_tac_toe-ci.yaml` | PRs con cambios en `Toc_tac_toe/` |
| Pre-commit      | `.github/workflows/.pre-commit.yaml`    | PRs a `main`                      |

El CI principal ejecuta en orden:
1. **Linter** — `flake8 .` sobre todo el código
2. **Blackjack** — 41 pruebas, cobertura ≥ 85%
3. **Craps** — pruebas unitarias, reporte de cobertura
4. **Poker** — 155 pruebas con pytest, reporte de cobertura
5. **Pong** — 28 pruebas, reporte de cobertura
6. **Tic tac toe** — 23 pruebas, reporte de cobertura

---

## Cómo contribuir

1. Crea una rama desde `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/nombre-del-cambio
   ```

2. Realiza tus cambios y agrega pruebas para la nueva funcionalidad.

3. Verifica que el linter pase:
   ```bash
   flake8 .
   ```

4. Verifica que todas las pruebas sigan pasando con cobertura aceptable.

5. Haz commit y push:
   ```bash
   git add .
   git commit -m "feat: descripción del cambio"
   git push origin feature/nombre-del-cambio
   ```

6. Abre un **Pull Request** hacia `develop` en GitHub. El CI se ejecutará automáticamente y un compañero debe revisar y aprobar el PR antes de hacer merge.

> **Regla de equipo:** ningún PR se mergea sin al menos una aprobación y el CI en verde.

---

## Estructura general de archivos

```
Pystation/
│
├── Menu.py                        # Punto de entrada — menú principal
├── requirements.txt               # Dependencias globales
├── README.md
├── .flake8
├── .coverage
│
├── .vscode/
│   └── settings.json
│
├── .github/
│   └── workflows/
│       ├── ci.yaml                # CI principal (lint + pruebas de todos los juegos)
│       ├── snake-ci.yaml          # CI dedicado para Snake con diff de cobertura
│       ├── poker-ci.yaml          # CI dedicado para poker con diff de cobertura
│       ├── tic_tac_toe-ci.yaml    # CI dedicado para Tic tac toe con diff de cobertura y pruebas en gui
│       └── .pre-commit.yaml       # Ejecución de hooks pre-commit en CI
│
├── mockups/                       # Capturas de pantalla de la aplicación
│   ├── poker.png
│   ├── snake.png
│   └── tictactoe.png
│
├── blackjack/
│   ├── blackjack.py               # Punto de entrada del juego
│   ├── core/game.py               # Lógica principal
│   ├── models/                    # Card, Hand, Player, Shoe
│   ├── ui/                        # Button, CardRenderer, Overlay, Table
│   ├── img/
│   └── tests/                     # 41 pruebas unitarias + integración + BDD
│
├── craps/
│   ├── craps.py                   # Punto de entrada
│   ├── craps_game.py              # Lógica del juego
│   ├── img/
│   └── tests/
│       ├── unittests.py           # Pruebas unitarias
│       └── pyautogui_test.py      # Pruebas de sistema (requieren pantalla)
│
├── poker/
│   ├── poker.py                   # UI del juego
│   ├── game_logic.py              # Lógica: cartas, manos, fases del juego
│   ├── requirements.txt
│   ├── img/
│   ├── tests/
│   │   ├── test_unit.py           # Pruebas unitarias
│   │   └── test_integration.py    # Pruebas de integración
│   └── system_tests/
│       └── features/              # Pruebas BDD con behave
│
├── pong/
│   ├── pong.py                    # Juego completo
│   ├── sound_manager.py           # Motor de sonido
│   ├── requirements.txt
│   ├── img/
│   ├── sound/
│   ├── features/                  # Escenarios BDD
│   └── tests/
│       ├── test_pong_logic.py
│       └── test_sound_manager.py
│
├── snake/
│   ├── snake.py                   # Lógica del juego
│   ├── game_ui.py                 # Interfaz gráfica
│   ├── sound_manager.py
│   ├── img/
│   ├── tests/                     # Pruebas unitarias
│   ├── integration_tests/         # Pruebas de integración
│   └── system_tests/features/     # Pruebas BDD con behave
│
└── Tic_tac_toe/
    ├── Tic_tac_toe.py
    ├── features/
    │   ├── steps/
    |   │   └── steps.py
    │   └── tictactoe.feature
    ├── tests/
    |   └── test_tic_tac_toe.py
    ├── img/
    │   ├── gato_bg.jpg
    │   ├── gato_bg2.jpg
    │   ├── logo.png
    │   ├── p1_cursor.png
    │   └── p2_cursor.png
    ├── .coverage
    └── musica/
        ├── background.mp3
        └── write.wav
```

---

## Resumen de pruebas por juego

| Juego       | Framework         | Pruebas | Cobertura lógica    |
|-------------|-------------------|---------|---------------------|
| Blackjack   | unittest + behave | 41      | 98%                 |
| Craps       | unittest          | 2       | 34% (craps_game.py) |
| Poker       | pytest            | 155     | 96% (game_logic.py) |
| Pong        | unittest          | 28      | 79%                 |
| Snake       | unittest + behave | 80+     | >85%                |
| Tic Tac Toe | unittest + behave | 23      | 72%                 |
