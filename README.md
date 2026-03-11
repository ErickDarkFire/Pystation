# Minijuegos con Pygame

## Descripción

Este proyecto consiste en la creación de una serie de minijuegos desarrollados con **Pygame**, una biblioteca ampliamente utilizada para el desarrollo de videojuegos en Python. El objetivo principal es aplicar técnicas de **pruebas de software** para verificar el correcto funcionamiento de cada minijuego.

El proyecto permite poner en práctica conceptos fundamentales de testing de software, análisis de código y uso de herramientas de cobertura para evaluar la calidad del código desarrollado en Pygame. Además, fomenta la identificación y corrección de errores para mejorar la estabilidad y la experiencia del usuario en cada minijuego.

---

## Requerimientos

Antes de ejecutar el proyecto, asegúrate de contar con lo siguiente:

- **Python** 3.10 o superior
- **pip** (gestor de paquetes de Python)
- Sistema operativo: Windows, macOS o Linux
- Conexión a internet para instalar dependencias (primera vez)

---

## Herramientas Utilizadas

| Herramienta     | Propósito                                              |
|-----------------|--------------------------------------------------------|
| `Pygame`        | Desarrollo y renderizado de los minijuegos             |
| `unittest`      | Framework de pruebas unitarias estándar de Python      |
| `coverage.py`   | Medición y reporte de cobertura de código              |
| `Git`           | Control de versiones del proyecto                      |

---

## Dependencias

Las dependencias del proyecto se encuentran en el archivo `requirements.txt`. Para instalarlas, ejecuta:

```bash
pip install -r requirements.txt
```

Contenido del archivo `requirements.txt`:

```
pygame==2.5.2
coverage==7.4.0
```

---

## Cómo Correr la Aplicación

### 1. Clonar el repositorio

```bash
git clone https://github.com/ErickDarkFire/Pystation.git
cd Pystation
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación principal

```bash
python main.py
```

### 4. Ejecutar las pruebas unitarias

Para correr todas las pruebas con `unittest`:

```bash
python -m unittest discover -s tests -v
```

### 5. Ejecutar las pruebas con reporte de cobertura

```bash
coverage run -m unittest discover -s tests
coverage report -m
```

Para generar un reporte HTML de cobertura:

```bash
coverage html -d coverage/
```

> El reporte se generará en la carpeta `coverage/`. Abre el archivo `index.html` en tu navegador para visualizarlo.

---

## Cómo Contribuir

Si deseas contribuir al proyecto, puedes seguir los siguientes pasos:

1. **Realizar un fork** del repositorio desde GitHub.

2. **Crear una nueva rama** para tu cambio:
   ```bash
   git checkout -b feature/nombre-de-tu-cambio
   ```

3. **Realizar los cambios** y agregar pruebas si es necesario.

4. **Hacer commit** de los cambios:
   ```bash
   git commit -m "feat: descripción clara del cambio realizado"
   ```

5. **Enviar los cambios** al repositorio remoto:
   ```bash
   git push origin feature/nombre-de-tu-cambio
   ```

6. **Crear un Pull Request** desde GitHub para revisión por parte del equipo.

> Por favor, asegúrate de que todas las pruebas existentes pasen antes de enviar tu Pull Request.

---

## Estructura General de Archivos

```
minijuegos-pygame/
│
├── main.py
├── requirements.txt
├── README.md
│
├── juegos/
│   ├── juego1.py
│   ├── juego2.py
│   └── juego3.py
│
├── assets/
│   ├── imagenes/
│   └── sonidos/
│
├── tests/
│   ├── test_juego1.py
│   ├── test_juego2.py
│   └── test_juego3.py
│
└── coverage/
```
