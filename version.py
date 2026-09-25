"""Application version: the single source is the VERSION file in the project root."""

from __future__ import annotations

import sys
from pathlib import Path

from resources import resource_path

APP_NAME = "DataMobile Exchange Parser"
APP_VERSION = resource_path("VERSION").read_text(encoding="utf-8").strip()


def version_tuple(version: str = APP_VERSION) -> tuple[int, int, int, int]:
    parts = [int(part) for part in version.split(".")]
    return tuple((parts + [0, 0, 0, 0])[:4])  # type: ignore[return-value]


def windows_version_info(version: str = APP_VERSION) -> str:
    """Version resource for PyInstaller's --version-file (shown in the exe properties)."""
    numbers = version_tuple(version)
    strings = {
        "CompanyName": "DataMobile",
        "FileDescription": APP_NAME,
        "FileVersion": version,
        "InternalName": APP_NAME,
        "OriginalFilename": f"{APP_NAME}.exe",
        "ProductName": APP_NAME,
        "ProductVersion": version,
    }
    string_structs = ",\n          ".join(
        f"StringStruct({key!r}, {value!r})" for key, value in strings.items()
    )
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={numbers},
    prodvers={numbers},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '041904B0',
        [
          {string_structs}
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1049, 1200])])
  ]
)
"""


if __name__ == "__main__":
    # python version.py              -> prints the version (used by build scripts)
    # python version.py <file.txt>   -> writes the Windows version resource
    if len(sys.argv) > 1:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(windows_version_info(), encoding="utf-8")
    else:
        print(APP_VERSION)
