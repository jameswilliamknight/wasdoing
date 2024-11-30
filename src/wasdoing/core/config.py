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
}


@dataclass
class Config:
    """Configuration class for Was Doing"""
    active_context: Optional[str]
    contexts: List[str]
    default_output: str
    watch_interval: float

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create Config from dictionary"""
        return cls(
            active_context=data.get("active_context"),
            contexts=data.get("contexts", []),
            default_output=data.get("default_output", "work_doc.md"),
            watch_interval=data.get("watch_interval", 1.0),
        )

    def to_dict(self) -> dict:
        """Convert Config to dictionary"""
        return {
            "active_context": self.active_context,
            "contexts": self.contexts,
            "default_output": self.default_output,
            "watch_interval": self.watch_interval,
        }


def ensure_setup() -> Optional[str]:
    """
    Check if Was Doing is properly set up.
    Returns an error message if setup is needed, None if everything is good.
    """
    config_file = Path.home() / ".wwjd" / "config"

    if not config_file.exists():
        return "Was Doing needs to be set up first.\nRun: doc --setup"

    try:
        config_path = config_file.read_text().strip()
        config_toml = Path(config_path) / "config.toml"

        if not config_toml.exists():
            return f"Configuration not found at {config_toml}\nRun: doc --setup"

        return None
    except Exception as e:
        return f"Error reading configuration: {e}\nRun: doc --setup"


def _read_pointer_file() -> Optional[Path]:
    """Read the pointer file and return the config directory path"""
    pointer_file = Path.home() / ".wwjd" / "config"
    if pointer_file.exists():
        return Path(pointer_file.read_text().strip())
    return None


def get_config_path() -> Optional[Path]:
    """Get the configuration file path if it exists"""
    config_dir = _read_pointer_file()
    return config_dir if config_dir else None


def get_config_dir() -> Path:
    """Get the configuration directory path from the pointer file"""
    config_dir = _read_pointer_file()
    return config_dir if config_dir else Path.home() / ".wwjd"


def load_config() -> Config:
    """Load configuration from file"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.toml"

    try:
        if not config_file.exists():
            print(f"Creating new configuration at {config_file}")
            config = Config.from_dict(DEFAULT_CONFIG)
            save_config(config)
            return config

        try:
            data = toml.load(config_file)
            return Config.from_dict(data)
        except toml.TomlDecodeError:
            print(f"Warning: Corrupted config file at {config_file}, creating new one")
            config = Config.from_dict(DEFAULT_CONFIG)
            save_config(config)
            return config
        except Exception as e:
            print(f"Warning: Error loading config ({e}), creating new one")
            config = Config.from_dict(DEFAULT_CONFIG)
            save_config(config)
            return config

    except Exception as e:
        print(f"Critical error accessing config: {e}")
        raise


def save_config(config: Config, config_dir: Optional[Path] = None) -> None:
    """Save configuration to file"""
    if config_dir is None:
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
    if not context:  # Handle empty context name
        return False

    config = load_config()
    if context not in config.contexts:
        print(f"Context '{context}' does not exist")
        return False

    try:
        config.active_context = context
        save_config(config)
        return True
    except Exception as e:
        print(f"Error setting active context: {e}")
        return False


def list_contexts() -> List[str]:
    """List all available contexts"""
    config = load_config()
    return config.contexts


def validate_context_name(name: str) -> bool:
    """Validate a context name"""
    if not name:
        print("Context name cannot be empty")
        return False

    if len(name) > 64:  # Reasonable max length
        print("Context name too long (max 64 characters)")
        return False

    if not all(c.isalnum() or c in '-_' for c in name):
        print("Context name can only contain letters, numbers, hyphens and underscores")
        return False

    return True


def create_context(name: str) -> bool:
    """Create a new context"""
    if not validate_context_name(name):
        return False

    try:
        config_dir = get_config_dir()
        tasks_dir = config_dir / "tasks"

        try:
            tasks_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Permission denied creating directory: {tasks_dir}")
            return False
        except OSError as e:
            print(f"Failed to create directory {tasks_dir}: {e}")
            return False

        config = load_config()
        if name in config.contexts:
            print(f"Context '{name}' already exists")
            return False

        config.contexts.append(name)
        save_config(config)
        print(f"Created context: {name}")
        return True
    except Exception as e:
        print(f"Error creating context: {e}")
        return False


def delete_context(name: str) -> bool:
    """Delete a context and its associated database."""
    try:
        config = load_config()
        if name not in config.contexts:
            return False

        # Delete the context's database file
        config_path = get_config_dir()
        db_path = config_path / "tasks" / f"{name}.db"
        db_path.unlink(missing_ok=True)

        # Remove from contexts list
        config.contexts.remove(name)

        # Clear active context if it was the deleted one
        if config.active_context == name:
            config.active_context = None

        save_config(config)
        return True
    except Exception as e:
        print(f"Error deleting context: {e}")  # For debugging
        return False
