# Owner: Person 2
# Purpose: SQLite database initialization and schema setup
# TODO(person2): Add sqlite-vec extension loading and migration engine

import sqlite3
from typing import Any

from backend.app.core.config import settings
from backend.app.core.logging import logger


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to SQLite with row factory."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables: tasks, activity_log (with provider column), permissions, settings."""
    logger.info("Initializing SQLite database tables at %s", settings.db_path)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            agent TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id TEXT PRIMARY KEY,
            action_type TEXT NOT NULL,
            params TEXT NOT NULL,
            agent TEXT NOT NULL,
            provider TEXT NOT NULL,
            status TEXT NOT NULL,
            undo_payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS permissions (
            action_type TEXT PRIMARY KEY,
            policy TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


def query_all(query: str, args: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Helper to execute read queries and return list of dicts."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
