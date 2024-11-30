"""Database operations for Was Doing."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from .config import get_config_dir, get_active_context

def get_db_path(context: Optional[str] = None) -> Path:
    """Get the database path for a context."""
    if context is None:
        context = get_active_context()
    return get_config_dir() / "tasks" / f"{context}.db"

def ensure_db_schema(db_path: Path) -> None:
    """Ensure the database has the correct schema."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_entry(content: str, entry_type: str = "history") -> None:
    """Add an entry to the active context's database.

    Args:
        content: The entry text
        entry_type: Type of entry (history or summary)
    """
    db_path = get_db_path()
    ensure_db_schema(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO entries (type, content, timestamp) VALUES (?, ?, ?)",
            (entry_type, content, datetime.now().isoformat())
        )
        conn.commit()

def get_entries(entry_type: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple[str, str, str]]:
    """Get entries from the active context's database.

    Args:
        entry_type: Optional filter by type (history or summary)
        limit: Optional limit on number of entries to return

    Returns:
        List of (content, type, timestamp) tuples
    """
    db_path = get_db_path()
    ensure_db_schema(db_path)

    with sqlite3.connect(db_path) as conn:
        query = "SELECT content, type, timestamp FROM entries"
        params = []

        if entry_type:
            query += " WHERE type = ?"
            params.append(entry_type)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        return conn.execute(query, params).fetchall()

def add_history_entry(content: str) -> None:
    """Add a history entry."""
    add_entry(content, "history")

def add_summary_entry(content: str) -> None:
    """Add a summary entry."""
    add_entry(content, "summary")

def get_history_entries(limit: Optional[int] = None) -> List[Tuple[str, str, str]]:
    """Get history entries."""
    return get_entries("history", limit)

def get_summary_entries(limit: Optional[int] = None) -> List[Tuple[str, str, str]]:
    """Get summary entries."""
    return get_entries("summary", limit)