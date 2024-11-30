"""Command-line interface for Was Doing"""

import sys
import os
import argparse
import subprocess
import venv
from pathlib import Path
from rich.console import Console

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
from ..worklog.context import get_context_db_path
from ..ui.sql_shell import run_sql_shell

console = Console()

def ensure_venv():
    """Ensure we're running in a virtual environment"""
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
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
        os.execv(str(python), [str(python), "-m", "wasdoing.cli.commands"] + sys.argv[1:])

def main():
    """Main CLI entry point"""
    # Ensure we're in a venv before proceeding
    ensure_venv()

    parser = argparse.ArgumentParser(
        description="Document your work with history and summary entries."
    )

    # Setup commands
    parser.add_argument(
        "--setup", action="store_true", help="Run the interactive setup wizard"
    )

    # Context management
    context_group = parser.add_argument_group("Context Management")
    context_group.add_argument(
        "--context", "-c", help="Set or switch to a context (project/task)"
    )
    context_group.add_argument(
        "--list-contexts", "-l", action="store_true", help="List all available contexts"
    )
    context_group.add_argument(
        "--new-context", "-n", help="Create a new context"
    )

    # Entry management
    entry_group = parser.add_argument_group("Entry Management")
    entry_group.add_argument(
        "--add-history", "-H", help="Add a history entry"
    )
    entry_group.add_argument(
        "--add-summary", "-s", help="Add a summary entry"
    )

    # Output management
    output_group = parser.add_argument_group("Output Management")
    output_group.add_argument(
        "--watch", "-w", action="store_true",
        help="Watch mode: automatically regenerate markdown on database changes"
    )
    output_group.add_argument(
        "--hot-reload", "-r", action="store_true", help="Alias for --watch"
    )
    output_group.add_argument(
        "--output", "-o", default="output.md",
        help="Output path for the generated markdown file"
    )
    output_group.add_argument(
        "--db-path", help="Custom path to the SQLite database"
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

    if args.context:
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
    if not active_context and (
        args.add_history or args.add_summary or args.watch or args.hot_reload
    ):
        console.print(
            "[red]❌ No active context. Set one with --context or create new with --new-context[/red]"
        )
        sys.exit(1)

    # Use configuration or command line arguments
    config_dir = get_config_path()
    db_path = (
        Path(args.db_path)
        if args.db_path
        else get_context_db_path(config_dir, active_context)
    )
    output_path = Path(args.output)

    # Initialize repository
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
        watch_database(db_path, output_path)
        sys.exit(0)