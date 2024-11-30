"""
File System Watcher Module for Work Documentation System

This module provides real-time document generation through file system monitoring.
It follows the Observer pattern and provides robust error handling.
"""

# Standard library imports
from dataclasses import dataclass
from pathlib import Path
import sys
import time
from typing import Optional, List

# Third-party imports
from rich.console import Console
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# Local application imports
from repository import WorkLogRepository, DatabaseError
from markdown_handler import (
    DocumentGenerator,
    MarkdownGenerator,
    PDFGenerator,
    DefaultTemplate,
    DocumentError
)

# Initialize console with no clearing
console = Console(force_terminal=True, no_color=False, soft_wrap=True)


@dataclass
class WatcherConfig:
    """Configuration for database watcher"""
    db_path: Path
    output_paths: List[Path]
    check_interval: float = 1.0
    max_retries: int = 3
    retry_delay: float = 2.0


class WatcherError(Exception):
    """Base exception for watcher errors"""
    pass


class DatabaseWatcher:
    """Manages the file system observer for database changes"""

    def __init__(self, config: WatcherConfig):
        self.config = config
        self.observer = Observer()
        self.handler = DatabaseChangeHandler(config)

        # Schedule the observer
        self.observer.schedule(
            self.handler,
            str(config.db_path.parent),
            recursive=False
        )

    def start(self) -> None:
        """Start watching the database file"""
        try:
            self.observer.start()
            console.print(f"👀 Watching {self.config.db_path} for changes...")
            console.print("Press Ctrl+C to stop")
        except Exception as e:
            raise WatcherError(f"Failed to start watcher: {str(e)}")

    def stop(self) -> None:
        """Stop watching the database file"""
        try:
            self.observer.stop()
            self.observer.join()
            console.print("\n🛑 Stopping watch mode...")
        except Exception as e:
            raise WatcherError(f"Failed to stop watcher: {str(e)}")


class DatabaseChangeHandler(FileSystemEventHandler):
    """Handles database file changes and triggers document generation"""

    def __init__(self, config: WatcherConfig):
        """Initialize the handler with configuration"""
        self.config = config
        self.repo = WorkLogRepository(config.db_path)
        self.template = DefaultTemplate()
        self.generators = [
            (MarkdownGenerator(self.template), path)
            for path in config.output_paths
            if path.suffix == '.md'
        ] + [
            (PDFGenerator(self.template), path)
            for path in config.output_paths
            if path.suffix == '.pdf'
        ]

        # Initial generation
        self._safe_regenerate()

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events"""
        if not event.is_directory and Path(event.src_path) == self.config.db_path:
            console.print(f"🔄 Database changed, regenerating documents...")
            self._safe_regenerate()

    def _safe_regenerate(self) -> None:
        """Safely regenerate documents with retry logic"""
        try:
            self._regenerate_documents()
            self.retries = 0  # Reset retry counter on success
        except (DatabaseError, DocumentError) as e:
            self.retries += 1
            if self.retries >= self.config.max_retries:
                console.print(f"[red]❌ Failed to regenerate after {self.retries} attempts. Error: {str(e)}[/red]")
                return

            console.print(f"[yellow]⚠️ Regeneration failed, retrying in {self.config.retry_delay} seconds...[/yellow]")
            time.sleep(self.config.retry_delay)
            self._safe_regenerate()

    def _regenerate_documents(self) -> None:
        """Regenerate all configured document formats"""
        entries = self.repo.get_all_entries()

        for generator, output_path in self.generators:
            try:
                generator.generate(entries, output_path)
                console.print(f"📝 Generated {output_path.suffix[1:].upper()} file: {output_path}")
            except DocumentError as e:
                console.print(f"[red]❌ Failed to generate {output_path}: {str(e)}[/red]")


def watch_database(db_path: Path, output_paths: List[Path]) -> None:
    """
    Watch a database file and regenerate documents on changes

    Args:
        db_path: Path to the SQLite database
        output_paths: List of paths for output files (can mix .md and .pdf)
    """
    config = WatcherConfig(db_path=db_path, output_paths=output_paths)
    watcher = DatabaseWatcher(config)

    try:
        watcher.start()
        while True:
            time.sleep(config.check_interval)
    except KeyboardInterrupt:
        watcher.stop()
    except WatcherError as e:
        console.print(f"[red]❌ {str(e)}[/red]")
        sys.exit(1)
