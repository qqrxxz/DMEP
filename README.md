# DataMobile Exchange Parser

Настольное приложение для расшифровки файлов обмена DataMobile в форматах
`.dm` и `.dmU`.

Программа сопоставляет значения из файла с описанием выбранного формата и
показывает результат в удобном текстовом виде. Работа выполняется локально: 
доступ к сети не требуется.

## Готовые версии

| Платформа | Файл | Назначение |
| --- | --- | --- |
| Windows x64 | [DataMobileExchangeParser_Portable_Windows_x64.zip]([releases/DataMobileExchangeParser_Portable_Windows_x64.zip](https://github.com/qqrxxz/DMEP/releases/download/v1.0.0/DataMobileExchangeParserSetup.exe)) | Portable-версия без установки |
| Windows Portable | [DataMobileExchangeParser_Portable_Windows_x64.zip](releases/DataMobileExchangeParser_Portable_Windows_x64.zip) | Portable-версия без установки |
| macOS | [DataMobileExchangeParser_macOS.dmg](releases/DataMobileExchangeParser_macOS.dmg) | Установка через DMG |
| macOS | [DataMobileExchangeParser_Portable_macOS.zip](releases/DataMobileExchangeParser_Portable_macOS.zip) | Portable-приложение в ZIP |
| Исходники | [DataMobileExchangeParser_Source.zip](releases/DataMobileExchangeParser_Source.zip) | Чистый архив проекта |

Сборки macOS универсальные и подходят для Apple Silicon и Intel. Windows-
версия предназначена для 64-битной Windows.

## Возможности

- 22 формата обмена DataMobile;
- разделитель полей `;`;
- кодировки UTF-8, UTF-8 BOM и Windows-1251;
- расшифровка операций, признаков, типов строк и служебных значений;
- вывод `значение не передано` для пустых или отсутствующих полей;
- отображение дополнительных значений, не описанных в выбранном формате;
- поддержка сложных файлов с несколькими типами строк;
- работа без сети и сохранения результата на диск.

Формат определяется только выбором пользователя. Автоматическое переключение
между форматами не выполняется.

## Использование

1. Запустите приложение.
2. Выберите нужный формат обмена в выпадающем списке.
3. Нажмите **Выбрать .dm / .dmU** и укажите файл.
4. Нажмите **Расшифровать**.
5. Результат появится в нижней части окна.

Если данные отображаются со смещением, сначала проверьте правильность
выбранного формата обмена.

### Windows portable

Полностью распакуйте ZIP, откройте папку `DataMobile Exchange Parser` и
запустите:

```text
DataMobile Exchange Parser.exe
```

Не переносите только EXE-файл отдельно: для работы приложения нужна соседняя
папка `_internal`.

### macOS

Для обычной установки откройте DMG и перенесите приложение в `Applications`.
Portable ZIP достаточно распаковать, после чего можно запускать файл
`DataMobile Exchange Parser.app`.

## Поддерживаемые форматы обмена

1. Документы из терминала
2. Единицы измерения
3. Загрузка документа
4. Ключ сессии
5. КМ для печати
6. КМ для сканирования
7. Контрагенты
8. Марки ЕГАИС
9. Пользователи
10. Связи шаблонов и дополнительных форм
11. Склады
12. Справочник значений дополнительных форм
13. Типы серий
14. Товары
15. Товары ЕГАИС
16. Товары изменённые
17. Шаблоны
18. Шаблоны штрихкодов
19. Штрихкоды
20. Штрихкоды изменённые
21. Элементы дополнительных форм
22. Ячейки

## Настройка разбора

Основные параметры вынесены из программного кода:

| Путь | Содержимое |
| --- | --- |
| `config/exchange_specs.json` | Список форматов, последовательность строк и порядок полей |
| `config/decoders.json` | Расшифровки служебных значений |
| `specs/` | Исходные описания всех 22 форматов |
| `exchange_parser.py` | Общая логика чтения и формирования результата |

При запуске из исходников изменения JSON применяются сразу. Чтобы они попали в
готовое `.exe` или `.app`, приложение необходимо пересобрать.

## Структура проекта

```text
DataMobileExchangeParser/
├── config/                         настройки форматов и расшифровок
├── installer/                      сценарий Inno Setup
├── releases/                       готовые архивы и установочные файлы
├── specs/                          документация по форматам обмена
├── tests/                          автоматические проверки
├── app_window.py                   интерфейс приложения
├── exchange_parser.py              разбор файлов
├── exchange_specs.py               загрузка схем
├── decoders.py                     расшифровка значений
├── main.py                         точка запуска
├── build_macos.sh                  сборка приложения macOS
├── build_dmg.sh                    создание DMG
├── build_portable_macos.sh         создание portable ZIP для macOS
├── build_windows.bat               сборка приложения Windows
├── build_portable_windows.bat      создание portable ZIP для Windows
└── build_installer_windows.bat     создание Windows-установщика
```

## Запуск из исходников

Рекомендуется 64-битный Python 3.10–3.13.

### macOS

```bash
chmod +x run_macos.command
./run_macos.command
```

Скрипт создаст локальное виртуальное окружение `.venv`, установит зависимости
и запустит приложение.

### Windows

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --no-compile -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Сборка macOS

Подготовьте исполняемые скрипты и соберите приложение:

```bash
chmod +x build_macos.sh build_dmg.sh build_portable_macos.sh
./build_macos.sh
```

Результат:

```text
dist/DataMobile Exchange Parser.app
```

По умолчанию создаётся универсальная сборка для Apple Silicon и Intel.
При необходимости можно собрать приложение только для одной архитектуры:

```bash
MACOS_ARCH=arm64 ./build_macos.sh
MACOS_ARCH=x86_64 ./build_macos.sh
```

Создание DMG:

```bash
./build_dmg.sh
```

Создание portable ZIP:

```bash
./build_portable_macos.sh
```

Оба файла появятся в каталоге `releases`.

## Сборка Windows

Windows-сборку следует выполнять в Windows с установленным 64-битным
Python 3.10–3.13.

### Приложение

```bat
build_windows.bat
```

Результат:

```text
dist\DataMobile Exchange Parser\DataMobile Exchange Parser.exe
```

### Portable ZIP

После успешной сборки приложения выполните:

```bat
build_portable_windows.bat
```

Результат:

```text
releases\DataMobileExchangeParser_Portable_Windows.zip
```

### Установщик

1. Установите Inno Setup 6.
2. Выполните:

```bat
build_installer_windows.bat
```

Результат:

```text
releases\DataMobileExchangeParserSetup.exe
```

Установщик размещает программу в профиле текущего пользователя и не требует
прав администратора.

## Проверка

macOS или Linux:

```bash
python3 -m unittest discover -s tests -v
```

Windows:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Набор проверок контролирует загрузку всех форматов, разбор первой строки
`КоличествоСтрокВФайле`, отсутствующие значения, расшифровки и объединённые
записи.

## Возможные предупреждения системы

Готовые файлы не подписаны коммерческими сертификатами.

- **Windows SmartScreen:** выберите **Подробнее → Выполнить в любом случае**,
  если файл получен из доверенного источника.
- **macOS Gatekeeper:** нажмите приложение правой кнопкой мыши, выберите
  **Открыть** и подтвердите запуск.

Для массового распространения рекомендуется подписать Windows-приложение
сертификатом Code Signing, а macOS-приложение — сертификатом Developer ID с
последующей нотариализацией.
