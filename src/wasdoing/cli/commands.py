"""Command-line interface for Was Doing"""

import sys
import os
import argparse
import subprocess
import venv
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
import inquirer

from ..setup import (
    setup_wizard,
    ensure_setup,
    get_config_path,
    get_active_context,
    set_active_context,
    list_contexts,
    create_context,
)
from ..worklog.repository import WorkLogRepository
from ..worklog.context import get_context_db_path, get_context_path
from ..ui.sql_shell import run_sql_shell

console = Console()


def ensure_venv():
    """Ensure we're running in a virtual environment"""
    if not hasattr(sys, "real_prefix") and not sys.base_prefix != sys.prefix:
        # We're not in a venv, let's create one and install ourselves
        venv_path = Path.home() / ".local" / "share" / "wasdoing" / "venv"
        if not venv_path.exists():
            console.print("🔧 First run detected! Setting up virtual environment...")
            venv_path.parent.mkdir(parents=True, exist_ok=True)
            venv.create(venv_path, with_pip=True)

            # Get the path to our package directory
            package_dir = Path(__file__).parent.parent.parent

            # Install our package in the new venv
            pip = venv_path / "bin" / "pip"
            subprocess.run([str(pip), "install", "-e", str(package_dir)], check=True)

            # Create symlink to the doc command
            bin_dir = Path.home() / ".local" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            doc_link = bin_dir / "doc"
            if doc_link.exists():
                doc_link.unlink()
            doc_link.symlink_to(venv_path / "bin" / "doc")

        # Re-exec the command in the venv
        python = venv_path / "bin" / "python"
        os.execv(
            str(python), [str(python), "-m", "wasdoing.cli.commands"] + sys.argv[1:]
        )


def get_examples_text():
    return """Examples and Tips for using the doc command:

Basic Examples:
  # Create a new context
  doc -n my-project

  # List all contexts
  doc -l

  # Switch to a context (or use without argument for interactive menu)
  doc -c my-project

  # Add a history entry (what you're doing right now)
  doc -H "Working on feature X"

  # Add a summary entry (wrap up what you did)
  doc -s "Completed feature X implementation"

  # Watch mode (auto-generates docs when you make changes)
  doc -w

  # Watch mode with custom output file
  doc -w -o my-docs.md

Advanced Combinations:
  # Create context and start watching in one go
  doc -n feature-x -w

  # Switch context and add history entry
  doc -c feature-x -H "Starting work on database schema"

  # Switch context and start watching with custom output
  doc -c feature-x -w -o feature-docs.md

  # Add both history and summary in one command
  doc -H "Fixed bug #123" -s "Resolved memory leak in cache system"

  # Switch context interactively and start watching
  doc -c -w

Pro Tips:
  • Use -c without args for an interactive context menu
  • All output files are stored in your context directory
  • Watch mode (-w) automatically rebuilds docs on any changes
"""


def main():
    """Main CLI entry point"""
    # Ensure we're in a venv before proceeding
    ensure_venv()

    # Handle special help cases
    if "--help-examples" in sys.argv:
        print(get_examples_text())
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="""Document your work with history and summary entries.

Use --help-examples to see usage examples and tips""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Basic options
    parser.add_argument(
        "--help-examples",
        action="store_true",
        help="Show examples and tips for using the doc command",
    )

    # Setup commands
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the interactive setup wizard (first-time setup)",
    )

    # Context management
    context_group = parser.add_argument_group(
        "Context Management",
        description="Commands for managing different work contexts (projects/tasks)",
    )
    context_group.add_argument(
        "--context",
        "-c",
        nargs="?",  # Makes the argument optional
        const="",  # Value when flag is present but no argument given
        help="Set or switch to a context. Use without value for interactive menu",
    )
    context_group.add_argument(
        "--list-contexts",
        "-l",
        action="store_true",
        help="List all available contexts with their active status",
    )
    context_group.add_argument(
        "--new-context", "-n", help="Create a new context (e.g., 'doc -n my-project')"
    )

    # Entry management
    entry_group = parser.add_argument_group(
        "Entry Management", description="Commands for adding entries to your work log"
    )
    entry_group.add_argument(
        "--add-history", "-H", help="Add a history entry (what you're doing right now)"
    )
    entry_group.add_argument(
        "--add-summary", "-s", help="Add a summary entry (wrap up what you did)"
    )

    # Output management
    output_group = parser.add_argument_group(
        "Output Management", description="Commands for controlling document generation"
    )
    output_group.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch mode: automatically regenerate docs when you make changes",
    )
    output_group.add_argument(
        "--hot-reload", "-r", action="store_true", help="Alias for --watch"
    )
    output_group.add_argument(
        "--output",
        "-o",
        default="output.md",
        help="Output path for the generated markdown file. If a relative path is given, "
        "it will be created in the context directory. (default: output.md)",
    )
    output_group.add_argument(
        "--db-path", help="Custom path to the SQLite database (advanced use only)"
    )

    args = parser.parse_args()

    # Handle help examples
    if args.help_examples:
        print(get_examples_text())
        sys.exit(0)
