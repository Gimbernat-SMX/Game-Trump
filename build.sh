#!/usr/bin/env bash
# build.sh – genera el ejecutable en macOS y Linux
set -e

VENV="./venv"
PYTHON="$VENV/bin/python3"
PIP="$VENV/bin/pip"

echo "==> Comprobando entorno virtual..."
if [ ! -f "$PYTHON" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv "$VENV"
fi

echo "==> Instalando dependencias..."
$PIP install --quiet pygame-ce pyinstaller

echo "==> Limpiando builds anteriores..."
rm -rf build dist

echo "==> Compilando GimbernatBros..."
$VENV/bin/pyinstaller game.spec --clean --noconfirm

echo ""
echo "============================================="
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  Ejecutable:  dist/GimbernatBros"
    echo "  App Bundle:  dist/GimbernatBros.app"
else
    echo "  Ejecutable:  dist/GimbernatBros"
fi
echo "============================================="
