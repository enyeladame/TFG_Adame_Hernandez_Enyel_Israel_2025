Motor de videojuegos inspirado en SCUMM — TRABAJO DE FINAL DE GRADO - ENYEL ISRAEL ADAME HERNÁNDEZ

Descripción del proyecto.
======================================
Motor 2D minimalista para aventuras gráficas estilo SCUMM, escrito en Python con Pygame. 

Incluye una demo jugable que muestra:
-Interfaz inspirada en SCUMM.
-Inventario de 2 filas × 3 columnas (6 casillas).
-Puertas, contenedores y objetos interactuables.
-Sistema de recetas y combinaciones de objetos (2 ? 1).
-Diálogos simples (mediante el control de flags).
-Guardado y carga de partida por medio de un archivo JSON.
-Resumen de rendimiento al terminar la ejecución del código (FPS, eventos, recursos, duración, pico de objetos en inventario).

Requisitos previos.
======================================
- Windows / macOS / Linux.
- Python 3.10 o superior (recomendado 3.10 o 3.11).
- pip actualizado.
- Permisos de lectura/escritura en la carpeta del proyecto.

Instalación rápida.
======================================
Windows (PowerShell o CMD):
1) Ir a la carpeta del proyecto:
   cd C:\DIR
   
2) Crear entorno virtual:
   py -3.10 -m venv .venv
   
3) Activar entorno:
   .venv\Scripts\activate
   
4) Actualizar pip:
   python -m pip install -U pip
   
5) Instalar dependencias:
   -Si existe 'requirements.txt':
       pip install -r requirements.txt
   -Si NO existe:
       pip install pygame

macOS / Linux (Terminal):
1) Ir a la carpeta del proyecto:
   cd ~/DIR
   
2) Crear entorno virtual:
   python3 -m venv .venv
   
3) Activar entorno:
   source .venv/bin/activate
   
4) Actualizar pip:
   python -m pip install -U pip
   
5) Instalar dependencias:
   -Si existe requirements.txt:
       pip install -r requirements.txt
   -Si NO existe:
       pip install pygame

Ejecutar la DEMO.
======================================
Desde la raíz del proyecto:

- Windows:
  cd C:\DIR
  python -m demo.main

- macOS / Linux:
  python demo/main.py


Estructura del proyecto.
======================================
TFG_AdameEnyelv3/
  engine/
    audio.py            (control de la música y volumen 0–10)
    combinaciones.py    (funcionamiento para el manejo de combinacion de objetos con recetas 2 objetos ? 1 objeto)
    cursor.py           (cursor personalizado para el proyecto)
    guardado.py         (control de guardado de partida + carga de estado con archivos JSON)
    menu.py             (control del menú principal)
    paneles.py          (control del panel inferior)
    recursos.py         (carga y caché de imágenes/fuentes/sonidos)
    rendimiento.py      (control y telemétria de FPS/eventos detectados durante la ejecución)
    scripting.py        (intérprete de scripts por triggers y/o acciones)
  demo/
    main.py             (bucle principal de la demo)
    datos/
      habitaciones.json (descripcion del "mundo": puertas, interactuables, objetos, scripts, dialogos, etc)
      recetas.json      (recetas de combinaciones posibles de objetos)
    assets/
      fondos/*.png
      items/*.png
      cursor/Cursor.png
      ost/*.mp3
      fuentes/Roboto-Regular.ttf    (disponible, fácil de leer para el usuario)
  LEEME.txt (este archivo).

Cómo personalizar la demo (modificando el contenido de los archivos JSON).
======================================
- Añadir/editar habitaciones: demo/datos/habitaciones.json
  -Fondo: la ruta del PNG que se utilizará de fondo.
  -Puertas: {id, rect|poligono, abierta, destino}
  -Interactuables: contenedores/objetos.
  -Scripts: reglas por trigger/objetivo/item con resultado diferente.

- Añadir/editar recetas: demo/datos/recetas.json
  - {"ingredientes": ["A","B"], "resultado": "C"}

El motor es data-driven (lógica jugable y contenido fuera del código del motor, declarado todo en datos externos), por lo que crear contenido no requiere tocar el motor, sino modificar los scripts, añadir assets y modificar el main.
