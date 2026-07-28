#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_NAME="DataMobile Exchange Parser"
APP_PATH="dist/${APP_NAME}.app"
ZIP_PATH="releases/DataMobileExchangeParser_Portable_macOS.zip"

if [ ! -d "$APP_PATH" ]; then
  echo "Ошибка: не найдено приложение ${APP_PATH}"
  echo "Сначала запустите ./build_macos.sh"
  exit 1
fi

mkdir -p releases
rm -f "$ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

echo
echo "Готово: ${ZIP_PATH}"
