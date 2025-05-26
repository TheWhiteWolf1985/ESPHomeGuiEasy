"""
@file log_handler.py
@brief Gestione dei log e console per esphomeGuieasy.

Contiene metodi per scrivere messaggi nella console con formattazione colorata.
"""

from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor

class LOGHandler:
    """
    @class LOGHandler
    @brief Gestisce la stampa di messaggi nella console con stile VSCode.
    """

    @staticmethod
    def append_to_console(console_widget, text, msg_type="info"):
        """
        @brief Aggiunge testo formattato alla QTextEdit console.

        @param console_widget QTextEdit su cui scrivere
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

        cursor = console_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", format)
        console_widget.setTextCursor(cursor)
        console_widget.ensureCursorVisible()
