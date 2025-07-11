class Pantone:
    """
    Palette centralizzata per tutti i colori principali e gli stili CSS della GUI.
    """
    PRIMARY_BG = "#23272e"
    SECONDARY_BG = "#1e1e1e"
    ACCENT = "#3a9dda"
    HIGHLIGHT = "#61dafb"
    GROUPBOX_BG = "#23272e"
    GROUPBOX_BORDER = "#2a2d2e"
    TEXT_MAIN = "#d4d4d4"
    TEXT_ACCENT = "#fff"
    ERROR = "#ff5555"
    WARNING = "#f1c40f"
    SUCCESS = "#33ff99"
    ACCORDION_HEADER_BG = "#283346"
    ACCORDION_HEADER_TEXT = "#e0eafc"
    ACCORDION_HEADER_ACCENT = "#3a9dda"
    BTN_UPDATE_BACKGROUND = "#28a745"
    BTN_UPDATE_TEXT = "#FFFFFF"    


    GROUPBOX_STYLE = f"""
        QGroupBox {{
            background-color: {PRIMARY_BG};
            border: 1.5px solid {GROUPBOX_BORDER};
            border-radius: 8px;
            color: {TEXT_MAIN};
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
            color: {TEXT_MAIN};
            font-size: 11pt;
        }}
    """

    LINEEDIT_STYLE = f"""
        QLineEdit {{
            background-color: {SECONDARY_BG};
            color: {TEXT_MAIN};
            border: 1px solid {GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
            padding: 4px 8px;
        }}
        QLineEdit:disabled {{
            background-color: #222;
            color: #888;
        }}
    """

    COMBO_STYLE = f"""
        QComboBox {{
            background-color: {SECONDARY_BG};
            color: {TEXT_MAIN};
            border: 1px solid {GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
            padding: 4px 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {SECONDARY_BG};
            color: {TEXT_MAIN};
            selection-background-color: {ACCENT};
            selection-color: {TEXT_ACCENT};
        }}
        QComboBox:disabled {{
            background-color: #222;
            color: #888;
        }}
    """

    CHECKBOX_STYLE = f"""
        QCheckBox {{
            color: {TEXT_MAIN};
            font-size: 11pt;
            padding: 4px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1px solid {HIGHLIGHT};
        }}
    """

    ACCORDION_HEADER_STYLE = f"""
        QToolButton {{
            background-color: {ACCORDION_HEADER_BG};
            color: {ACCORDION_HEADER_TEXT};
            font-size: 13pt;
            font-weight: bold;
            border: none;
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
            text-align: left;
            width: 100%;
        }}
        QToolButton:checked {{
            background-color: {ACCORDION_HEADER_ACCENT};
            color: #fff;
        }}
    """    

    LABEL_STYLE = f"""
        QLabel {{
            color: {TEXT_MAIN};
            font-size: 11pt;
        }}
    """    

    LABEL_TITLE_STYLE = f"""
        QLabel {{
            color: {TEXT_MAIN};
            font-size: 11pt;
            font-weight: bold;
        }}
    """    

    UPDATE_YAML_BTN_STYLE = f"""
    QPushButton {{
        font-weight: bold;
        padding: 6px 18px;
        background: {BTN_UPDATE_BACKGROUND};
        color: {BTN_UPDATE_TEXT};
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

    ACCORDION_QTOOLBUTTON = """
            QToolButton {
                background-color: #23272e;
                color: #d4d4d4;
                font-size: 12pt;
                font-weight: bold;
                border: none;
                padding: 8px;
                text-align: left;
            }
            QToolButton:checked {
                background-color: #3a9dda;
                color: #fff;
            }
        """
    
    LISTWIDGET_STYLE = f"""
        QListWidget {{
            background-color: {SECONDARY_BG};
            color: {TEXT_MAIN};
            border: 1px solid {GROUPBOX_BORDER};
            border-radius: 5px;
            font-size: 11pt;
        }}
        QListWidget::item:selected {{
            background-color: {ACCENT};
            color: {TEXT_ACCENT};
        }}
        QListWidget::item {{
            margin-bottom: 7px;
            padding: 5px;
            border: 1px inset {SECONDARY_BG};
            border-radius: 5px;
            text-align: center;
        }}
    """

    DIALOG_TITLE_STYLE = """
    QLabel {
        color: #ffffff;
        font-size: 16pt;
        font-weight: bold;
        padding: 12px;
    }
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

    BUTTON_STYLE_GREEN =  f"""
            QPushButton {{
                font-weight: bold;
                padding: 5px 6px;
                background: {BTN_UPDATE_BACKGROUND};
                color: {BTN_UPDATE_TEXT};
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
    
    TAB_WIDGET = """
            QTabWidget::pane { border: none;}
            QTabBar::tab:selected { background: #23272e; color: #61dafb; }
            QTabBar::tab { background: #1e1e1e; color: #d4d4d4; font-size: 12pt; border-radius: 8px; padding: 8px 16px;}
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

