"""Display utilities for Was Doing CLI output."""
from typing import Optional, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.text import Text

console = Console()

def format_command_help(commands: List[Tuple[str, str]], min_spacing: int = 4) -> str:
    """Format command help text with right-aligned descriptions.

    Args:
        commands: List of (command, description) tuples
        min_spacing: Minimum spaces between command and description

    Returns:
        Formatted string with aligned descriptions
    """
    if not commands:
        return ""

    # Find the longest command length
    max_cmd_len = max(len(cmd) for cmd, _ in commands)

    # Format each line with proper spacing
    lines = []
    for cmd, desc in commands:
        padding = " " * (max_cmd_len - len(cmd) + min_spacing)
        lines.append(f"{cmd}{padding}{desc}")

    return "\n".join(lines)

def show_panel(
    content: str,
    *,
    title: Optional[str] = None,
    style: str = "blue",
    padding: tuple[int, int] = (1, 3),  # (vertical, horizontal) padding
    width: int = 80,
    align: str = "left",  # left, center, right
) -> None:
    """Display a consistently styled panel.

    Args:
        content: The main text content to display
        title: Optional title with emoji
        style: Border style color (default: blue)
        padding: Tuple of (vertical, horizontal) padding
        width: Panel width (default: 80)
        align: Content alignment (default: left)
    """
    if align != "left":
        content = Align(content, align=align)

    panel = Panel(
        content,
        title=title,
        border_style=style,
        width=width,
        padding=padding,
    )
    console.print(panel)

def show_help_panel(
    commands: List[Tuple[str, str]],
    *,
    title: Optional[str] = None,
    style: str = "blue",
) -> None:
    """Show a panel with aligned command descriptions.

    Args:
        commands: List of (command, description) tuples
        title: Optional panel title
        style: Border style color
    """
    content = format_command_help(commands)
    show_panel(content, title=title, style=style)

def success_panel(content: str, title: str = "✨  Success") -> None:
    """Show a success message in a green panel."""
    show_panel(content, title=title, style="green")

def error_panel(content: str, title: str = "❌  Error") -> None:
    """Show an error message in a red panel."""
    show_panel(content, title=title, style="red")

def info_panel(content: str, title: str = "ℹ️  Info") -> None:
    """Show an info message in a blue panel."""
    show_panel(content, title=title, style="blue")

def warning_panel(content: str, title: str = "⚠️  Warning") -> None:
    """Show a warning message in a yellow panel."""
    show_panel(content, title=title, style="yellow")