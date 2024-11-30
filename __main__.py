#!/usr/bin/env python3

"""
Main Entry Point for Work Documentation System

This module follows the Single Responsibility Principle by acting as the composition root
and command-line interface coordinator. It delegates all business logic to appropriate modules.
"""

# Standard library imports
import argparse
from pathlib import Path
import sys
from typing import Optional

# Third-party imports
from rich.console import Console
from rich.panel import Panel
import markdown
from weasyprint import HTML, CSS

# Local application imports
from repository import WorkLogRepository
from markdown_handler import MarkdownGenerator
from watcher import watch_database
from setup import (
    ensure_setup,
    setup_wizard,
    Config,
    get_config_path,
    get_active_context,
    set_active_context,
    list_contexts,
    create_context,
    delete_context,
    add_history_entry,
    add_summary_entry,
)
from setup.display import (
    show_panel,
    success_panel,
    error_panel,
    info_panel,
    warning_panel,
    show_help_panel,
)

console = Console()

DEFAULT_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 2em;
}
h1, h2, h3 { color: #333; }
code { background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; }
pre { background: #f8f8f8; padding: 1em; border-radius: 5px; overflow-x: auto; }
a { color: #0366d6; }
"""


def export_to_pdf(markdown_path: Path, pdf_path: Path) -> None:
    """Convert a markdown file to PDF with nice styling"""
    try:
        # Read markdown content
        with open(markdown_path, "r") as f:
            md_content = f.read()

        # Convert to HTML
        html = markdown.markdown(md_content, extensions=["extra", "codehilite"])

        # Create styled HTML document
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{DEFAULT_CSS}</style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        # Generate PDF
        HTML(string=html_doc).write_pdf(pdf_path, stylesheets=[CSS(string=DEFAULT_CSS)])
        console.print(f"📄 Exported PDF to: {pdf_path}")

    except Exception as e:
        console.print(f"[red]❌ Failed to export PDF: {str(e)}[/red]")
        sys.exit(1)


class RichHelpFormatter(argparse.HelpFormatter):
    """Custom formatter for creating Rich-styled help output"""
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def format_help(self):
        """Override to return our custom formatted help"""
        return ""  # We'll handle the actual formatting in the parser


def main():
    parser = argparse.ArgumentParser(
        description="Document your work with history and summary entries.",
        formatter_class=RichHelpFormatter,
        usage=argparse.SUPPRESS,  # We'll handle usage in our custom help
    )

    parser.add_argument(
        "--setup", action="store_true", help="Run the interactive setup wizard"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify if Was Doing is properly set up"
    )

    # Context management
    context_group = parser.add_argument_group("Context Management")
    context_group.add_argument(
        "--context",
        "-c",
        nargs='?',  # Make it optional to trigger our custom handling
        metavar="CONTEXT_NAME",
        help="Set or switch to a context (project/task)",
    )
    context_group.add_argument(
        "--list-contexts", "-l", action="store_true", help="List all available contexts"
    )
    context_group.add_argument(
        "--new-context",
        "-n",
        metavar="CONTEXT_NAME",
        help="Create a new context",
    )

    # Entry management
    entry_group = parser.add_argument_group("Entry Management")
    entry_group.add_argument("-H", "--add-history", metavar="TEXT", help="Add a history entry")
    entry_group.add_argument("-s", "--add-summary", metavar="TEXT", help="Add a summary entry")
    entry_group.add_argument("--history", action="store_true", help="View history entries")
    entry_group.add_argument("--summary", action="store_true", help="View summary entries")

    # Output management
    output_group = parser.add_argument_group("Output Management")
    output_group.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch mode: automatically regenerate markdown on database changes",
    )
    output_group.add_argument(
        "--hot-reload", "-r", action="store_true", help="Alias for --watch"
    )
    output_group.add_argument(
        "--output",
        "-o",
        help="Output path for the generated markdown file",
        default="work_doc.md",
    )
    output_group.add_argument(
        "--export",
        "-e",
        help="Export markdown file to PDF (e.g. --export output.pdf)",
        metavar="PDF_PATH",
    )

    parser.add_argument("--db-path", help="Path to the SQLite database")

    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        # Main help panel
        console.print(Panel(
            "[bold blue]Was Doing[/]\n"
            "[dim]A development-friendly work documentation system[/]",
            title="👋 Welcome",
            border_style="blue",
            width=80
        ))

        # Setup commands panel
        setup_panel = Panel(
            "[bold]--setup[/]              Run the interactive setup wizard\n"
            "[bold]--verify[/]             Check if Was Doing is properly configured",
            title="🔧 Setup",
            border_style="cyan",
            width=80
        )

        # Context management panel
        context_panel = Panel(
            "[bold]-c, --context[/] NAME    Switch to a different context\n"
            "[bold]-n, --new-context[/] NAME Create a new context\n"
            "[bold]-l, --list-contexts[/]   List all available contexts",
            title="📂 Context Management",
            border_style="blue",
            width=80
        )

        # Entry management panel
        entry_panel = Panel(
            "[bold]-H, --add-history[/] TEXT Add a history entry\n"
            "[bold]-s, --add-summary[/] TEXT Add a summary entry",
            title="📝 Entry Management",
            border_style="green",
            width=80
        )

        # Output management panel
        output_panel = Panel(
            "[bold]-w, --watch[/]           Watch mode: auto-regenerate on changes\n"
            "[bold]-r, --hot-reload[/]      Alias for --watch\n"
            "[bold]-o, --output[/] PATH     Output path for markdown (default: work_doc.md)\n"
            "[bold]-e, --export[/] PATH     Export to PDF",
            title="📄 Output Management",
            border_style="magenta",
            width=80
        )

        # Examples panel
        examples_panel = Panel(
            "# Create a new context and add entries\n"
            "[dim]$[/] [bold]doc -n[/] my-project\n"
            "[dim]$[/] [bold]doc -H[/] \"Started working on authentication\"\n"
            "[dim]$[/] [bold]doc -s[/] \"Implemented OAuth2 flow\"\n\n"
            "# Switch context and use watch mode\n"
            "[dim]$[/] [bold]doc -c[/] another-project\n"
            "[dim]$[/] [bold]doc -w[/]",
            title="💡 Examples",
            border_style="yellow",
            width=80
        )

        # Print all panels
        console.print(setup_panel)
        console.print(context_panel)
        console.print(entry_panel)
        console.print(output_panel)
        console.print(examples_panel)
        sys.exit(0)

    try:
        args = parser.parse_args()

        # Check if setup is needed before any other operations
        if not ensure_setup():
            console.print("[yellow]Was Doing needs to be set up first.[/yellow]")
            console.print("Run: doc --setup")
            sys.exit(1)

        # Handle verify command
        if args.verify:
            config_path = get_config_path()
            if not config_path or not (config_path / "config.toml").exists():
                console.print(Panel(
                    "[red]Was Doing is not configured![/]\n\n"
                    "[yellow]Run [bold]doc --setup[/] to configure Was Doing.[/]",
                    title="❌ Setup Required",
                    border_style="red",
                    width=80
                ))
                sys.exit(1)
            else:
                console.print(Panel(
                    "[green]Was Doing is properly configured![/]\n\n"
                    f"[dim]Configuration:[/] {config_path}/config.toml\n"
                    f"[dim]Tasks Directory:[/] {config_path}/tasks\n"
                    f"[dim]Active Context:[/] {get_active_context() or '[yellow]None[/]'}",
                    title="✅ Setup Verified",
                    border_style="green",
                    width=80
                ))
                sys.exit(0)

        # Get active context or exit if none
        active_context = get_active_context()
        if not active_context:
            if args.add_history or args.add_summary or args.watch:
                error_panel(
                    "[yellow]No active context.[/]\n\n"
                    "Set one with [bold]--context[/] or create new with [bold]--new-context[/]",
                    title="❌ No Context"
                )
                sys.exit(1)

        # Handle history/summary entries first if we have them
        if args.add_history:
            add_history_entry(args.add_history)
            success_panel(
                f"[green]Added history entry:[/]\n{args.add_history}",
                title="📝 History Entry Added"
            )
            sys.exit(0)

        if args.add_summary:
            add_summary_entry(args.add_summary)
            success_panel(
                f"[green]Added summary entry:[/]\n{args.add_summary}",
                title="📝 Summary Entry Added"
            )
            sys.exit(0)

        # Handle watch mode
        if args.watch:
            info_panel(
                f"[green]Watching for changes in context: {active_context}[/]\n\n"
                "[dim]Press Ctrl+C to stop[/]",
                title="👀 Watch Mode"
            )
            watch_database(active_context)
            sys.exit(0)

        # Only show context selector for explicit context commands
        if (hasattr(args, 'context') and args.context is None) or args.list_contexts:
            try:
                contexts = list_contexts()
                active = get_active_context()

                if not contexts:
                    console.print(Panel(
                        "[yellow]No contexts found.[/]\n\n"
                        "Create one with: [bold]doc -n CONTEXT_NAME[/]",
                        title="📂 Contexts",
                        border_style="blue",
                        width=80
                    ))
                    sys.exit(0)

                if hasattr(args, 'context') and args.context is None:
                    # Interactive context selection
                    from inquirer import prompt, List

                    # Create choices list with active context first
                    sorted_contexts = sorted(contexts, key=lambda x: (x != active, x.lower()))
                    choices = [
                        (f"{'* ' if ctx == active else '  '}{ctx}{' (active)' if ctx == active else ''}", ctx)
                        for ctx in sorted_contexts
                    ]
                    choices.extend([
                        ('+ Create new context', 'new'),
                        ('- Delete a context', 'delete')
                    ])

                    questions = [
                        List('context',
                             message="Select a context or action",
                             choices=choices)
                    ]

                    answer = prompt(questions)
                    if answer:
                        if answer['context'] == 'new':
                            # Ask for new context name
                            from inquirer import Text
                            name_q = [
                                Text('name',
                                     message="Enter new context name",
                                     validate=lambda _, x: bool(x and all(c.isalnum() or c in '-_' for c in x)))
                            ]
                            name_answer = prompt(name_q)
                            if name_answer and name_answer['name']:
                                new_name = name_answer['name']
                                if create_context(new_name):
                                    set_active_context(new_name)
                                    success_panel(
                                        f"[green]Created and switched to: {new_name}[/]",
                                        title="✨  Context Created"
                                    )
                                else:
                                    error_panel(
                                        f"[red]Failed to create context: {new_name}[/]\n\n"
                                        "[yellow]Context names must be alphanumeric (with hyphens or underscores)[/]"
                                    )
                        elif answer['context'] == 'delete':
                            # Show context selection for deletion
                            delete_choices = [(ctx, ctx) for ctx in sorted_contexts]
                            delete_q = [
                                List('to_delete',
                                     message="Select context to delete",
                                     choices=delete_choices)
                            ]
                            delete_answer = prompt(delete_q)
                            if delete_answer:
                                to_delete = delete_answer['to_delete']
                                # Double check with the user
                                confirm_q = [
                                    List('confirm',
                                         message=f"[red]Are you sure you want to delete '{to_delete}'?[/] This cannot be undone.",
                                         choices=[
                                             ('No, keep it', False),
                                             ('Yes, delete it', True)
                                         ])
                                ]
                                confirm = prompt(confirm_q)
                                if confirm and confirm['confirm']:
                                    if delete_context(to_delete):
                                        success_panel(
                                            f"[green]Successfully deleted context: {to_delete}[/]",
                                            title="🗑️  Context Deleted"
                                        )
                                    else:
                                        error_panel(
                                            f"[red]Failed to delete context: {to_delete}[/]"
                                        )
                        elif answer['context'] != active:
                            # Switch to selected context
                            set_active_context(answer['context'])
                            console.print(Panel(
                                f"[green]Now working in: {answer['context']}[/]",
                                title="🔄 Context Switched",
                                border_style="green",
                                width=80
                            ))
                else:
                    # Just list contexts (for -l/--list-contexts)
                    console.print(Panel(
                        "\n".join(
                            f"[green]* {ctx}[/green] (active)" if ctx == active
                            else f"  {ctx}"
                            for ctx in sorted_contexts
                        ),
                        title="📂 Contexts",
                        border_style="blue",
                        width=80
                    ))
                    console.print("\n[dim]Use [bold]doc -c[/] to switch contexts[/]")
                sys.exit(0)
            except FileNotFoundError:
                console.print(Panel(
                    "[yellow]No contexts found.[/]\n\n"
                    "Create one with: [bold]doc -n CONTEXT_NAME[/]",
                    title="📂 Contexts",
                    border_style="blue",
                    width=80
                ))
                sys.exit(0)

        # Handle context switching
        if args.context:
            if set_active_context(args.context):
                console.print(Panel(
                    f"[green]Now working in: {args.context}[/]",
                    title="🔄 Context Switched",
                    border_style="green",
                    width=80
                ))
            else:
                # Context doesn't exist, ask if they want to create it
                console.print(Panel(
                    f"[yellow]Context '{args.context}' doesn't exist.[/]\n",
                    title="❓ Context Not Found",
                    border_style="yellow",
                    width=80
                ))

                # Use inquirer for a nice prompt
                from inquirer import prompt, List, shortcuts

                questions = [
                    List('action',
                         message=f"Would you like to create '{args.context}'?",
                         choices=[
                             ('Yes, create and switch to it', 'create'),
                             ('No, show available contexts', 'list'),
                             ('Cancel', 'cancel')
                         ])
                ]

                answer = prompt(questions)
                if answer and answer['action'] == 'create':
                    if create_context(args.context):
                        set_active_context(args.context)
                        success_panel(
                            f"[green]Created and switched to: {args.context}[/]",
                            title="✨  Context Created"
                        )
                    else:
                        error_panel(
                            f"[red]Failed to create context: {args.context}[/]\n\n"
                            "[yellow]Context names must be alphanumeric (with hyphens or underscores)[/]"
                        )
                elif answer and answer['action'] == 'list':
                    # Show available contexts
                    contexts = list_contexts()
                    if contexts:
                        console.print(Panel(
                            "\n".join(f"  {ctx}" for ctx in sorted(contexts)),
                            title="📂 Available Contexts",
                            border_style="blue",
                            width=80
                        ))
                    else:
                        console.print(Panel(
                            "[yellow]No contexts found.[/]\n\n"
                            "Create one with: [bold]doc -n CONTEXT_NAME[/]",
                            title="📂 Contexts",
                            border_style="blue",
                            width=80
                        ))
            sys.exit(0)

        # Handle new context creation
        if args.new_context:
            if create_context(args.new_context):
                success_panel(
                    f"[green]Created new context: {args.new_context}[/]",
                    title="✨  Context Created"
                )
            else:
                error_panel(
                    f"[red]Failed to create context: {args.new_context}[/]\n\n"
                    "[yellow]Context names must be alphanumeric (with hyphens or underscores)[/]"
                )
            sys.exit(0)

        # Get active context or exit if none
        active_context = get_active_context()
        if not active_context and (
            args.add_history or args.add_summary or args.watch or args.hot_reload
        ):
            console.print(Panel(
                "[red]No active context found.[/]\n\n"
                "[yellow]Set one with [bold]--context[/] or create new with [bold]--new-context[/][/]",
                title="❌ No Context",
                border_style="red",
                width=80
            ))
            sys.exit(1)

        # Use configuration or command line arguments
        config_path = get_config_path()
        db_path = (
            Path(args.db_path)
            if args.db_path
            else config_path / "tasks" / f"{active_context}.db"
        )
        output_path = Path(args.output)

        # Initialize repository
        repo = WorkLogRepository(db_path)

        # Handle commands
        if args.add_history:
            entry = repo.add_entry("history", args.add_history)
            console.print(Panel(
                f"[green]Added to {active_context}:[/]\n\n"
                f"[dim]{entry.timestamp}[/]\n"
                f"{args.add_history}",
                title="📝 History Entry Added",
                border_style="green",
                width=80
            ))

        if args.add_summary:
            entry = repo.add_entry("summary", args.add_summary)
            console.print(Panel(
                f"[green]Added to {active_context}:[/]\n\n"
                f"[dim]{entry.timestamp}[/]\n"
                f"{args.add_summary}",
                title="📝 Summary Entry Added",
                border_style="green",
                width=80
            ))

        # Generate markdown or watch
        if not (args.watch or args.hot_reload):
            entries = repo.get_all_entries()
            markdown_gen = MarkdownGenerator()
            markdown_gen.generate_from_entries(entries, output_path)
            console.print(Panel(
                f"[green]Generated markdown file:[/] {output_path}",
                title="📄 Documentation Updated",
                border_style="blue",
                width=80
            ))

            # Handle PDF export if requested
            if args.export:
                try:
                    export_to_pdf(output_path, Path(args.export))
                    console.print(Panel(
                        f"[green]Successfully exported to:[/] {args.export}",
                        title="📑 PDF Export Complete",
                        border_style="green",
                        width=80
                    ))
                except Exception as e:
                    console.print(Panel(
                        f"[red]Failed to export PDF:[/]\n\n{str(e)}",
                        title="❌ Export Failed",
                        border_style="red",
                        width=80
                    ))
                    sys.exit(1)
        else:
            # Start watch mode
            watch_database(db_path, output_path)

    except argparse.ArgumentError as e:
        parser.print_help()
        sys.exit(1)
    except SystemExit as e:
        # Catch the system exit from argparse's error handling
        if str(e) == '2':  # This is the exit code for argument errors
            command = next((arg for arg in sys.argv[1:] if arg.startswith('-')), None)
            if command:
                console.print(f"[red]Error: '{command}' is not a valid command[/red]")
                console.print("\nDid you mean one of these?")
                if command in ['-p']:
                    console.print("  doc -n PROJECT_NAME    Create a new project/context")
                    console.print("  doc -c PROJECT_NAME    Switch to an existing project")
                    console.print("  doc -l                 List all projects")
                else:
                    console.print("  -n, --new-context      Create a new context")
                    console.print("  -c, --context          Switch to a context")
                    console.print("  -l, --list-contexts    List all contexts")
                    console.print("\nUse 'doc --help' to see all available commands")
            else:
                parser.print_help()
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()
