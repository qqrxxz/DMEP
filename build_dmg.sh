#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_NAME="DataMobile Exchange Parser"
APP_PATH="dist/${APP_NAME}.app"
STAGING_DIR="build/dmg"
DMG_PATH="releases/DataMobileExchangeParser_macOS.dmg"

if [ ! -d "$APP_PATH" ]; then
  echo "Ошибка: не найдено приложение ${APP_PATH}"
  echo "Сначала запустите ./build_macos.sh"
  exit 1
fi

mkdir -p releases build
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp -R "$APP_PATH" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"
rm -f "$DMG_PATH"

hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$STAGING_DIR" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

rm -rf "$STAGING_DIR"
echo
echo "Готово: ${DMG_PATH}"
