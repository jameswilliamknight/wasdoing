"""
Interactive Setup Wizard for Was Doing

This module provides an interactive CLI experience for setting up Was Doing.
It uses rich for pretty output and inquirer for user input.
"""

import os
from pathlib import Path
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from halo import Halo

from .config import Config, save_config, get_config_path

# Initialize console
console = Console(force_terminal=True, no_color=False)


def validate_path(answers: dict, current: str) -> bool:
    """Validate a path input"""
    try:
        path = Path(current)
        if path.exists() and not path.is_dir():
            console.print("[red]Path exists but is not a directory[/red]")
            return False
        return True
    except Exception:
        return False


def setup_wizard() -> bool:
    """Run the interactive setup wizard"""
    console.print("\n[bold]Welcome to Was Doing![/bold]")
    console.print(
        "\nLet's get your work documentation system set up. This will only take a moment.\n"
    )

    # Ask for config location
    questions = [
        inquirer.List(
            "config_location",
            message="Where would you like to store your configuration",
            choices=[
                ("Default location (~/.wwjd)", "default"),
                ("Custom location", "custom"),
            ],
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:  # User cancelled
        return False

    try:
        if answers["config_location"] == "default":
            config_dir = Path.home() / ".wwjd" / "wasdoing"
        else:
            path_question = [
                inquirer.Path(
                    "config_path",
                    message="Enter the path for your configuration",
                    exists=False,
                    path_type=inquirer.Path.DIRECTORY,
                    validate=validate_path,
                )
            ]
            path_answer = inquirer.prompt(path_question)
            if not path_answer:  # User cancelled
                return False
            config_dir = Path(path_answer["config_path"])

        # Create base directory structure
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create contexts directory
        contexts_dir = config_dir / "contexts"
        contexts_dir.mkdir(exist_ok=True)

        # Create pointer file to store config location
        pointer_dir = Path.home() / ".wwjd"
        pointer_dir.mkdir(parents=True, exist_ok=True)
        pointer_file = pointer_dir / "config"
        pointer_file.write_text(str(config_dir))

        console.print(
            Panel(
                "[green]✨ Setup complete![/]\n\n"
                f"[dim]Configuration directory:[/] {config_dir}\n"
                f"[dim]Contexts directory:[/] {contexts_dir}\n\n"
                "Try creating your first context:\n"
                "[dim]$[/] [bold]doc -n my-project[/]",
                title="🎉 Ready to Go!",
                border_style="green",
                width=80,
            )
        )

        return True

    except Exception as e:
        console.print(f"[red]Setup failed: {str(e)}[/red]")
        return False


def write_config_pointer(config_pointer: Path, config_dir: Path) -> None:
    """Write the config pointer file"""
    config_pointer.mkdir(parents=True, exist_ok=True)
    with open(config_pointer / "config", "w") as f:
        f.write(str(config_dir))
