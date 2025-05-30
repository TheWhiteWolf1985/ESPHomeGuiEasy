# esphomeGuieasy - GUI editor for ESPHome
# Copyright (c) 2025 Juri
#
# Released under AGPLv3 - Non-commercial use only.
# See LICENSE file for details.

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
