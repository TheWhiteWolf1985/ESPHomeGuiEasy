# -*- coding: utf-8 -*-
"""
@file progress_dialog.py
@brief Simple modal dialog with a progress bar and label.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Implements a QDialog with a QLabel and QProgressBar to indicate task progress.
Supports determinate and indeterminate modes.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar

class ProgressDialog(QDialog):
    """
    @brief Modal dialog showing a progress bar and status label.

    Used to provide visual feedback during long-running operations.
    """
    def __init__(self, title="Operazione in corso...", label_text="Elaborazione file...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.setModal(True)
        self.setFixedWidth(400)
        self.progress_bar.setValue(0)

    def set_progress(self, value, maximum):
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def set_indeterminate(self):
        # Barra animata indeterminata (marquee)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
