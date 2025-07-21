# -*- coding: utf-8 -*-
"""
@file color_pantone.py
@brief Centralized color palette and CSS style definitions used across the GUI.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Defines color palette and stylesheet constants used for dark/light UI modes.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtGui import QPalette, QColor


class GeneralGUIPalette:
    """
    @brief Contains all primary colors and CSS styles used in the GUI.

    Includes styles for group boxes, line edits, combo boxes, checkboxes,
    accordion headers, labels, buttons, menus, dialogs, tabs, and text areas.
    """

    """
    @var PRIMARY_BG
    Primary background color used in main windows and panels.
    """
    PRIMARY_BG = "#23272e"

    """
    @var SECONDARY_BG
    Secondary background color, typically used for input fields and panels.
    """
    SECONDARY_BG = "#1e1e1e"

    """
    @var ACCENT
    Accent color used for highlights and interactive elements.
    """
    ACCENT = "#3a9dda"

    """
    @var HIGHLIGHT
    Highlight color used for selection and focus states.
    """
    HIGHLIGHT = "#61dafb"

    """
    @var GROUPBOX_BG
    Background color specifically for group boxes.
    """
    GROUPBOX_BG = "#23272e"

    """
    @var GROUPBOX_BORDER
    Border color used around group boxes.
    """
    GROUPBOX_BORDER = "#2a2d2e"

    """
    @var TEXT_MAIN
    Main text color used for standard labels and text.
    """
    TEXT_MAIN = "#d4d4d4"

    """
    @var TEXT_ACCENT
    Accent text color, typically used on highlighted elements.
    """
    TEXT_ACCENT = "#fff"

    """
    @var ERROR
    Color used to indicate error states or messages.
    """
    ERROR = "#ff5555"

    """
    @var WARNING
    Color used to indicate warnings or caution.
    """
    WARNING = "#f1c40f"

    """
    @var SUCCESS
    Color used to indicate success or confirmation states.
    """
    SUCCESS = "#33ff99"

    """
    @var ACCORDION_HEADER_BG
    Background color of accordion header buttons.
    """
    ACCORDION_HEADER_BG = "#283346"

    """
    @var ACCORDION_HEADER_TEXT
    Text color of accordion header buttons.
    """
    ACCORDION_HEADER_TEXT = "#e0eafc"

    """
    @var ACCORDION_HEADER_ACCENT
    Accent background color when accordion header is active or selected.
    """
    ACCORDION_HEADER_ACCENT = "#3a9dda"

    """
    @var BTN_UPDATE_BACKGROUND
    Background color for update buttons.
    """
    BTN_UPDATE_BACKGROUND = "#28a745"

    """
    @var BTN_UPDATE_TEXT
    Text color for update buttons.
    """
    BTN_UPDATE_TEXT = "#FFFFFF"


class DarkModeGUI(GeneralGUIPalette):
    """
    @brief Provides dark mode QPalette for the application.
    """
    @staticmethod
    def get_palette():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(DarkModeGUI.PRIMARY_BG))
        palette.setColor(QPalette.ColorRole.Base, QColor(DarkModeGUI.SECONDARY_BG))
        palette.setColor(QPalette.ColorRole.Text, QColor(DarkModeGUI.TEXT_MAIN))
        palette.setColor(QPalette.ColorRole.Button, QColor(DarkModeGUI.PRIMARY_BG))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#5f1717"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(DarkModeGUI.ACCENT))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(DarkModeGUI.GROUPBOX_BORDER))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
        return palette


class LightModeGUI(GeneralGUIPalette):
    """
    @brief Provides light mode QPalette for the application.
    """
    @staticmethod
    def get_palette():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d7"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
        return palette

class Pantone(GeneralGUIPalette):

    ACCORDION_HEADER_STYLE = f"""
        QToolButton {{
            background-color: {GeneralGUIPalette.ACCORDION_HEADER_BG};
            color: {GeneralGUIPalette.ACCORDION_HEADER_TEXT};
            font-size: 13pt;
            font-weight: bold;
            border: none;
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
            text-align: left;
            width: 100%;
        }}
        QToolButton:checked {{
            background-color: {GeneralGUIPalette.ACCORDION_HEADER_ACCENT};
            color: #fff;
        }}
    """    

    BUTTON_STYLE = """
    QPushButton {
        background-color: #2d2d30;
        color: #ffffff;
        font-size: 12pt;
        padding: 8px 12px;
        text-align: left;
        border: 1px solid #3a3a3d;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #3c3f41;
    }
    QPushButton:pressed {
        background-color: #007acc;
        color: #ffffff;
    }
    """
    COMMON_BUTTON_STYLE = """
            QPushButton {
                background-color: #6A9955;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4e7d44;
            }
        """    

    CHECKBOX_STYLE = f"""
        QCheckBox {{
            color: {GeneralGUIPalette.TEXT_MAIN};
            font-size: 11pt;
            padding: 4px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {GeneralGUIPalette.ACCENT};
            border: 1px solid {GeneralGUIPalette.HIGHLIGHT};
        }}
    """

    COMBO_STYLE = f"""
        QComboBox {{
            background-color: {GeneralGUIPalette.SECONDARY_BG};
            color: {GeneralGUIPalette.TEXT_MAIN};
            border: 1px solid {GeneralGUIPalette.GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
            padding: 4px 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {GeneralGUIPalette.SECONDARY_BG};
            color: {GeneralGUIPalette.TEXT_MAIN};
            selection-background-color: {GeneralGUIPalette.ACCENT};
            selection-color: {GeneralGUIPalette.TEXT_ACCENT};
        }}
        QComboBox:disabled {{
            background-color: #222;
            color: #888;
        }}
    """

    DIALOG_STYLE = """
    QLabel {
        color: #d4d4d4;
        font-size: 11pt;
    }
    QPushButton {
        background-color: #3a9dda;
        color: #fff;
        border-radius: 8px;
        font-size: 11pt;
        padding: 6px 12px;
    }
    QDialog {
        background-color: #23272e;
    }
"""

    DIALOG_TITLE_STYLE = """
    QLabel {
        color: #ffffff;
        font-size: 16pt;
        font-weight: bold;
        padding: 12px;
    }
    """

    GROUPBOX_STYLE = f"""
        QGroupBox {{
            background-color: {GeneralGUIPalette.PRIMARY_BG};
            border: 1.5px solid {GeneralGUIPalette.GROUPBOX_BORDER};
            border-radius: 8px;
            color: {GeneralGUIPalette.TEXT_MAIN};
            margin-top: 10px;
            font-weight: bold;
            font-size: 12pt;
            padding: 8px;
        }}
        QGroupBox:title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px 0 3px;
        }}
        QLabel {{
            color: {GeneralGUIPalette.TEXT_MAIN};
            font-size: 11pt;
        }}
    """

    LABEL_STYLE = f"""
        QLabel {{
            color: {GeneralGUIPalette.TEXT_MAIN};
            font-size: 11pt;
        }}
    """    

    LABEL_TITLE_STYLE = f"""
        QLabel {{
            color: {GeneralGUIPalette.TEXT_MAIN};
            font-size: 11pt;
            font-weight: bold;
        }}
    """    

    LINEEDIT_STYLE = f"""
        QLineEdit {{
            background-color: {GeneralGUIPalette.SECONDARY_BG};
            color: {GeneralGUIPalette.TEXT_MAIN};
            border: 1px solid {GeneralGUIPalette.GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
            padding: 4px 8px;
        }}
        QLineEdit:disabled {{
            background-color: #222;
            color: #888;
        }}
    """

    LISTWIDGET_STYLE = f"""
        QListWidget {{
            background-color: {GeneralGUIPalette.SECONDARY_BG};
            color: {GeneralGUIPalette.TEXT_MAIN};
            border: 1px solid {GeneralGUIPalette.GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
        }}
        QListWidget::item:selected {{
            background-color: {GeneralGUIPalette.ACCENT};
            color: {GeneralGUIPalette.TEXT_ACCENT};
        }}
        QListWidget::item {{
            margin-bottom: 7px;
            padding: 5px;
            border: 1px inset {GeneralGUIPalette.SECONDARY_BG};
            border-radius: 5px;
            text-align: center;
        }}
    """

    MENUBAR_QLABEL = """
                QLabel {
                    background-color: #2c2c2c;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 6px;
                    border-top: 1px solid #555;
                    border-bottom: 1px solid #555;
                }
            """   

    MENU_BAR = """
            QMenuBar {
                background-color: #23272e;
                color: #d4d4d4;
                font-size: 12pt;
                font-weight: bold;
                border: none;
            }
            QMenuBar::item {
                background: transparent;
                color: #d4d4d4;
                padding: 6px 14px;
            }
            QMenuBar::item:selected {
                background: #333842;
                color: #61dafb;
                border-radius: 5px;
            }
            QMenuBar::item:pressed {
                background: #22262d;
                color: #3a9dda;
            }
            QMenu {
                background-color: #23272e;
                color: #d4d4d4;
                font-size: 11pt;
                border: 1.5px solid #2a2d2e;
                border-radius: 6px;
            }
            QMenu::item {
                background: transparent;
                color: #d4d4d4;
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #3a9dda;
                color: #fff;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 2px;
                background: #333842;
                margin-left: 6px;
                margin-right: 6px;
            }
        """

    QMESSAGE_BOX = """
            QMessageBox {
                background-color: #2e2e2e;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 10pt;
            }
            QMessageBox QPushButton {
                background-color: #444;
                color: white;
                padding: 6px 14px;
                border-radius: 6px;
            }
            QMessageBox QPushButton:hover {
                background-color: #555;
            }
        """

    SPINBOX_STYLE = """
        QSpinBox {
            background-color: #2a2d2e;
            color: #d4d4d4;
            border: 1px solid #444;
            border-radius: 5px;
            font-size: 11pt;
            padding: 4px 8px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background: #23272e;
            subcontrol-origin: border;
            border-radius: 2px;
            width: 16px;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 10px;
            height: 10px;
        }
        QSpinBox:disabled {
            background-color: #222;
            color: #888;
        }
    """

    TEXTAREA_STYLE = """
        QTextEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #3c3c3c;
            padding: 4px;
            font-size: 16px;
            border-radius: 6px;
        }
    """

    UPDATE_YAML_BTN_STYLE = f"""
    QPushButton {{
        font-weight: bold;
        padding: 6px 18px;
        background: {GeneralGUIPalette.BTN_UPDATE_BACKGROUND};
        color: {GeneralGUIPalette.BTN_UPDATE_TEXT};
        border-radius: 8px;
        font-size: 12pt;
        border: none;
        margin-top: 10px;
        width: 200px;
        }}
    QPushButton:hover {{
        background-color: #218838;  /* Un po' più scuro */
    }}        
    """
