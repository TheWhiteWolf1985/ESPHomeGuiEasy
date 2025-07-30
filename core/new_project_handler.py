# -*- coding: utf-8 -*-
"""
@file new_project_handler.py
@brief Creates and initializes new ESPHome projects with predefined structure and metadata.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

This file contains the logic to:
- Generate a new project folder and optional subfolders
- Create initial `project.yaml` and `info.json` files
- Populate the editor with initial YAML
- Link with logger, compiler, and UI callbacks

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from config.GUIconfig import CATEGORY_TO_FOLDER
from core.translator import Translator
from datetime import datetime

def create_new_project(data: dict, yaml_editor, logger, compiler, reset_tabs_callback, update_recent_callback):
    """
    @brief Creates a new project folder structure and updates the main GUI interface accordingly.

    @param data Dictionary with input values from the project creation dialog.
    @param yaml_editor Reference to the YAML editor widget to populate initial content.
    @param logger Logging function or object with .log(msg, level) method.
    @param compiler Object with set_project_dir(path) method.
    @param reset_tabs_callback Function to reset UI tabs.
    @param update_recent_callback Function to update the list of recent files.
    @return Tuple (project_dir, yaml_path) if successful, or (None, None) on error.
    """
    nome_proj = data["name"].strip()
    root_dir = Path(data["base_dir"]).expanduser()
    categoria_raw = data.get("category", "Other / Misc").strip()
    categoria = CATEGORY_TO_FOLDER.get(categoria_raw, "Other_Misc")
    project_dir = root_dir / categoria / nome_proj


    if project_dir.exists():
        QMessageBox.warning(None, Translator.tr("warning"), Translator.tr("dir_exists"))
        return None, None

    try:
        project_dir.mkdir(parents=True)
        if data["create_subfolders"]:
            (project_dir / "yaml").mkdir()
            (project_dir / "logs").mkdir()
            (project_dir / "assets").mkdir()
    except Exception as e:
        QMessageBox.critical(None, Translator.tr("error"), Translator.tr("create_dir_error").format(e=e))
        return None, None

    yaml_path = project_dir / f"{nome_proj}.yaml"

    # === Generazione contenuto YAML compilato ===
    try:
        yaml_content = f"""esphome:
  name: {nome_proj}
  friendly_name: {nome_proj.replace("_", " ").title()}

esp32:
  board: esp32dev
  framework:
    type: arduino

logger:

api:

ota:

wifi:
  ssid: "your_wifi"
  password: "your_password"

captive_portal:
"""
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
    except Exception as e:
        QMessageBox.critical(None, Translator.tr("error"), Translator.tr("yaml_write_error").format(error=e))
        return None, None

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            yaml_editor.setPlainText(f.read())
    except Exception as e:
        QMessageBox.critical(None, Translator.tr("error"), Translator.tr("yaml_open_error").format(error=e))
        return None, None

    logger.log(Translator.tr("new_project_created").format(project_dir=project_dir), "success")

    reset_tabs_callback()
    compiler.set_project_dir(str(project_dir))
    update_recent_callback()

    info = {
        "name": data["name"],
        "author": data.get("author", "Unknown"),
        "version": data.get("version", "1.0"),
        "update": datetime.today().strftime("%Y-%m-%d"),
        "category": data.get("category", "Other / Misc"),
        "description": data.get("description", ""),
        "changelog": []  # ✅ aggiunto per supporto incrementale
    }

    info_path = project_dir / "info.json"
    try:
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.log(Translator.tr("infojson_error").format(error=e), "error")

    return str(project_dir), str(yaml_path)

