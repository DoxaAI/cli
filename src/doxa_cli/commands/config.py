import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from doxa_cli.config import CONFIG
from doxa_cli.constants import CONFIG_PATH, DOXA_BASE_URL, DOXA_STORAGE_URL, IS_DEBUG
from doxa_cli.errors import show_error


def config_info(
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Show additional debug information.",
            show_default=False,
        ),
    ] = False,
    reset: Annotated[
        bool,
        typer.Option(
            "--reset", "-r", help="Reset the configuration.", show_default=False
        ),
    ] = False,
):
    console = Console()
    table = Table(title="DOXA AI CLI Configuration", expand=True, leading=1)

    table.add_column("Key", style="bold cyan")
    table.add_column("Value", overflow="fold")

    table.add_row("DOXA API Base URL", DOXA_BASE_URL)

    if DOXA_STORAGE_URL:
        table.add_row("DOXA Storage Override URL", DOXA_STORAGE_URL)

    table.add_row("Configuration Path", CONFIG_PATH)

    if debug or IS_DEBUG:
        try:
            table.add_row("Access Token", CONFIG.get("access_token", "None"))
            table.add_row("Access Token Expiry", CONFIG.get("expires_at", "None"))
            table.add_row("Refresh Token", CONFIG.get("refresh_token", "None"))
        except FileNotFoundError:
            show_error("\nOops, your configuration file could not be read.")
        except:
            show_error("\nSorry, no debug information is available!")

    console.print(table)

    if reset:
        try:
            CONFIG.clear()
            console.print(
                "\nThe configuration file was deleted successfully.", style="bold green"
            )
        except:
            show_error(
                "\nThe DOXA CLI was unable to reset its configuration. Please delete the file manually."
            )
