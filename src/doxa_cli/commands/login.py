import datetime
import json
import os
import time
import webbrowser

import click
import requests
from doxa_cli.constants import CLIENT_ID, CONFIG_DIRECTORY, LOGIN_URL, SCOPE, TOKEN_URL
from doxa_cli.utils import update_doxa_config


@click.command()
def login():
    """Log in with your DOXA account."""

    now = datetime.datetime.now()
    r = requests.post(
        LOGIN_URL, data={"client_id": CLIENT_ID, "scope": SCOPE}, verify=True
    )
    get_device_time = now + r.elapsed

    data = json.loads(r.text)
    device_code = data["device_code"]
    interval = data["interval"]
    expire = datetime.timedelta(0, data["expires_in"])
    click.secho(
        "\nUse the link below to log into the CLI using your DOXA account:",
        fg="green",
        bold=True,
    )
    click.secho(data["verification_uri_complete"])

    try:
        webbrowser.open(data["verification_uri_complete"], 2, False)
        click.secho(
            "\nThe verification link has been opened in your default browser.\n",
            fg="green",
            bold=True,
        )
    except:
        click.secho("\n")

    while True:
        if datetime.datetime.now() < get_device_time + expire:
            try:
                now = datetime.datetime.now()
                r = requests.post(
                    TOKEN_URL,
                    data={
                        "grant_type": "device_code",
                        "client_id": CLIENT_ID,
                        "device_code": device_code,
                    },
                    verify=True,
                )

                if "error" in r.text:
                    click.secho("Authorisation pending...")

                else:
                    access_time = now + r.elapsed
                    click.secho(
                        "\nAuthorisation successful - you are now logged in!",
                        fg="green",
                        bold=True,
                    )

                    token = json.loads(r.text)

                    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)

                    try:
                        update_doxa_config(
                            access_token=token["access_token"],
                            refresh_token=token.get("refresh_token", None),
                            expires_at=access_time
                            + datetime.timedelta(seconds=token["expires_in"]),
                        )
                    except:
                        click.secho(
                            "\nA CLI error occurred while logging you in.",
                            fg="red",
                            bold=True,
                        )

                    return
            except ValueError:
                click.secho(
                    "Ooops, an error occurred while logging you in.",
                    fg="red",
                    bold=True,
                )
                return

            time.sleep(interval)
        else:
            click.secho(
                "\nDevice code expired. Please try logging in again.",
                fg="red",
                bold=True,
            )
            return
