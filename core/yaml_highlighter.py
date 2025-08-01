# -*- coding: utf-8 -*-
"""
@file yaml_highlighter.py
@brief Implements YAML syntax highlighting in the code editor.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Highlights keys, strings, numbers, booleans, null, lists, comments, and optional indentation  
using VS Code-like color scheme (for dark themes).

Built on top of QSyntaxHighlighter and regular expressions.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re

class YamlHighlighter(QSyntaxHighlighter):
    """
    @brief Provides syntax highlighting for YAML in a QTextDocument using VS Code dark theme colors.

    Supports detection and formatting of:
    - Keys
    - Strings
    - Numbers
    - Booleans
    - Null values
    - Lists
    - Comments
    - Indentation (optional)

    Uses QSyntaxHighlighter and regular expressions to parse each line of text.
    """
    def __init__(self, document):
        super().__init__(document)

        # Formati base
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#569CD6"))  # blu chiavi

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178"))  # rosso stringhe

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # verde numeri

        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#DCDCAA"))  # giallo booleani

        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("#808080"))  # grigio null

        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#9CDCFE"))  # celeste liste

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))  # verde commenti

        self.indent_format = QTextCharFormat()
        self.indent_format.setForeground(QColor("#404040"))  # grigio indentazione

        # Regole di evidenziazione (ordine conta!)
        self.rules = [
            (re.compile(r'^\s*[\w\-\.]+:'), self.key_format),  # chiavi
            (re.compile(r':\s*".*?"'), self.string_format),
            (re.compile(r":\s*\'.*?\'"), self.string_format),
            (re.compile(r":\s*\d+"), self.number_format),
            (re.compile(r":\s*(true|false)\b", re.IGNORECASE), self.boolean_format),
            (re.compile(r":\s*null\b", re.IGNORECASE), self.null_format),
            (re.compile(r'^\s*-\s.*'), self.list_format),  # liste
            (re.compile(r'#.*$'), self.comment_format)
        ]

    def highlightBlock(self, text):
        """
        @brief Called by Qt for each block of text. Applies highlighting rules.

        @param text The line of text being processed.
        """
        # Evidenzia indentazione (opzionale, solo spazi iniziali)
        match_indent = re.match(r'^(\s+)', text)
        if match_indent:
            start, end = match_indent.span(1)
            self.setFormat(start, end - start, self.indent_format)

        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
