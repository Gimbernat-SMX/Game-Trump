#!/usr/bin/env bash
# PumpTrump – Script de instalación
# Uso: sh install.sh

set -e

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJ_DIR/venv"

echo "=== PumpTrump – Instalación ==="

# 1. Comprobar Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 no está instalado. Instálalo y vuelve a ejecutar."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)")
if [ "$PYTHON_VERSION" -lt 38 ]; then
    echo "ERROR: Se necesita Python 3.8 o superior."
    exit 1
fi

echo "Python OK: $(python3 --version)"

# 2. Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
fi

# 3. Instalar dependencias
echo "Instalando dependencias..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet pygame-ce

echo ""
echo "=== Instalación completada ==="
echo "Para iniciar el juego ejecuta:  ./run"
