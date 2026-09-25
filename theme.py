from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

from resources import resource_path


@dataclass(frozen=True)
class Theme:
    window: str
    surface: str
    surface_alt: str
    border: str
    text: str
    muted: str
    faint: str
    accent: str
    accent_hover: str
    accent_text: str
    accent_soft: str
    danger: str
    danger_soft: str
    arrow_icon: str


LIGHT = Theme(
    window="#F3F4F6",
    surface="#FFFFFF",
    surface_alt="#F7F8FA",
    border="#DADDE3",
    text="#1F2328",
    muted="#5B636E",
    faint="#98A0AB",
    accent="#2563EB",
    accent_hover="#1D4ED8",
    accent_text="#FFFFFF",
    accent_soft="#E8EFFD",
    danger="#C62828",
    danger_soft="#FDECEC",
    arrow_icon="assets/chevron-down-light.png",
)

DARK = Theme(
    window="#18191C",
    surface="#222429",
    surface_alt="#282B31",
    border="#3A3E46",
    text="#E7E9EC",
    muted="#A3AAB5",
    faint="#6E7580",
    accent="#5B93FF",
    accent_hover="#7AA7FF",
    accent_text="#0F1115",
    accent_soft="#223352",
    danger="#FF7B72",
    danger_soft="#3A2226",
    arrow_icon="assets/chevron-down-dark.png",
)


def is_dark_mode() -> bool:
    hints = QGuiApplication.styleHints()
    if hasattr(hints, "colorScheme"):
        return hints.colorScheme() == Qt.ColorScheme.Dark
    return QGuiApplication.palette().color(QPalette.Window).lightness() < 128


def current_theme() -> Theme:
    return DARK if is_dark_mode() else LIGHT


def monospace_family() -> str:
    return QFontDatabase.systemFont(QFontDatabase.FixedFont).family()


def apply_theme(app: QApplication, theme: Theme) -> None:
    """Use Fusion so the stylesheet looks the same on Windows and macOS."""
    app.setStyle("Fusion")

    font = app.font()
    if font.pointSizeF() < 10:
        font.setPointSizeF(10)
        app.setFont(font)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(theme.window))
    palette.setColor(QPalette.WindowText, QColor(theme.text))
    palette.setColor(QPalette.Base, QColor(theme.surface))
    palette.setColor(QPalette.AlternateBase, QColor(theme.surface_alt))
    palette.setColor(QPalette.Text, QColor(theme.text))
    palette.setColor(QPalette.Button, QColor(theme.surface))
    palette.setColor(QPalette.ButtonText, QColor(theme.text))
    palette.setColor(QPalette.Highlight, QColor(theme.accent))
    palette.setColor(QPalette.HighlightedText, QColor(theme.accent_text))
    palette.setColor(QPalette.PlaceholderText, QColor(theme.faint))
    palette.setColor(QPalette.ToolTipBase, QColor(theme.surface))
    palette.setColor(QPalette.ToolTipText, QColor(theme.text))
    app.setPalette(palette)
    app.setStyleSheet(stylesheet(theme))


def stylesheet(t: Theme) -> str:
    arrow = resource_path(t.arrow_icon).as_posix()
    return f"""
    QMainWindow, QWidget#central {{
        background: {t.window};
    }}
    QLabel {{
        color: {t.text};
    }}
    QLabel#title {{
        font-size: 18pt;
        font-weight: 600;
    }}
    QLabel#cardTitle {{
        font-weight: 600;
    }}
    QLabel#subtitle, QLabel#caption, QLabel#status {{
        color: {t.muted};
    }}
    QFrame#card {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: 12px;
    }}
    QFrame#card[dropTarget="true"] {{
        background: {t.accent_soft};
        border: 2px dashed {t.accent};
    }}
    QComboBox, QLineEdit {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 8px;
        padding: 6px 12px;
        min-height: 24px;
        selection-background-color: {t.accent};
        selection-color: {t.accent_text};
    }}
    QLineEdit[readOnly="true"] {{
        background: {t.surface_alt};
    }}
    QComboBox:hover, QLineEdit:hover {{
        border-color: {t.faint};
    }}
    QComboBox:focus, QLineEdit:focus {{
        border-color: {t.accent};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 32px;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url("{arrow}");
        width: 12px;
        height: 8px;
    }}
    QComboBox QAbstractItemView {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        selection-background-color: {t.accent_soft};
        selection-color: {t.text};
        outline: none;
        padding: 4px;
    }}
    QPushButton {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 8px;
        padding: 6px 16px;
        min-height: 24px;
    }}
    QPushButton:hover {{
        background: {t.surface_alt};
        border-color: {t.faint};
    }}
    QPushButton:pressed {{
        background: {t.accent_soft};
    }}
    QPushButton:disabled {{
        color: {t.faint};
        background: {t.surface_alt};
    }}
    QPushButton#primary {{
        background: {t.accent};
        color: {t.accent_text};
        border: 1px solid {t.accent};
        font-weight: 600;
    }}
    QPushButton#primary:hover {{
        background: {t.accent_hover};
        border-color: {t.accent_hover};
    }}
    QCheckBox {{
        color: {t.muted};
        spacing: 8px;
    }}
    QTextBrowser {{
        background: {t.surface};
        border: none;
        border-top: 1px solid {t.border};
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        padding: 8px 16px;
        selection-background-color: {t.accent_soft};
        selection-color: {t.text};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 12px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {t.border};
        border-radius: 4px;
        min-height: 32px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t.faint};
    }}
    QScrollBar::add-line, QScrollBar::sub-line,
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: none;
        height: 0;
        width: 0;
    }}
    QToolTip {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        padding: 4px 8px;
    }}
    """


def output_font(base: QFont) -> QFont:
    font = QFont(base)
    font.setPointSizeF(max(base.pointSizeF(), 10) + 1)
    return font
