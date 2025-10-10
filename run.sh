#!/bin/bash
# Script para activar entorno virtual y ejecutar main.py

# Ruta al entorno virtual
VENV_DIR="venv"

# Verifica si el entorno virtual existe
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ No se encontró el entorno virtual en: $VENV_DIR"
    exit 1
fi

# Activar el entorno virtual
source "$VENV_DIR/bin/activate"

# Ejecutar el archivo Python
python bot.py

# Desactivar el entorno virtual (opcional, porque se hace automáticamente al terminar el script)
# deactivate
