"""Empaqueta la aplicación como ejecutable usando PyInstaller.

Uso:
    python build_app.py

Requiere instalar PyInstaller en el entorno de Python:
    python -m pip install pyinstaller
"""

from __future__ import annotations

import shutil
import subprocess
import sys

APP_NAME = "EquipoPlato"


def main() -> int:
    if shutil.which("pyinstaller") is None:
        print("PyInstaller no está instalado.")
        print("Instálalo con: python -m pip install pyinstaller")
        return 1

    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "app.py",
    ]
    print("Ejecutando:", " ".join(command))
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
