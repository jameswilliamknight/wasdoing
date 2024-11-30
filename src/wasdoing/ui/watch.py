"""
Watch mode functionality for Was Doing

This module provides real-time document generation through file system monitoring.
"""

import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from ..worklog.repository import WorkLogRepository
from ..worklog.generator import MarkdownGenerator, DefaultTemplate

console = Console()


class DatabaseChangeHandler(FileSystemEventHandler):
    """Handles database file changes and triggers document generation"""

    def __init__(self, db_path: Path, output_path: Path):
        """Initialize the handler with paths"""
        self.db_path = db_path
        self.output_path = output_path
        self.repo = WorkLogRepository(db_path)
        self.generator = MarkdownGenerator(DefaultTemplate())

        # Initial generation
        self._regenerate()

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events"""
        if not event.is_directory and Path(event.src_path) == self.db_path:
            console.print("🔄 Database changed, regenerating document...")
            self._regenerate()

    def _regenerate(self) -> None:
        """Regenerate the markdown document"""
        try:
            entries = self.repo.get_all_entries()
            self.generator.generate(entries, self.output_path)
            console.print(f"📝 Generated markdown file: {self.output_path}")
        except Exception as e:
            console.print(f"[red]❌ Failed to regenerate: {str(e)}[/red]")


def watch_database(db_path: Path, output_path: Path) -> None:
    """
    Watch a database file and regenerate documents on changes

    Args:
        db_path: Path to the SQLite database
        output_path: Path for the output markdown file
    """
    observer = Observer()
    handler = DatabaseChangeHandler(db_path, output_path)

    # Schedule watching the database file's directory
    observer.schedule(handler, str(db_path.parent), recursive=False)

    try:
        observer.start()
        console.print(f"👀 Watching {db_path} for changes...")
        console.print("Press Ctrl+C to stop")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n🛑 Stopping watch mode...")
    except Exception as e:
        console.print(f"[red]❌ Watch error: {str(e)}[/red]")
        sys.exit(1)
    finally:
        observer.join()