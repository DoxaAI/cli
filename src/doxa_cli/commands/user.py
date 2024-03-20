import requests
import typer
from rich.console import Console
from rich.table import Table

from doxa_cli.constants import USER_URL
from doxa_cli.errors import SessionExpiredError, SignedOutError, show_error
from doxa_cli.utils import get_request_client


def user():
    """Display DOXA AI account information. You must be logged in."""

    console = Console()

    try:
        session = get_request_client(require_auth=True)
    except SignedOutError:
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
        data = session.get(USER_URL, verify=True).json()
    except requests.exceptions.JSONDecodeError:
        show_error(
            "Oops, the server returned an invalid response. Please try again later."
        )
        raise typer.Exit(1)
    except:
        show_error(
            "Oops, your user information could not be fetched at this time. You may wish to try logging in again."
        )
        raise typer.Exit(1)

    username = data.get("preferred_username")

    console.print(
        f"\nHello, @{username}! Here are your account details:\n",
        style="bold green",
    )

    table = Table(
        title=f"User Information for @{username}",
        leading=1,
        title_style="bold white",
    )

    table.add_column("Field", style="bold cyan")
    table.add_column("Value", overflow="fold")

    table.add_row("Username", username)
    table.add_row("Email", data.get("email"))
    table.add_row("Tag", data.get("sub"))

    console.print(table)
