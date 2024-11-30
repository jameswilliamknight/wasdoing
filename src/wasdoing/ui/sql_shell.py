#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich import print as rprint
from ..setup.config import get_config_path, get_active_context

console = Console()

def get_current_db_path() -> Optional[Path]:
    """Get the path to the current context's database"""
    config_dir = get_config_path()
    if not config_dir:
        return None

    active_context = get_active_context()
    if not active_context:
        return None

    db_path = config_dir / "tasks" / f"{active_context}.db"
    if not db_path.exists():
        return None

    return db_path

def format_sql_results(cursor: sqlite3.Cursor) -> Table:
    """Format SQL results into a Rich table"""
    table = Table(show_header=True, header_style="bold magenta")

    # Add columns
    if cursor.description:
        columns = [col[0] for col in cursor.description]
        for column in columns:
            table.add_column(column)

        # Add rows
        for row in cursor.fetchall():
            table.add_row(*[str(cell) for cell in row])

    return table

def run_sql_shell():
    """Run an interactive SQL shell with syntax highlighting"""
    # Check configuration
    if not get_config_path():
        console.print("[red]❌ WWJD is not configured. Run 'doc --setup' first.[/red]")
        return

    # Check active context
    active_context = get_active_context()
    if not active_context:
        console.print("[red]❌ No active context. Set one with 'doc -c <context>' or create new with 'doc -n <context>'[/red]")
        return

    # Get database path
    db_path = get_current_db_path()
    if not db_path:
        console.print(f"[red]❌ Database not found for context '{active_context}'[/red]")
        return

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        console.print(f"[red]❌ Failed to connect to database: {e}[/red]")
        return

    console.print(f"\n[green]🔍 SQL Shell for context '[bold]{active_context}[/bold]'[/green]")
    console.print("[dim]Type your SQL queries. Use .help for commands, .tables to list tables, or .exit to quit.[/dim]\n")

    while True:
        try:
            # Get user input with syntax highlighting
            query = Prompt.ask("[blue]sql>[/blue] ")

            # Handle special commands
            if query.lower() in ['.exit', '.quit', 'exit', 'quit']:
                break
            elif query.lower() == '.help':
                console.print("\n[yellow]Available commands:[/yellow]")
                console.print("  .help   - Show this help message")
                console.print("  .tables - List all tables")
                console.print("  .exit   - Exit the SQL shell")
                console.print("  .quit   - Exit the SQL shell\n")
                continue
            elif query.lower() == '.tables':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                if tables:
                    console.print("\n[yellow]Available tables:[/yellow]")
                    for table in tables:
                        console.print(f"  {table[0]}")
                    console.print()
                else:
                    console.print("[yellow]No tables found in database[/yellow]\n")
                continue

            # Execute the query
            cursor.execute(query)

            # Format and display results
            if cursor.description:  # SELECT query
                table = format_sql_results(cursor)
                console.print(table)
            else:  # INSERT, UPDATE, DELETE query
                affected = cursor.rowcount
                conn.commit()
                console.print(f"[green]✓ Query executed successfully. {affected} rows affected.[/green]")

        except sqlite3.Error as e:
            console.print(f"[red]❌ SQL Error: {e}[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Use .exit or .quit to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

    conn.close()
    console.print("\n[green]👋 Goodbye![/green]")

if __name__ == "__main__":
    run_sql_shell()
