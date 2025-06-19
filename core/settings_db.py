import sqlite3
import os
import shutil
from config.GUIconfig import USER_DB_PATH

def get_user_db_path() -> str:
    """
    Restituisce il percorso utilizzabile per user_config.db (scrivibile).
    Se non esiste nella cartella APPDATA, copia quello in sola lettura da /core.
    """
    appdata_path = os.path.join(os.environ["APPDATA"], "ESPHomeGUIeasy")
    os.makedirs(appdata_path, exist_ok=True)

    user_db_path = os.path.join(appdata_path, "user_config.db")
    local_db_path = os.path.join(os.path.dirname(__file__), "user_config.db")

    if not os.path.exists(user_db_path) and os.path.exists(local_db_path):
        try:
            shutil.copy(local_db_path, user_db_path)
        except Exception as e:
            print(f"[ERRORE] Impossibile copiare user_config.db: {e}")
    return user_db_path


def init_db():
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recent_files (
            path TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def set_setting(key: str, value: str):
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str) -> str | None:
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_recent_file(path: str):
    filename = os.path.basename(path)
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recent_files (path, filename, last_opened)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(path) DO UPDATE SET last_opened=CURRENT_TIMESTAMP, filename=excluded.filename
    """, (path, filename))
    conn.commit()
    conn.close()



def get_recent_files(limit: int = 4) -> list[tuple[str, str]]:
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        SELECT path, filename FROM recent_files
        ORDER BY last_opened DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


