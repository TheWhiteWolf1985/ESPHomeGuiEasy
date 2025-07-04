import requests
import zipfile
import io
import os
import json
import config.GUIconfig as config
from core.log_handler import GeneralLogHandler


class GitHubHandler:
    """
    @class GitHubHandler
    @brief Gestisce il download e parsing dei progetti ESPHome dalla repo GitHub della community.
    """

    @staticmethod
    def fetch_project_metadata_list():
        """
        @brief Scarica solo i file info.json da ogni progetto ZIP presente nella cartella GitHub.
        @return Lista di dict con metadata progetto (Name, Version, Author, Update, category)
        """
        url = f"https://api.github.com/repos/{config.REPO_OWNER}/{config.REPO_NAME}/contents/{config.PROJECTS_PATH}"
        try:
            resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
            resp.raise_for_status()
            entries = resp.json()

            projects = []
            for entry in entries:
                if entry["type"] == "dir":
                    info_url = f"https://raw.githubusercontent.com/{config.REPO_OWNER}/{config.REPO_NAME}/main/{config.PROJECTS_PATH}/{entry['name']}/info.json"
                    try:
                        info_resp = requests.get(info_url)
                        info_resp.raise_for_status()
                        info_json = info_resp.json()
                        projects.append(info_json)
                    except Exception as parse_err:
                        GeneralLogHandler().error(f"Errore caricamento info.json per {entry['name']}: {parse_err}")


            return projects

        except Exception as e:
            GeneralLogHandler().error(f"Errore nel recupero dei metadati da GitHub: {e}")
            return []

    @staticmethod
    def fetch_projects_from_github():
        """
        @brief Scarica tutti i progetti ZIP dalla repo GitHub ufficiale e ne estrae info e yaml.
        @return Lista di dict: [{"info": info_dict, "yaml": yaml_string}, ...]
        """
        url = f"https://api.github.com/repos/{config.REPO_OWNER}/{config.REPO_NAME}/contents/{config.PROJECTS_PATH}"
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
            GeneralLogHandler().error(f"Errore nel recupero dei progetti da GitHub: {e}")
            return []
        
    @staticmethod
    def download_project_to_folder(name: str, local_path: str):
        """
        @brief Scarica info.json e project.yaml in una cartella locale.
        @param name Nome del progetto (nome della cartella nel repo)
        @param local_path Percorso locale dove salvare i file
        """
        base = f"https://raw.githubusercontent.com/{config.REPO_OWNER}/{config.REPO_NAME}/main/{config.PROJECTS_PATH}/{name}"
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
            GeneralLogHandler().error(f"Errore durante il download del progetto '{name}': {e}")

