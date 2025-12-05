# AI Video Editing Toolkit

Esta es una herramienta ligera para crear flujos de edición de video con ayuda de IA.
Combina operaciones básicas (recortes, cambios de velocidad, union de clips y
superposición de textos) con un generador heurístico de overlays para prompts o
transcripciones.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso rápido

```bash
python -m video_ai_tool entrada.mp4 salida.mp4 \
    --prompt "Presenta la marca, muestra el producto y remata con llamada a la acción" \
    --start 3 --end 27 --speed 1.1 --audio musica.mp3
```

Argumentos clave:
- `--prompt`: texto que se usa para generar overlays automáticos con la heurística AI.
- `--overlay`: se puede repetir para agregar mensajes personalizados.
- `--stitch`: lista opcional de videos extra para concatenar antes de editar.
- `--start` y `--end`: definen el recorte del clip original.

## Módulos
- `video_ai_tool.ai`: heurística que convierte prompts en instrucciones de overlay.
- `video_ai_tool.editor`: utilidades MoviePy para manipulación de video y audio.
- `video_ai_tool.cli`: interfaz de línea de comando y orquestador del pipeline.

## Nota

Las operaciones usan MoviePy y requieren FFMPEG instalado en el sistema. Ajusta
las rutas de fuente y salida según tus archivos locales.
