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
    if len(sys.argv) == 3 and sys.argv[1:3] == ["--help", "examples"]:
        print(get_examples_text())
        sys.exit(0)

    parser = argparse.ArgumentParser(
        usage="%(prog)s [-h] [--help examples] [--setup] [--context [CONTEXT]] [--list-contexts] [--new-context NEW_CONTEXT] [--add-history ADD_HISTORY] [--add-summary ADD_SUMMARY] [--watch] [--hot-reload] [--output OUTPUT] [--db-path DB_PATH]",
        description="Document your work with history and summary entries.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Setup commands
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the interactive setup wizard (first-time setup)"
    )

    # Context management
    context_group = parser.add_argument_group('Context Management',
        description="Commands for managing different work contexts (projects/tasks)")
    context_group.add_argument(
        "--context", "-c",
        nargs='?',  # Makes the argument optional
        const="",   # Value when flag is present but no argument given
        help="Set or switch to a context. Use without value for interactive menu"
    )
    context_group.add_argument(
        "--list-contexts", "-l", action="store_true",
        help="List all available contexts with their active status"
    )
    context_group.add_argument(
        "--new-context", "-n",
        help="Create a new context (e.g., 'doc -n my-project')"
    )

    # Entry management
    entry_group = parser.add_argument_group('Entry Management',
        description="Commands for adding entries to your work log")
    entry_group.add_argument(
        "--add-history", "-H",
        help="Add a history entry (what you're doing right now)"
    )
    entry_group.add_argument(
        "--add-summary", "-s",
        help="Add a summary entry (wrap up what you did)"
    )

    # Output management
    output_group = parser.add_argument_group('Output Management',
        description="Commands for controlling document generation")
    output_group.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch mode: automatically regenerate docs when you make changes"
    )
    output_group.add_argument(
        "--hot-reload", "-r", action="store_true",
        help="Alias for --watch"
    )
    output_group.add_argument(
        "--output", "-o",
        default="output.md",
        help="Output path for the generated markdown file. If a relative path is given, "
             "it will be created in the context directory. (default: output.md)"
    )
    output_group.add_argument(
        "--db-path",
        help="Custom path to the SQLite database (advanced use only)"
    )

    args = parser.parse_args()

    # Handle setup first
    if args.setup:
        if not setup_wizard():
            console.print("[red]Setup failed. Please try again.[/red]")
            sys.exit(1)
        sys.exit(0)

    # Ensure configuration exists
    error = ensure_setup()
    if error:
        console.print(f"[red]❌ {error}[/red]")
        sys.exit(1)

    # Handle context management
    if args.list_contexts:
        contexts = list_contexts()
        if not contexts:
            console.print("No contexts found. Create one with --new-context")
        else:
            active = get_active_context()
            console.print("\n📁 Available Contexts:")
            for ctx in contexts:
                if ctx == active:
                    console.print(f"  ▶️  {ctx} (active)")
                else:
                    console.print(f"     {ctx}")
        sys.exit(0)

    if args.new_context:
        if create_context(args.new_context):
            console.print(f"✅ Created new context: {args.new_context}")
            if not get_active_context():
                set_active_context(args.new_context)
                console.print(f"✅ Set {args.new_context} as active context")
        else:
            console.print(f"[red]❌ Failed to create context: {args.new_context}[/red]")
        sys.exit(0)

    if args.context is not None:  # Changed from if args.context:
        if args.context == "":  # Handle empty -c flag
            contexts = list_contexts()
            if not contexts:
                console.print("No contexts found. Create one with --new-context")
                sys.exit(1)

            questions = [
                inquirer.List(
                    'context',
                    message="Choose a context",
                    choices=[(f"▶️  {ctx}" if ctx == get_active_context() else ctx) for ctx in contexts],
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers:  # User cancelled
                sys.exit(0)

            # Strip the active marker if present
            selected = answers['context'].replace("▶️  ", "")

            if set_active_context(selected):
                console.print(f"✅ Switched to context: {selected}")
            else:
                console.print(f"[red]❌ Failed to switch to context: {selected}[/red]")
        else:
            if set_active_context(args.context):
                console.print(f"✅ Switched to context: {args.context}")
            else:
                console.print(f"[red]❌ Context not found: {args.context}[/red]")
                console.print(
                    "Create it with --new-context or list available contexts with --list-contexts"
                )
        sys.exit(0)

    # Get active context or exit if none
    active_context = get_active_context()

    # Use configuration or command line arguments
    config_dir = get_config_path()

    # Add this check before trying to use db_path
    if not active_context and not args.db_path:
        if not (
            args.setup
            or args.new_context
            or args.list_contexts
            or args.context is not None
        ):
            console.print(
                "[red]❌ No active context. Use --context to select one or --new-context to create one[/red]"
            )
            sys.exit(1)

    db_path = (
        Path(args.db_path)
        if args.db_path
        else get_context_db_path(config_dir, active_context) if active_context else None
    )

    # Initialize repository only if we need it
    if db_path:
        repo = WorkLogRepository(db_path)

    # Handle commands
    if args.add_history:
        entry = repo.add_entry("history", args.add_history)
        console.print(
            f"📝 Added history entry to {active_context} at {entry.timestamp}"
        )

    if args.add_summary:
        entry = repo.add_entry("summary", args.add_summary)
        console.print(
            f"📝 Added summary entry to {active_context} at {entry.timestamp}"
        )

    # Handle watch mode
    if args.watch or args.hot_reload:
        from ..ui.watch import watch_database

        # If output path is relative, make it relative to the context directory
        output_path = Path(args.output)
        if not output_path.is_absolute():
            context_dir = get_context_path(config_dir, active_context)
            output_path = context_dir / output_path
            # Create the directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

        watch_database(db_path, output_path)
        sys.exit(0)
