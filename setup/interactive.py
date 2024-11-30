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
from rich.style import Style
from halo import Halo
from tqdm import tqdm

from .config import Config, save_config, DEFAULT_CONFIG

# Initialize console with no clearing
console = Console(force_terminal=True, no_color=False, soft_wrap=True)

def setup_wizard() -> bool:
    """Run the interactive setup wizard"""
    # Show welcome panel
    welcome = Panel(
        "[bold blue]Welcome to Was Doing![/]\n\n"
        "Let's get your work documentation system set up. "
        "This will only take a moment.",
        title="🔧 Setup Wizard",
        border_style="blue"
    )
    console.print(welcome)

    # Get configuration location
    questions = [
        inquirer.List(
            "location",
            message="Where would you like to store your configuration?",
            choices=[
                ("Default location (~/.wasdoing)", str(Path.home() / ".wasdoing")),
                ("Custom location", "custom")
            ]
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return False

    if answers["location"] == "custom":
        questions = [
            inquirer.Path(
                "custom_path",
                message="Enter the path for configuration storage",
                exists=False,
                normalize_to_absolute_path=True,
                path_type=inquirer.Path.DIRECTORY
            )
        ]

        custom = inquirer.prompt(questions)
        if not custom:
            return False

        config_dir = Path(custom["custom_path"])
    else:
        config_dir = Path(answers["location"])

    try:
        # Setup progress spinner
        spinner = Halo(text="Setting up configuration", spinner="dots")
        spinner.start()

        # Create directories with progress
        steps = [
            ("Creating config directory", lambda: config_pointer.mkdir(parents=True, exist_ok=True)),
            ("Creating tasks directory", lambda: (config_dir / "tasks").mkdir(parents=True, exist_ok=True)),
            ("Saving configuration", lambda: save_config(config, config_dir)),
            ("Creating config pointer", lambda: write_config_pointer(config_pointer, config_dir))
        ]

        config_pointer = Path.home() / ".wasdoing"
        config = Config.from_dict(DEFAULT_CONFIG)
        config.config_dir = str(config_dir)

        for msg, func in steps:
            spinner.text = msg
            func()

        spinner.stop()

        # Show success panel
        success = Panel(
            "[bold green]Setup Complete![/]\n\n"
            f"[dim]Configuration:[/] {config_dir}\n"
            f"[dim]Tasks Directory:[/] {config_dir / 'tasks'}\n\n"
            "[bold]Try these commands:[/]\n"
            "  [blue]doc -n my-project[/]     Create your first context\n"
            "  [blue]doc -H \"Started work\"[/]  Add your first entry\n"
            "  [blue]doc -l[/]                List available contexts",
            title="✨ Ready to Go!",
            border_style="green"
        )
        console.print(success)

        return True
    except Exception as e:
        if "spinner" in locals():
            spinner.fail(f"Setup failed: {str(e)}")
        else:
            console.print(f"\n[red]Failed to save configuration: {str(e)}[/red]")
        return False

def write_config_pointer(config_pointer: Path, config_dir: Path) -> None:
    """Write the config pointer file"""
    with open(config_pointer / "config", "w") as f:
        f.write(str(config_dir))
