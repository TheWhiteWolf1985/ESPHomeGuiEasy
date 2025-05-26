"""
@file log_handler.py
@brief Gestione dei log e console per esphomeGuieasy.

Contiene metodi per scrivere messaggi nella console con formattazione colorata.
"""

from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt6.QtWidgets import QTextEdit

class LOGHandler:
    """
    @class LOGHandler
    @brief Gestisce la stampa di messaggi nella console con stile VSCode.
    """

    def __init__(self, console_widget: QTextEdit):
        """
        @brief Costruttore del log handler
        @param console_widget Il widget QTextEdit della console
        """
        self.console = console_widget

    def log(self, text: str, msg_type="info"):
        """
        @brief Aggiunge testo formattato alla QTextEdit console.

        @param text           Testo da scrivere
        @param msg_type       Tipo di messaggio: info | warning | error | success
        """
        format = QTextCharFormat()
        color_map = {
            "info": "#d4d4d4",
            "warning": "#DCDCAA",
            "error": "#F44747",
            "success": "#6A9955"
        }

        format.setForeground(QColor(color_map.get(msg_type, "#d4d4d4")))

        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", format)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()
