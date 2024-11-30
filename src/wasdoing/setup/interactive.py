"""Interactive setup wizard for Was Doing"""

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .config import get_config_path, create_context

console = Console()

def setup_wizard() -> bool:
    """
    Run the interactive setup wizard.
    Returns True if setup was successful, False otherwise.
    """
    try:
        console.print("\n Welcome to Was Doing Setup!\n")

        # Get or create config directory
        config_dir = get_config_path()
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create contexts directory
        contexts_dir = config_dir / "contexts"
        contexts_dir.mkdir(exist_ok=True)

        # Ask user to create their first context
        if Confirm.ask("Would you like to create your first context?"):
            while True:
                context_name = Prompt.ask("Enter a name for your context")
                if create_context(context_name):
                    console.print(f"\n✅ Created context: {context_name}")
                    break
                console.print("[red]Failed to create context. Please try again.[/red]")

        console.print("\n✨ Setup complete! You can now start using Was Doing.\n")
        console.print("Quick start:")
        console.print("  - List contexts: doc --list-contexts")
        console.print("  - Switch context: doc --context <name>")
        console.print("  - Add history: doc --add-history \"what you did\"")
        console.print("  - Add summary: doc --add-summary \"summary of work\"")

        return True

    except Exception as e:
        console.print(f"[red]Setup failed: {str(e)}[/red]")
        return False 