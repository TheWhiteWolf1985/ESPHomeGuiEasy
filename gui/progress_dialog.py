from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar

class ProgressDialog(QDialog):
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
