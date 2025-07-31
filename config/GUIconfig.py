# -*- coding: utf-8 -*-
"""
@file GUIconfig.py
@brief Contains global configuration constants for ESPHomeGUIeasy.

@defgroup config Configuration
@ingroup main
@brief Application constants, defaults, and paths.

Includes:
- Default paths (projects, builds, logs)
- GUI dimensions and layout constants
- Language map and application metadata
- GitHub repository links and updater settings

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os
import platform
from pathlib import Path

# === CONFIGURAZIONI SPECIFICHE PER SISTEMA OPERATIVO ===

class WindowsConfig:
    COMMUNITY_LOCAL_FOLDER = str(Path.home() / "Documents" / "ESPHomeGUIeasy" / "community_projects")
    DEFAULT_PROJECT_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "user_projects"
    DEFAULT_BUILD_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "build"
    LOCALAPPDATA_FOLDER = os.path.join(os.environ["LOCALAPPDATA"], "ESPHomeGUIeasy")
    os.makedirs(LOCALAPPDATA_FOLDER, exist_ok=True)
    USER_DB_PATH = os.path.join(LOCALAPPDATA_FOLDER, "user_config.db")
    LOG_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy"
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_PATH = LOG_DIR / "log.txt"
    MODULE_SCHEMA_PATH = str(Path(__file__).parent.parent / "config" / "modules_schema.json")

class MacOSConfig:
    COMMUNITY_LOCAL_FOLDER = str(Path.home() / "Documents" / "ESPHomeGUIeasy" / "community_projects")
    DEFAULT_PROJECT_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "user_projects"
    DEFAULT_BUILD_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "build"
    LOCALAPPDATA_FOLDER = str(Path.home() / "Library/Application Support" / "ESPHomeGUIeasy")
    os.makedirs(LOCALAPPDATA_FOLDER, exist_ok=True)
    USER_DB_PATH = os.path.join(LOCALAPPDATA_FOLDER, "user_config.db")
    LOG_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy"
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_PATH = LOG_DIR / "log.txt"
    MODULE_SCHEMA_PATH = str(Path(__file__).parent.parent / "config" / "modules_schema.json")

class LinuxConfig:
    COMMUNITY_LOCAL_FOLDER = str(Path.home() / "Documents" / "ESPHomeGUIeasy" / "community_projects")
    DEFAULT_PROJECT_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "user_projects"
    DEFAULT_BUILD_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "build"
    LOCALAPPDATA_FOLDER = str(Path.home() / ".config" / "ESPHomeGUIeasy")
    os.makedirs(LOCALAPPDATA_FOLDER, exist_ok=True)
    USER_DB_PATH = os.path.join(LOCALAPPDATA_FOLDER, "user_config.db")
    LOG_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy"
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_PATH = LOG_DIR / "log.txt"
    MODULE_SCHEMA_PATH = str(Path(__file__).parent.parent / "config" / "modules_schema.json")


def get_platform_config():
    try:
        from core.settings_db import get_setting  # Import locale per evitare ciclo
        detected_platform = get_setting("os_platform")
    except Exception:
        detected_platform = None

    if detected_platform:
        platform_normalized = detected_platform.lower()
    else:
        import platform
        platform_normalized = platform.system().lower()

    if platform_normalized == "windows":
        return WindowsConfig(), "windows"
    elif platform_normalized == "darwin" or platform_normalized == "macos":
        return MacOSConfig(), "macos"
    else:
        return LinuxConfig(), "linux"


conf, PLATFORM_ID = get_platform_config()

# === INFORMAZIONI SULL'APPLICAZIONE ===
class AppInfo:
    NAME = "ESPHomeGuiEasy"
    VERSION = "1.4.2"
    RELEASE_DATE = "2025-07-31"
    GITHUB_URL = "https://raw.githubusercontent.com/TheWhiteWolf1985/esphomeguieasy/main/latest_version.json"
    RELEASE_URL = "https://github.com/TheWhiteWolf1985/esphomeguieasy/releases"
    REPO_OWNER = "TheWhiteWolf1985"
    REPO_NAME = "esphomeguieasy-projects"

# === PERCORSI GLOBALI STATICI ===
class GlobalPaths:
    TEMPLATE_PROJECT_PATH = "config/default_template.yaml"
    SW_ICON_PATH = "assets/icon/esphomeguieasy_icon.png"
    SPLASH_IMAGE = "assets/background_image.png"
    DOCS_PATH = "docs/"
    ICON_PATH = "assets/icon/"
    PROJECT_PLACEHOLDER_IMG = "assets/project_placeholder.png"
    COMMUNITY_PROJECTS_PATH = "progetti"
    SENSORS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "sensors.json")
    ACTIONS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "actions.json")
    TRIGGERS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "triggers.json")
    CONDITIONS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "conditions.json")
    TIMERS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "timers.json")
    SCRIPTS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "scripts.json")
    BOARDS_JSON_PATH = str(Path(__file__).parent.parent / "config" / "boards.json")

# === DIMENSIONI INTERFACCIA UTENTE ===
class UIDimensions:
    MAIN_WINDOW_HEIGHT = 900
    MAIN_WINDOW_WIDTH = 1500
    MAIN_SPLITTER_LEFT_COLUMN = 750
    MAIN_SPLITTER_RIGHT_COLUMN = 750
    BLOCK_WIDTH = 250
    BLOCK_HEIGHT = 200
    BLOCK_COLLAPSED_HEIGHT = 40

# === INFORMAZIONI SUL SISTEMA ===
class SystemInfo:
    PLATFORM = platform.system()
    VERSION = platform.version()
    RELEASE = platform.release()
    ARCHITECTURE = platform.machine()

# === TIPO DI DISTRIBUZIONE/INSTALLAZIONE ===
class PackageInfo:
    TYPE = "installer"  # Possible values: "installer", "portable", "appimage", "dmg", "source"
    SOURCE = "GitHub"   # Or "local", "snap", "brew", etc.    

# === LINGUE E CATEGORIE ===
LANGUAGES = {
    "en": "English",
    "it": "Italiano",
    "es": "Español",
    "de": "Deutsch",
    "br": "Brasileiro",
    "pt": "Português"
}

CATEGORY_TO_FOLDER  = {
    "Home Monitoring": "Home_Monitoring",
    "Energy & Power": "Energy_Power",
    "Security & Alarm": "Security_Alarm",
    "Actuators & I/O": "Actuators_IO",
    "Communication": "Communication",
    "Automation Logic": "Automation_Logic",
    "Other / Misc": "Other_Misc"
}
