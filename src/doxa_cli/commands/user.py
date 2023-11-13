import requests
import typer
from rich.console import Console
from rich.table import Table

from doxa_cli.constants import USER_URL
from doxa_cli.errors import LoggedOutError, SessionExpiredError
from doxa_cli.utils import get_access_token, show_error


def user():
    """Display DOXA account information. You must be logged in."""

    console = Console()

    try:
        access_token = get_access_token()
    except LoggedOutError:
        console.print(
            "\nYou must be logged in to see user information.", style="bold cyan"
        )
        raise typer.Exit(1)
    except SessionExpiredError:
        console.print(
            "\nYour session has expired. Please log in again.", style="bold yellow"
        )
        raise typer.Exit(1)
    except:
        show_error()
        raise typer.Exit(1)

    try:
        data = requests.get(
            USER_URL, headers={"Authorization": f"Bearer {access_token}"}, verify=True
        ).json()
    except:
        show_error(
            "Oops, your user information could not be fetched at this time. You may wish to try logging in again."
        )
        raise typer.Exit(1)

    console.print(
        f"\nHello, @{data['preferred_username']}! Here are your account details:\n",
        style="bold green",
    )

    table = Table(
        title=f"User Information for @{data['preferred_username']}",
        leading=1,
        title_style="bold white",
    )

    table.add_column("Field", style="bold cyan")
    table.add_column("Value", overflow="fold")

    table.add_row("Username", data["preferred_username"])
    table.add_row("Email", data["email"])
    table.add_row("Tag", data["sub"])

    console.print(table)
