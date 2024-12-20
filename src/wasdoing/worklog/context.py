"""Context management utilities"""

import re
from pathlib import Path
from typing import Optional
import toml
from datetime import datetime

def format_context_name(name: str) -> str:
    """
    Format a context name to kebab-case.
    Example: "MyNewFeature" -> "my-new-feature"
    """
    # Insert hyphen between camelCase
    name = re.sub(r'(?<!^)(?=[A-Z])', '-', name)
    # Convert to lowercase
    return name.lower()

def get_context_path(config_dir: Path, context_name: str) -> Path:
    """Get the context directory path"""
    formatted_name = format_context_name(context_name)
    return config_dir / "contexts" / formatted_name

def get_context_db_path(config_dir: Path, context_name: str) -> Path:
    """Get the database path for a context"""
    return get_context_path(config_dir, context_name) / "database.db"

def get_context_config_path(config_dir: Path, context_name: str) -> Path:
    """Get the config path for a context"""
    return get_context_path(config_dir, context_name) / "config.toml"

def get_context_output_path(config_dir: Path, context_name: str) -> Path:
    """Get the default output path for a context"""
    return get_context_path(config_dir, context_name) / "output.md"

def create_context_structure(config_dir: Path, context_name: str) -> bool:
    """Create the full context directory structure"""
    try:
        print(f"Creating context directory at {config_dir}")
        context_dir = get_context_path(config_dir, context_name)
        context_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {context_dir}")

        # Create default context config
        config = {
            "name": context_name,
            "created_at": datetime.now().isoformat(),
            "output_file": "output.md",
            "watch_interval": 1.0,
        }
        print(f"Created config: {config}")

        config_path = get_context_config_path(config_dir, context_name)
        print(f"Writing config to: {config_path}")
        with open(config_path, "w") as f:
            toml.dump(config, f)
        print("Config written successfully")

        return True
    except Exception as e:
        print(f"Error creating context structure: {str(e)}")
        return False

def load_context_config(config_dir: Path, context_name: str) -> dict:
    """Load context-specific configuration"""
    config_path = get_context_config_path(config_dir, context_name)
    if not config_path.exists():
        return {}

    try:
        return toml.load(config_path)
    except Exception:
        return {}