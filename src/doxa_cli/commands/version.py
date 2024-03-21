from rich.console import Console

from doxa_cli.constants import __version__


def version():
    """Gives the version of the DOXA CLI."""

    console = Console()
    console.print(
        f"\n[bold white]You are running DOXA CLI version [bold cyan]{__version__} 😎"
    )
