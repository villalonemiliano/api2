#!/bin/bash

# Exit on error
set -e

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install pytest pytest-cov

# Ejecutar pruebas
echo "Ejecutando pruebas..."
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Desactivar entorno virtual
deactivate 