import sys

import click
import requests

from doxa_cli.constants import USER_URL
from doxa_cli.errors import (
    BrokenConfigurationError,
    LoggedOutError,
    SessionExpiredError,
)
from doxa_cli.utils import (
    clear_doxa_config,
    get_access_token,
    print_line,
    show_error,
    try_to_fix_broken_config,
)


@click.command()
def user():
    """Display DOXA account information. You must be logged in."""

    try:
        access_token = get_access_token()
    except LoggedOutError:
        click.secho(
            "\nYou must be logged in to show user information.", fg="cyan", bold=True
        )
        sys.exit(1)
    except BrokenConfigurationError:
        click.secho(
            "\nOops, the DOXA CLI configuration file could not be read properly.\n",
            fg="yellow",
            bold=True,
        )
        try_to_fix_broken_config()
        sys.exit(1)
    except SessionExpiredError:
        click.secho(
            "\nYour session has expired. Please log in again.",
            fg="yellow",
            bold=True,
        )
        clear_doxa_config()
        sys.exit(1)
    except Exception as e:
        show_error("\nAn error occurred while performing this command.", exception=e)
        sys.exit(1)

    try:
        data = requests.get(
            USER_URL, headers={"Authorization": f"Bearer {access_token}"}, verify=True
        ).json()
    except Exception as e:
        print("error", e)
        show_error(
            "Oops, your user information could not be fetched at this time. You might wish to try logging in again."
        )
        sys.exit(1)

    click.secho(
        f"\nHello, {data['preferred_username']}! Here are your account details:\n",
        fg="green",
        bold=True,
    )

    print_line("Username", data["preferred_username"])
    print_line("Email", data["email"])
    print_line("Tag", data["sub"])
