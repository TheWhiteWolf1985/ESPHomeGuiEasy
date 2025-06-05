from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextCursor

class LOGHandler:
    def __init__(self, console_widget=None):
        self._console = console_widget  # riferimento iniziale, ma non permanente

    @property
    def console(self):
        # Cerca un QTextEdit attivo con nome console_output
        for w in QApplication.topLevelWidgets():
            if hasattr(w, "console_output"):
                return w.console_output
        return self._console  # fallback se non troviamo nulla

    def log(self, message, level="info"):
        console = self.console
        if console is None:
            print(f"[{level.upper()}] {message}")
            return

        try:
            cursor = console.textCursor()
            if level == "error":
                color = "#ff5555"
            elif level == "warning":
                color = "#f1c40f"
            elif level == "success":
                color = "#33ff99"
            else:
                color = "#d4d4d4"

            html = f'<span style="color:{color};">[{level.upper()}]</span> {message}<br>'
            console.moveCursor(QTextCursor.MoveOperation.End)
            console.insertHtml(html)
            console.moveCursor(QTextCursor.MoveOperation.End)
        except RuntimeError:
            print(f"[LOGGER ERROR] QTextEdit distrutto. Messaggio:\n[{level.upper()}] {message}")