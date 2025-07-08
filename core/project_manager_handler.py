# -*- coding: utf-8 -*-
"""
@file project_manager_handler.py
@brief Loads and parses metadata for locally saved ESPHome projects organized by category.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Scans subdirectories of DEFAULT_PROJECT_DIR and loads each project's `info.json`.  
Used to populate the Project Manager UI with cards and metadata.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import json
from pathlib import Path
from config.GUIconfig import DEFAULT_PROJECT_DIR


def load_local_projects() -> dict:
    """
    @brief Scans local project folders and returns a dictionary grouped by category.

    Each project includes its parsed `info.json` metadata and absolute path.

    @return dict {category_name: [project_info_dict, ...]}
    """

    result = {}
    if not DEFAULT_PROJECT_DIR.exists():
        return result

    for category_dir in DEFAULT_PROJECT_DIR.iterdir():
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        result[category_name] = []

        for project_dir in category_dir.iterdir():
            if not project_dir.is_dir():
                continue

            info_path = project_dir / "info.json"
            if info_path.exists():
                try:
                    with open(info_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data["__path"] = str(project_dir)
                    data["category"] = category_name
                    result[category_name].append(data)
                except Exception as e:
                    print(f"Errore caricando {info_path}: {e}")

    return result
