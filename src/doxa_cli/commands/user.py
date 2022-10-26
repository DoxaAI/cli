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


@click.command()
def user():
    """Display information on the currently logged in user."""

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
            "Oops, your user information could not be fetched at this time.",
            fg="red",
            bold=True,
        )
        return

    click.secho(
        f"\nHello, you are currently logged in as {click.style(data['username'], fg='cyan', bold=True)}{click.style('!', fg='green', bold=True)}\n",
        fg="green",
        bold=True,
    )
    if data.get("admin", False):
        click.secho("[You are an admin.]\n", fg="cyan", bold=True)

    diff = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.strptime(
        data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    click.echo(
        f'{click.style("You created your account ", fg="green", bold=True)}{click.style(f"{diff.days} days ago", bold=True)}{click.style(".", fg="green", bold=True)}'
    )
