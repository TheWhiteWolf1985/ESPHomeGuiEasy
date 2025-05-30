from PyQt6.QtWidgets import QMenuBar, QFileDialog
from PyQt6.QtGui import QAction
from core.translator import Translator
from gui.color_pantone import Pantone

class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(Pantone.MENU_BAR)

        # --- FILE MENU ---
        file_menu = self.addMenu(Translator.tr("menu_file"))

        self.new_action = QAction(Translator.tr("new_project"), self)
        self.new_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_action)

        self.open_action = QAction(Translator.tr("open_project"), self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)

        self.save_action = QAction(Translator.tr("save_project"), self)
        self.save_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.save_action)

        self.saveas_action = QAction(Translator.tr("save_as"), self)
        self.saveas_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(self.saveas_action)

        file_menu.addSeparator()

        self.import_action = QAction(Translator.tr("import_yaml"), self)
        file_menu.addAction(self.import_action)

        self.export_action = QAction(Translator.tr("export_yaml"), self)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        self.exit_action = QAction(Translator.tr("exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(self.exit_action)

        self.settings_menu = self.addMenu(Translator.tr("menu_settings"))
        self.language_menu = self.settings_menu.addMenu(Translator.tr("menu_language"))
        self._build_language_menu()     

        self.current_language = Translator.current_language()

    def update_labels(self):
        # Aggiorna tutte le label dei menu e voci secondo la lingua attuale
        self.clear()  # Elimina tutti i menu per forzare la ricostruzione
        file_menu = self.addMenu(Translator.tr("menu_file"))
        self.new_action = QAction(Translator.tr("new_project"), self)
        self.open_action = QAction(Translator.tr("open_project"), self)
        self.save_action = QAction(Translator.tr("save_project"), self)
        self.saveas_action = QAction(Translator.tr("save_as"), self)
        self.import_action = QAction(Translator.tr("import_yaml"), self)
        self.export_action = QAction(Translator.tr("export_yaml"), self)
        self.exit_action = QAction(Translator.tr("exit"), self)
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.saveas_action)
        file_menu.addSeparator()
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Recreate settings menu
        self.settings_menu = self.addMenu(Translator.tr("menu_settings"))
        self.language_menu = self.settings_menu.addMenu(Translator.tr("menu_language"))
        self._build_language_menu()


    def _build_language_menu(self):
        self.language_menu.clear()
        from core.translator import Translator
        # Map: code → (emoji, display name)
        flag_map = {
            "it": "🇮🇹",
            "en": "🇬🇧",
            "de": "🇩🇪",
            "es": "🇪🇸"
        }
        name_map = {
            "it": "Italiano",
            "en": "English",
            "de": "Deutsch",
            "es": "Español"
        }
        current_lang = Translator.current_language()
        langs = Translator.get_available_languages()
        for code in langs:
            flag = flag_map.get(code, "")
            name = name_map.get(code, code.upper())
            text = f"{flag} {name}"
            action = QAction(text, self)
            action.setCheckable(True)
            action.setChecked(code == current_lang)
            # Bandierina a sinistra, spunta a destra
            action.setData(code)
            # Collegamento selezione lingua
            action.triggered.connect(lambda checked, c=code: self._set_language(c))
            self.language_menu.addAction(action)

    def _set_language(self, lang_code):
        from core.translator import Translator
        import json
        # Cambia la lingua
        Translator.load_language(lang_code)
        self.current_language = lang_code
        # Salva la preferenza su user_settings.json
        try:
            with open("user_settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            settings = {}
        settings["language"] = lang_code
        with open("user_settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f)
        # Aggiorna label e menu
        if hasattr(self.parent(), "aggiorna_tutte_le_label"):
            self.parent().aggiorna_tutte_le_label()
        self._build_language_menu()