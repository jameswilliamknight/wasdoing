"""Configuration management for Was Doing"""

from pathlib import Path
from typing import Optional, List
import toml

from ..worklog.context import (
    format_context_name,
    get_context_path,
    get_context_db_path,
    create_context_structure,
    load_context_config,
)

class Config:
    """Configuration class"""
    def __init__(
        self,
        active_context: Optional[str] = None,
        contexts: List[str] = None,
        default_output: str = "output.md",
        watch_interval: float = 1.0,
    ):
        self.active_context = active_context
        self.contexts = contexts or []
        self.default_output = default_output
        self.watch_interval = watch_interval

def get_config_path() -> Path:
    """Get the configuration directory path"""
    pointer = Path.home() / ".wwjd" / "config"
    if pointer.exists():
        return Path(pointer.read_text().strip())
    return Path.home() / ".wwjd" / "wasdoing"

def ensure_setup() -> Optional[str]:
    """Ensure configuration exists and is valid"""
    config_dir = get_config_path()

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create contexts directory
    contexts_dir = config_dir / "contexts"
    contexts_dir.mkdir(exist_ok=True)

    return None

def create_context(name: str) -> bool:
    """Create a new context"""
    config_dir = get_config_path()

    try:
        # Create context directory structure
        if not create_context_structure(config_dir, name):
            return False

        # Initialize empty database
        from ..worklog.repository import WorkLogRepository
        repo = WorkLogRepository(get_context_db_path(config_dir, name))
        return True
    except Exception:
        return False

def list_contexts() -> List[str]:
    """List all available contexts"""
    config_dir = get_config_path()
    contexts_dir = config_dir / "contexts"

    if not contexts_dir.exists():
        return []

    # Look for context directories that have a database.db file
    return [
        p.name for p in contexts_dir.iterdir()
        if p.is_dir() and (p / "database.db").exists()
    ]

def get_active_context() -> Optional[str]:
    """Get the currently active context"""
    config_dir = get_config_path()
    active_file = config_dir / "active_context"

    if not active_file.exists():
        return None

    return active_file.read_text().strip()

def set_active_context(name: str) -> bool:
    """Set the active context"""
    config_dir = get_config_path()
    context_dir = get_context_path(config_dir, name)

    if not context_dir.exists() or not (context_dir / "database.db").exists():
        return False

    active_file = config_dir / "active_context"
    active_file.write_text(name)
    return True

def delete_context(name: str) -> bool:
    """Delete an existing context"""
    config_dir = get_config_path()
    context_dir = get_context_path(config_dir, name)

    if not context_dir.exists():
        return False

    try:
        # If this is the active context, clear it
        active_context = get_active_context()
        if active_context == name:
            active_file = config_dir / "active_context"
            if active_file.exists():
                active_file.unlink()

        # Remove the context directory and all its contents
        import shutil
        shutil.rmtree(context_dir)
        return True
    except Exception:
        return False
