"""
Setup Module for Was Doing

This module handles the initial setup and configuration management.
It provides:
1. Interactive setup process
2. Configuration file management
3. User preference handling
4. Path validation and creation
"""

from pathlib import Path
from typing import Optional

from .config import (
    Config,
    get_config_path,
    get_active_context,
    set_active_context,
    list_contexts,
    create_context,
    delete_context,
    ensure_setup,
)
from .interactive import setup_wizard

__all__ = [
    "ensure_setup",
    "setup_wizard",
    "Config",
    "get_config_path",
    "get_active_context",
    "set_active_context",
    "list_contexts",
    "create_context",
    "delete_context",
]
