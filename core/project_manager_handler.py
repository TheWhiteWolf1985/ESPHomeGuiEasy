import json
from pathlib import Path
from config.GUIconfig import DEFAULT_PROJECT_DIR


def load_local_projects() -> dict:
    """
    Scansiona tutte le sottocartelle di DEFAULT_PROJECT_DIR e restituisce
    un dizionario categoria -> lista progetti.

    Ogni progetto è un dizionario con i metadati letti da info.json + path.
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
