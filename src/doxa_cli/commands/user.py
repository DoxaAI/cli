import datetime
import json

import click
import requests
from doxa_cli.constants import CONFIG_PATH, USER_URL
from doxa_cli.utils import (
    clear_doxa_config,
    is_refresh_required,
    read_doxa_config,
    refresh_oauth_token,
)


def print_line(key: str, value: str):
    click.echo(click.style(f"{key + ':':<20}", fg="cyan", bold=True) + click.style(value, bold=True))


@click.command()
@click.option("-e", "--extra", type=bool, default=False, is_flag=True, hidden=True)
def user(extra):
    """Display DOXA account information. You must be logged in."""

    try:
        config = read_doxa_config()
    except FileNotFoundError:
        click.secho(
            "\nYou must be logged in to show user information.", fg="cyan", bold=True
        )
        return
    except (ValueError, AssertionError):
        # oops, the config is corrupted!
        click.secho(
            "\nOops, the DOXA CLI configuration file could not be read properly.\n",
            fg="yellow",
            bold=True,
        )

        try:
            clear_doxa_config()
            click.secho("Please log in again to fix this issue.", fg="green", bold=True)
        except:
            click.secho(
                "The DOXA CLI was unable to reset its configuration.\n",
                fg="red",
                bold=True,
            )
            click.secho(
                f"Please manually delete the file at the following path: {CONFIG_PATH}."
            )

        return

    if is_refresh_required(config["expires_at"]):
        try:
            access_token = refresh_oauth_token()
        except:
            click.secho(
                "\nYour session has expired. Please log in again.",
                fg="yellow",
                bold=True,
            )
            return
    else:
        access_token = config["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        r = requests.post(USER_URL, headers=headers, verify=True)
        data = json.loads(r.text)["user"]
    except:
        click.secho(
            "Oops, your user information could not be fetched at this time. You might wish to try logging in again.",
            fg="red",
            bold=True,
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
        click.secho("\nYou are an admin. With great power comes great responsibility.", fg="blue", bold=True)

    diff = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(
        data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    click.secho(
        f"\nYou created your account {diff.days} days ago.", fg="green", bold=True
    )
