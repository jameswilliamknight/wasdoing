"""
Repository Module for Work Documentation System

This module implements the repository pattern for SQLite database operations.
It follows SOLID principles and provides a clean interface for data access.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Generator, List, Optional, Tuple

from rich.console import Console

console = Console()


class DatabaseError(Exception):
    """Base exception for database operations"""

    pass


class ConnectionError(DatabaseError):
    """Exception raised when database connection fails"""

    pass


class QueryError(DatabaseError):
    """Exception raised when a database query fails"""

    pass


@dataclass(frozen=True)
class Entry:
    """Immutable data structure for work log entries"""

    id: Optional[int]
    type: str
    content: str
    timestamp: datetime

    @classmethod
    def from_row(cls, row: Tuple) -> "Entry":
        """Create an Entry from a database row"""
        return cls(
            id=row[0],
            type=row[1],
            content=row[2],
            timestamp=datetime.fromisoformat(row[3]),
        )


class WorkLogRepository:
    """Repository for work log entries following the repository pattern"""

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """

    def __init__(self, db_path: Path):
        """Initialize the repository with a database path"""
        self.db_path = db_path
        self._ensure_db_exists()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.
        Ensures proper connection handling and cleanup.
        """
        try:
            conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            raise ConnectionError(f"Database connection failed: {str(e)}")
        finally:
            if "conn" in locals():
                conn.close()

    def _ensure_db_exists(self) -> None:
        """Initialize the database if it doesn't exist"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self.SCHEMA)
        except DatabaseError as e:
            console.print(f"[red]Failed to initialize database: {str(e)}[/red]")
            raise

    def add_entry(self, entry_type: str, content: str) -> Entry:
        """
        Add a new entry to the database.

        Args:
            entry_type: Type of entry ('history' or 'summary')
            content: Entry content text

        Returns:
            The created Entry object

        Raises:
            QueryError: If the database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Insert the new entry
                cursor.execute(
                    "INSERT INTO entries (type, content) VALUES (?, ?)",
                    (entry_type, content),
                )

                # Get the inserted entry
                entry_id = cursor.lastrowid
                cursor.execute(
                    "SELECT id, type, content, timestamp FROM entries WHERE id = ?",
                    (entry_id,),
                )
                row = cursor.fetchone()

                if not row:
                    raise QueryError("Failed to retrieve inserted entry")

                return Entry.from_row(row)

        except sqlite3.Error as e:
            raise QueryError(f"Failed to add entry: {str(e)}")

    def get_all_entries(self) -> List[Entry]:
        """
        Retrieve all entries from the database.

        Returns:
            List of Entry objects ordered by timestamp

        Raises:
            QueryError: If the database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, type, content, timestamp FROM entries ORDER BY timestamp"
                )
                return [Entry.from_row(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise QueryError(f"Failed to retrieve entries: {str(e)}")

    def get_entry_by_id(self, entry_id: int) -> Optional[Entry]:
        """
        Retrieve a specific entry by ID.

        Args:
            entry_id: The ID of the entry to retrieve

        Returns:
            Entry object if found, None otherwise

        Raises:
            QueryError: If the database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, type, content, timestamp FROM entries WHERE id = ?",
                    (entry_id,),
                )
                row = cursor.fetchone()
                return Entry.from_row(row) if row else None
        except sqlite3.Error as e:
            raise QueryError(f"Failed to retrieve entry {entry_id}: {str(e)}")

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry by ID.

        Args:
            entry_id: The ID of the entry to delete

        Returns:
            True if entry was deleted, False if not found

        Raises:
            QueryError: If the database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise QueryError(f"Failed to delete entry {entry_id}: {str(e)}")

    def update_entry(self, entry_id: int, content: str) -> Optional[Entry]:
        """
        Update an entry's content.

        Args:
            entry_id: The ID of the entry to update
            content: New content for the entry

        Returns:
            Updated Entry object if found, None otherwise

        Raises:
            QueryError: If the database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE entries SET content = ? WHERE id = ?", (content, entry_id)
                )
                if cursor.rowcount == 0:
                    return None
                return self.get_entry_by_id(entry_id)
        except sqlite3.Error as e:
            raise QueryError(f"Failed to update entry {entry_id}: {str(e)}")
