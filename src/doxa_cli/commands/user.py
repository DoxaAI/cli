import datetime
import json

import click
import requests
from doxa_cli.constants import USER_URL
from doxa_cli.errors import (
    BrokenConfigurationError,
    LoggedOutError,
    SessionExpiredError,
)
from doxa_cli.utils import (
    get_access_token,
    print_line,
    show_error,
    try_to_fix_broken_config,
)


@click.command()
@click.option("-e", "--extra", type=bool, default=False, is_flag=True, hidden=True)
def user(extra):
    """Display DOXA account information. You must be logged in."""

    try:
        access_token = get_access_token()
    except LoggedOutError:
        click.secho(
            "\nYou must be logged in to show user information.", fg="cyan", bold=True
        )
        return
    except BrokenConfigurationError:
        click.secho(
            "\nOops, the DOXA CLI configuration file could not be read properly.\n",
            fg="yellow",
            bold=True,
        )
        try_to_fix_broken_config()
        return
    except SessionExpiredError:
        click.secho(
            "\nYour session has expired. Please log in again.",
            fg="yellow",
            bold=True,
        )
        return
    except:
        show_error("\nAn error occurred while performing this command.")
        return

    try:
        data = requests.post(
            USER_URL, headers={"Authorization": f"Bearer {access_token}"}, verify=True
        ).json()["user"]
    except:
        show_error(
            "Oops, your user information could not be fetched at this time. You might wish to try logging in again."
        )
        return

    click.secho(
        f"\nHello, {data['username']}! Here are your account details:\n",
        fg="green",
        bold=True,
    )

    if extra:
        print_line("User ID", data["id"])

    print_line("Username", data["username"])
    print_line("Email", data["email"])

    if data.get("competitions", None):
        print_line("Competitions", ", ".join(data["competitions"]))

    if extra and data.get("roles", None):
        print_line("Roles", ", ".join(role["name"] for role in data["roles"]))

    if extra and "verified" in data:
        print_line("Verified", str(data["verified"]).lower())

    if extra and "metadata" in data:
        print_line("Metadata", json.dumps(data["metadata"], indent=2))

    if extra and "created_at" in data:
        print_line("Created at", data["created_at"])

    if extra and "updated_at" in data:
        print_line("Updated at", data["updated_at"])

    if data.get("admin", False):
        click.secho(
            "\nYou are an admin. With great power comes great responsibility.",
            fg="blue",
            bold=True,
        )

    diff = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(
        data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    click.secho(
        f"\nYou created your account {diff.days} days ago.", fg="green", bold=True
    )
