import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from doxa_cli.constants import CONFIG_PATH, DOXA_BASE_URL, DOXA_STORAGE_URL, IS_DEBUG
from doxa_cli.utils import clear_doxa_config, read_doxa_config, show_error


def config(
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
            config = read_doxa_config()

            table.add_row("Access Token", config.get("access_token", "None"))
            table.add_row("Access Token Expiry", config.get("expires_at", "None"))
            table.add_row("Refresh Token", config.get("refresh_token", "None"))
        except FileNotFoundError:
            show_error("\nOops, your configuration file could not be read.")
        except:
            show_error("\nSorry, no debug information is available!")

    console.print(table)

    if reset:
        try:
            clear_doxa_config()
            console.print(
                "\nThe configuration file was deleted successfully.", style="bold green"
            )
        except FileNotFoundError:
            console.log(
                "\nThere is no configuration file at that location to delete.",
                style="bold yellow",
            )
        except:
            show_error(
                "\nThe DOXA CLI was unable to reset its configuration. Please delete the file manually."
            )
