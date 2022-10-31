import datetime
import json

import click
import requests
from doxa_cli.constants import USER_URL
from doxa_cli.utils import get_access_token


def print_line(key: str, value: str):
    click.echo(click.style(f"{key + ':':<20}", fg="cyan", bold=True) + click.style(value, bold=True))


@click.command()
@click.option("-e", "--extra", type=bool, default=False, is_flag=True, hidden=True)
def user(extra):
    """Display DOXA account information. You must be logged in."""

    session_stop, access_token = get_access_token()
    if session_stop:
        return

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


