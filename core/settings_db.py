import sqlite3
import os
from config.GUIconfig import USER_DB_PATH
from core.log_handler import GeneralLogHandler
import traceback

logger = GeneralLogHandler()


def get_user_db_path() -> str:
    """
    Restituisce il percorso assoluto del file user_config.db in LOCALAPPDATA.
    Presume che il file sia già stato installato correttamente dal setup.
    """
    return USER_DB_PATH


def init_db():
    """
    Verifica che le tabelle settings e recent_files esistano.
    Non scrive alcun dato di default.
    """
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
    if key == "language":
        logger = GeneralLogHandler()
        logger.debug(f"set_setting('language', '{value}') chiamato da:\n{''.join(traceback.format_stack(limit=5))}")
    conn = sqlite3.connect(get_user_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str) -> str | None:
    try:
        conn = sqlite3.connect(get_user_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0].strip() if result and result[0].strip() else None
    except Exception:
        return None


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
