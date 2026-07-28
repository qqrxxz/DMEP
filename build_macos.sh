#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_NAME="DataMobile Exchange Parser"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MACOS_ARCH="${MACOS_ARCH:-universal2}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Ошибка: Python 3 не найден."
  echo "Установите Python 3.10–3.13 с python.org и повторите запуск."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade --no-compile "pip==25.0.1"
.venv/bin/python -m pip install --no-compile -r requirements.txt

.venv/bin/python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --target-arch "$MACOS_ARCH" \
  --name "$APP_NAME" \
  --add-data "config:config" \
  --add-data "specs:specs" \
  main.py

echo
echo "Готово: dist/${APP_NAME}.app"
