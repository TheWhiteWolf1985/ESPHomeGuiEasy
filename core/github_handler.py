# -*- coding: utf-8 -*-
"""
@file github_handler.py
@brief Handles download and parsing of ESPHome community projects from the GitHub repository.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Provides static methods to:
- Fetch metadata (`info.json`) from community projects
- Download complete `.zip` packages from GitHub
- Save selected project files locally (info.json and project.yaml)

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import io, os, json, zipfile, requests
from config.GUIconfig import AppInfo, GlobalPaths
from core.log_handler import GeneralLogHandler
from core.translator import Translator

class GitHubHandler:
    """
    @brief Utility class to interact with the GitHub community projects repository.

    All methods are static and designed for quick access to remote files and metadata.
    """

    @staticmethod
    def fetch_project_metadata_list():
        """
        @brief Downloads only the `info.json` metadata files from each project directory in the GitHub repository.

        @return A list of dictionaries containing project metadata (name, version, author, update, category).
        """
        url = f"https://api.github.com/repos/{AppInfo.REPO_OWNER}/{AppInfo.REPO_NAME}/contents/{GlobalPaths.COMMUNITY_PROJECTS_PATH}"
        try:
            resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
            resp.raise_for_status()
            entries = resp.json()

            projects = []
            for entry in entries:
                if entry["type"] == "dir":
                    info_url = f"https://raw.githubusercontent.com/{AppInfo.REPO_OWNER}/{AppInfo.REPO_NAME}/main/{GlobalPaths.COMMUNITY_PROJECTS_PATH}/{entry['name']}/info.json"
                    try:
                        info_resp = requests.get(info_url)
                        info_resp.raise_for_status()
                        info_json = info_resp.json()
                        projects.append(info_json)
                    except Exception as parse_err:
                        GeneralLogHandler().error(
                            Translator.tr("github_info_json_error").format(project=entry['name'], error=parse_err)
                        )
            return projects

        except Exception as e:
            GeneralLogHandler().error(Translator.tr("github_metadata_error").format(error=e))
            return []

    @staticmethod
    def fetch_projects_from_github():
        """
        @brief Downloads all `.zip` projects from the GitHub repository and extracts metadata and YAML.

        @return A list of dictionaries: [{"info": info_dict, "yaml": yaml_string}, ...]
        """
        url = f"https://api.github.com/repos/{AppInfo.REPO_NAME}/{AppInfo.REPO_NAME}/contents/{GlobalPaths.COMMUNITY_PROJECTS_PATH}"
        try:
            resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
            resp.raise_for_status()
            entries = resp.json()

            projects = []
            for entry in entries:
                if entry["name"].endswith(".zip"):
                    zip_url = entry["download_url"]
                    zip_resp = requests.get(zip_url)
                    zf = zipfile.ZipFile(io.BytesIO(zip_resp.content))

                    info_json = json.loads(zf.read("info.json"))
                    yaml_content = zf.read("project.yaml").decode("utf-8")

                    projects.append({"info": info_json, "yaml": yaml_content})

            return projects

        except Exception as e:
            GeneralLogHandler().error(
                Translator.tr("github_projects_error").format(error=e)
            )
            return []
        
    @staticmethod
    def download_project_to_folder(name: str, local_path: str):
        """
        @brief Downloads the `info.json` and `project.yaml` files for a given project into a local folder.

        @param name The project folder name in the GitHub repo.
        @param local_path The local destination path where the files will be saved.
        """
        base = f"https://raw.githubusercontent.com/{AppInfo.REPO_NAME}/{AppInfo.REPO_NAME}/main/{GlobalPaths.COMMUNITY_PROJECTS_PATH}/{name}"
        try:
            os.makedirs(local_path, exist_ok=True)

            info_url = f"{base}/info.json"
            yaml_url = f"{base}/project.yaml"

            info_resp = requests.get(info_url)
            info_resp.raise_for_status()
            with open(os.path.join(local_path, "info.json"), "w", encoding="utf-8") as f:
                f.write(info_resp.text)

            yaml_resp = requests.get(yaml_url)
            yaml_resp.raise_for_status()
            with open(os.path.join(local_path, "project.yaml"), "w", encoding="utf-8") as f:
                f.write(yaml_resp.text)

        except Exception as e:
            GeneralLogHandler().error(
                Translator.tr("github_download_error").format(project=name, error=e)
            )


