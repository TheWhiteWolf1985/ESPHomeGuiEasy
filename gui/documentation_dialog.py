from __future__ import annotations
import os, json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from core.translator import Translator
from gui.color_pantone import Pantone


class DocumentationDialog(QDialog):
    """Mostra un file HTML locale (o un URL remoto) in un QWebEngineView."""
    def __init__(self, start_page: str | QUrl, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(Translator.tr("menu_documentation"))
        self.setFixedSize(960, 700)
        self.setStyleSheet(Pantone.DIALOG_STYLE)

        vbox = QVBoxLayout(self)

        self.web = QWebEngineView()
        if isinstance(start_page, QUrl):
            url = start_page
        else:
            url = QUrl.fromLocalFile(os.path.abspath(start_page)) \
                  if os.path.exists(start_page) else QUrl(start_page)
        self.web.setUrl(url)

        def _hide_inner_scrollbars():
            css = """
                /* nasconde eventuali barre interne */
                ::-webkit-scrollbar { display: none !important; }
            """
            js = (
                "let s=document.createElement('style');"
                f"s.textContent=`{css}`;"
                "document.head.appendChild(s);"
            )
            self.web.page().runJavaScript(js)

        # inietta il CSS appena la pagina è caricata
        self.web.loadFinished.connect(lambda ok: ok and _hide_inner_scrollbars())

        vbox.addWidget(self.web)

        btn = QPushButton(Translator.tr("close"))
        btn.clicked.connect(self.accept)
        vbox.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)



