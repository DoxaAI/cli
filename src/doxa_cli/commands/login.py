import datetime
import time
import webbrowser

import click
import requests
import typer
from halo import Halo

from doxa_cli.config import CONFIG
from doxa_cli.constants import CLIENT_ID, LOGIN_URL, SCOPE, SPINNER, TOKEN_URL
from doxa_cli.errors import show_error
from doxa_cli.utils import get_request_client


def wait_for_auth(
    session: requests.Session,
    device_code: str,
    interval: int,
    expires_at: datetime.datetime,
):
    while True:
        now = datetime.datetime.now()
        if now >= expires_at:
            yield "EXPIRED", None
            break

        try:
            res = session.post(
                TOKEN_URL,
                json={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                },
                verify=True,
            ).json()
        except:
            yield "ERROR", None
            break

        if "error" in res:
            if res["error"] == "authorization_pending":
                yield "PENDING", None
                time.sleep(interval)
            elif res["error"] == "slow_down":
                yield "PENDING", None
                interval += 5
                time.sleep(interval)
            else:
                yield "AUTH_ERROR", res["error"]
        elif "access_token" in res:
            yield "SUCCESS", res
            break


def get_device_code(session: requests.Session):
    result = session.post(
        LOGIN_URL, json={"client_id": CLIENT_ID, "scope": SCOPE}, verify=True
    ).json()

    assert "device_code" in result
    assert "interval" in result
    assert "verification_uri_complete" in result

    return result


def login():
    """Log in with your DOXA AI platform account."""

    now = datetime.datetime.now()
    session = get_request_client()

    try:
        data = get_device_code(session)
    except:
        show_error(
            "\nAn error occurred while initiating the authorisation process. Please try again later."
        )
        raise typer.Exit(1)

    click.secho(
        "\nUse the link below to log into the CLI using your DOXA account:",
        fg="green",
        bold=True,
    )
    click.secho("\t" + data["verification_uri_complete"])

    try:
        webbrowser.open(data["verification_uri_complete"], 2, False)
        click.secho(
            "\nThe verification link has been opened in your default browser.\n",
            fg="green",
            bold=True,
        )
    except:
        typer.echo("\n")

    expires_at = now + datetime.timedelta(seconds=data["expires_in"])

    with Halo(text="Waiting for approval", spinner=SPINNER, enabled=True) as spinner:
        for state, result in wait_for_auth(
            session, data["device_code"], data["interval"], expires_at
        ):
            if state == "PENDING":
                continue

            if state == "EXPIRED":
                spinner.fail(
                    "The authorisation request has expired. Please rerun this command and try logging in again."
                )
            elif state == "ERROR":
                spinner.fail("A CLI error occurred during the authorisation process.")
            elif state == "AUTH_ERROR":
                spinner.fail("An error occurred while attempting to log you in.")
            elif state == "SUCCESS" and result is not None:
                try:
                    CONFIG.update(
                        {
                            "access_token": result["access_token"],
                            "refresh_token": result.get("refresh_token", None),
                            "expires_at": datetime.datetime.now()
                            + datetime.timedelta(seconds=result["expires_in"]),
                        }
                    )
                    spinner.succeed(
                        "Authorisation successful - you have now been logged in!"
                    )
                    return
                except:
                    spinner.fail("A CLI error occurred while logging you in.")
            else:
                spinner.fail("Ooops, a CLI error occurred.")

            raise typer.Exit(1)
