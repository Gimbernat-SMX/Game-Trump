"""Punto de entrada para PyInstaller."""
import os
import sys

# Asegurar que el directorio raíz está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main
main()
