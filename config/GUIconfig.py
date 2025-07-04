import os
from pathlib import Path

COMMUNITY_LOCAL_FOLDER = str(Path.home() / "Documents" / "ESPHomeGUIeasy" / "community_projects")
DEFAULT_PROJECT_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "user_projects"
DEFAULT_BUILD_DIR = Path.home() / "Documents" / "ESPHomeGUIeasy" / "build"

CATEGORY_TO_FOLDER = {
    "Home Monitoring": "Home_Monitoring",
    "Energy & Power": "Energy_Power",
    "Security & Alarm": "Security_Alarm",
    "Actuators & I/O": "Actuators_IO",
    "Communication": "Communication",
    "Automation Logic": "Automation_Logic",
    "Other / Misc": "Other_Misc"
}

LOCALAPPDATA_FOLDER = os.path.join(os.environ["LOCALAPPDATA"], "ESPHomeGUIeasy")
os.makedirs(LOCALAPPDATA_FOLDER, exist_ok=True)

USER_DB_PATH = os.path.join(LOCALAPPDATA_FOLDER, "user_config.db")
LOG_PATH = str(Path.home() / "Documents" / "ESPHomeGUIeasy" / "log.txt")

APP_NAME = "ESPHomeGuiEasy"
SW_ICON_PATH = "assets/icon/esphomeguieasy_icon.png"
SPLASH_IMAGE = "assets/background_image.png"
YAML_TEMPLATE_PATH = "config/default_template.yaml"
DOCS_PATH = "docs/"
ICON_PATH = "assets/icon/"
PROJECT_PLACEHOLDER_IMG = "assets/project_placeholder.png"

APP_VERSION = "1.4.0"
APP_RELEASE_DATE = "2025-07-04"

GITHUB_URL = "https://raw.githubusercontent.com/TheWhiteWolf1985/esphomeguieasy/main/latest_version.json"
RELEASE_URL = "https://github.com/TheWhiteWolf1985/esphomeguieasy/releases"
REPO_OWNER = "TheWhiteWolf1985"
REPO_NAME = "esphomeguieasy-projects"
PROJECTS_PATH = "progetti"

# Dimensioni della finestra principale
MAIN_WINDOW_HEIGHT = 900
MAIN_WINDOW_WIDTH = 1500

#dimensioni iniziali dei due splitter (sx: canvas, console - dx: comandi, tab)
MAIN_SPLITTER_LEFT_COLUMN = 750
MAIN_SPLITTER_RIGHT_COLUMN = 750 

# Dimensioni dei blocchi nel canvas dei sensori
BLOCK_WIDTH = 250
BLOCK_HEIGHT = 200
BLOCK_COLLAPSED_HEIGHT = 40
