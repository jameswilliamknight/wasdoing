"""Configuration management for the work documentation system"""

import os
from pathlib import Path
import toml
from typing import Optional, List
from dataclasses import dataclass, asdict

DEFAULT_CONFIG = {
    "active_context": None,
    "contexts": [],
    "default_output": "work_doc.md",
    "watch_interval": 1.0,
    "config_dir": None,
}


@dataclass
class Config:
    """Configuration class for Was Doing"""
    active_context: Optional[str]
    contexts: List[str]
    default_output: str
    watch_interval: float
    config_dir: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create Config from dictionary"""
        return cls(
            active_context=data.get("active_context"),
            contexts=data.get("contexts", []),
            default_output=data.get("default_output", "work_doc.md"),
            watch_interval=data.get("watch_interval", 1.0),
            config_dir=data.get("config_dir")
        )

    def to_dict(self) -> dict:
        """Convert Config to dictionary"""
        return {
            "active_context": self.active_context,
            "contexts": self.contexts,
            "default_output": self.default_output,
            "watch_interval": self.watch_interval,
            "config_dir": self.config_dir,
        }


def ensure_setup() -> Optional[str]:
    """
    Check if Was Doing is properly set up.
    Returns an error message if setup is needed, None if everything is good.
    """
    config_file = Path.home() / ".wasdoing" / "config"

    if not config_file.exists():
        return "Was Doing needs to be set up. Run with --setup to configure."

    config_path = config_file.read_text().strip()
    config_toml = Path(config_path) / "config.toml"

    if not config_toml.exists():
        return f"Configuration file not found at {config_toml}. Run with --setup to reconfigure."

    return None


def get_config_dir() -> Path:
    """Get the configuration directory path"""
    return Path.home() / ".wasdoing"


def get_config_path() -> Optional[Path]:
    """Get the configuration file path if it exists"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.toml"
    return config_file if config_file.exists() else None


def load_config() -> Config:
    """Load configuration from file"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.toml"

    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)

    if not config_file.exists():
        config = Config.from_dict(DEFAULT_CONFIG)
        save_config(config)
        return config

    try:
        data = toml.load(config_file)
        return Config.from_dict(data)
    except Exception:
        # If config is corrupted, create a new one
        config = Config.from_dict(DEFAULT_CONFIG)
        save_config(config)
        return config


def save_config(config: Config) -> None:
    """Save configuration to file"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.toml"
    with open(config_file, "w") as f:
        toml.dump(asdict(config), f)


def get_active_context() -> Optional[str]:
    """Get the currently active context"""
    config = load_config()
    return config.active_context


def set_active_context(context: str) -> bool:
    """Set the active context"""
    config = load_config()
    if context not in config.contexts:
        return False

    config.active_context = context
    save_config(config)
    return True


def list_contexts() -> List[str]:
    """List all available contexts"""
    config = load_config()
    return config.contexts


def create_context(name: str) -> bool:
    """Create a new context"""
    # Allow alphanumeric, hyphens, and underscores
    if not all(c.isalnum() or c in '-_' for c in name):
        return False

    try:
        # Ensure config directory exists
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        tasks_dir = config_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        # Load or create config
        config = load_config()
        if name in config.contexts:
            return False

        # Add to contexts list
        config.contexts.append(name)
        save_config(config)
        return True
    except Exception as e:
        print(f"Error creating context: {e}")  # For debugging
        return False


def delete_context(name: str) -> bool:
    """Delete a context and its associated database.

    Args:
        name: Name of the context to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Delete the context's database file
        config_path = get_config_dir()
        db_path = config_path / "tasks" / f"{name}.db"
        db_path.unlink(missing_ok=True)

        # Remove from contexts list
        config = load_config()
        if name not in config.contexts:
            return False

        config.contexts.remove(name)
        if config.active_context == name:
            config.active_context = None
        save_config(config)
        return True
    except Exception as e:
        print(f"Error deleting context: {e}")  # For debugging
        return False
