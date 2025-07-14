# -*- coding: utf-8 -*-
"""
@file settings_db.py
@brief Provides functions to read and write user settings stored in a local SQLite database.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Handles:
- Initialization of the `settings` and `recent_files` tables
- Get/set operations for key-value pairs in user config
- Storage of recently opened projects with timestamps

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import sqlite3, os, traceback
from config.GUIconfig import conf
from core.log_handler import GeneralLogHandler

logger = GeneralLogHandler()

def init_db():
    """
    @brief Initializes the SQLite database if not already present.

    Creates `settings` and `recent_files` tables if they do not exist.
    Does not insert any default values.
    """
    conn = sqlite3.connect(conf.USER_DB_PATH)
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
    """
    @brief Sets or updates a configuration key-value pair in the settings table.

    @param key The name of the setting (e.g. "language").
    @param value The string value to store.
    """
    if key == "language":
        logger = GeneralLogHandler()
        logger.debug(f"set_setting('language', '{value}') chiamato da:\n{''.join(traceback.format_stack(limit=5))}")
    conn = sqlite3.connect(conf.USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str) -> str | None:
    """
    @brief Retrieves the value of a setting from the database.

    @param key The setting name to look up.
    @return The stored value, or None if not found or an error occurs.
    """
    try:
        conn = sqlite3.connect(conf.USER_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0].strip() if result and result[0].strip() else None
    except Exception:
        return None


def add_recent_file(path: str):
    """
    @brief Adds or updates a recently opened file in the `recent_files` table.

    @param path Absolute path to the YAML file.
    """
    filename = os.path.basename(path)
    conn = sqlite3.connect(conf.USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recent_files (path, filename, last_opened)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(path) DO UPDATE SET last_opened=CURRENT_TIMESTAMP, filename=excluded.filename
    """, (path, filename))
    conn.commit()
    conn.close()


def get_recent_files(limit: int = 4) -> list[tuple[str, str]]:
    """
    @brief Retrieves the most recently opened files from the database.

    @param limit Maximum number of entries to return.
    @return List of tuples (path, filename) ordered by last_opened descending.
    """
    conn = sqlite3.connect(conf.USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT path, filename FROM recent_files
        ORDER BY last_opened DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results
