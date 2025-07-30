# -*- coding: utf-8 -*-
"""
@file log_handler.py
@brief Provides classes to handle log output both to a file and to a GUI console widget.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Implements two classes:
- LOGHandler: For colored HTML output to the console (e.g., QTextEdit)
- GeneralLogHandler: Singleton for logging to file and optionally to the GUI

Includes support for:
- Rotating file logging
- Colored log messages by level
- Exception logging with stack traces

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import logging, os,traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextCursor
from logging.handlers import RotatingFileHandler
from config.GUIconfig import conf

class LOGHandler:
    """
@brief Outputs messages to a QTextEdit widget, with color formatting per log level.

This class is mainly used to show logs in the GUI during runtime.  
If the GUI console is not available, logs fall back to standard output.
"""
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

class GeneralLogHandler:
    """
    @brief Singleton logger that writes to both file and GUI console (if available).

    Supports rotating file logging and colored HTML output to QTextEdit.  
    All logging levels (debug, info, warning, error) are available.
    """

    _instance = None

    def __new__(cls, console_widget=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger(console_widget)
        return cls._instance

    def _init_logger(self, console_widget=None):
        self._console = console_widget
        self._logger = logging.getLogger("ESPHomeGUIeasy")
        self._logger.setLevel(logging.DEBUG)

        # Aggiunge RotatingFileHandler se non presente
        if not any(isinstance(h, RotatingFileHandler) for h in self._logger.handlers):
            os.makedirs(os.path.dirname(conf.LOG_PATH), exist_ok=True)
            handler = RotatingFileHandler(
                conf.LOG_PATH,
                mode='a',
                maxBytes=20 * 1024 * 1024,  # 20 MB
                backupCount=2,
                encoding='utf-8'
            )
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            self._logger.addHandler(handler)

    @property
    def console(self):
        # Cerca un QTextEdit con attributo console_output
        for w in QApplication.topLevelWidgets():
            if hasattr(w, "console_output"):
                return w.console_output
        return self._console

    def log(self, message: str, level: str = "info"):
        # File logger
        if hasattr(self._logger, level.lower()):
            getattr(self._logger, level.lower())(message)
        else:
            self._logger.info(message)

        # GUI console logger
        console = self.console
        if console is not None:
            color = {
                "error": "#ff5555",
                "warning": "#f1c40f",
                "success": "#33ff99",
                "debug": "#8888ff",
                "info": "#d4d4d4"
            }.get(level.lower(), "#d4d4d4")
            html = f'<span style="color:{color};">[{level.upper()}]</span> {message}<br>'
            cursor = console.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            console.insertHtml(html)
            cursor.movePosition(QTextCursor.MoveOperation.End)

    def log_exception(self, context: str = "Errore sconosciuto"):
        """
        @brief Logs a full exception stack trace to the log file.

        @param context Optional string to describe where the exception occurred.
        """
        tb = traceback.format_exc()
        self._logger.error(f"{context}\n{tb}")         

    """
    @brief Logs a debug/info/warning/error/success message to the file and console.
    @param msg The message string to be logged.
    """
    def debug(self, msg: str):   self._logger.debug(msg)
    def info(self, msg: str):    self._logger.info(msg)
    def warning(self, msg: str): self._logger.warning(msg)
    def error(self, msg: str):   self._logger.error(msg)
    def success(self, msg: str): self._logger.info("[SUCCESS] " + msg)
