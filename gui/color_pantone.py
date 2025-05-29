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
    BTN_UPDATE_BACKGROUND = "#20c070"
    BTN_UPDATE_TEXT = "#131414"    


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
    UPDATE_YAML_BTN_STYLE = f"""
        font-weight: bold;
        padding: 6px 18px;
        background: {BTN_UPDATE_BACKGROUND};
        color: {BTN_UPDATE_TEXT};
        border-radius: 8px;
        font-size: 12pt;
        border: none;
        margin-top: 10px;
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

