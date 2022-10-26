import datetime
import json
import time
import webbrowser

import click
import requests
from doxa_cli.constants import CLIENT_ID, LOGIN_URL, SCOPE, TOKEN_URL
from doxa_cli.utils import update_doxa_config
from halo import Halo

SPINNER = {
		"interval": 80,
		"frames": [
			"▐⠂       ▌",
			"▐⠈       ▌",
			"▐ ⠂      ▌",
			"▐ ⠠      ▌",
			"▐  ⡀     ▌",
			"▐  ⠠     ▌",
			"▐   ⠂    ▌",
			"▐   ⠈    ▌",
			"▐    ⠂   ▌",
			"▐    ⠠   ▌",
			"▐     ⡀  ▌",
			"▐     ⠠  ▌",
			"▐      ⠂ ▌",
			"▐      ⠈ ▌",
			"▐       ⠂▌",
			"▐       ⠠▌",
			"▐       ⡀▌",
			"▐      ⠠ ▌",
			"▐      ⠂ ▌",
			"▐     ⠈  ▌",
			"▐     ⠂  ▌",
			"▐    ⠠   ▌",
			"▐    ⡀   ▌",
			"▐   ⠠    ▌",
			"▐   ⠂    ▌",
			"▐  ⠈     ▌",
			"▐  ⠂     ▌",
			"▐ ⠠      ▌",
			"▐ ⡀      ▌",
			"▐⠠       ▌"
		]
	}



def wait_for_auth(device_code: str, interval: int, expires_at: datetime.datetime):
    while True:
        now = datetime.datetime.now()
        if now >= expires_at:
            yield "EXPIRED", None
            break

        try:
            res = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "device_code",
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                },
                verify=True,
            ).json()
        except:
            yield "ERROR", None
            break

        if "error" in res:
            if "code" in res["error"] and res["error"]["code"] == "authorization_pending":
                yield "PENDING", None
                time.sleep(interval)
            else:
                yield "AUTH_ERROR", res["error"]
        elif "access_token" in res:
            yield "SUCCESS", res
            break


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
    expires_in = datetime.timedelta(0, data["expires_in"])
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
        click.secho("\n")

    with Halo(text='Waiting for approval', spinner=SPINNER, enabled=True) as spinner:
        for (state, result) in wait_for_auth(device_code, interval, get_device_time + expires_in):
            if state == "PENDING":
                continue

            if state == "EXPIRED":
                spinner.fail("The authorisation request has expired. Please rerun this command and try logging in again.")
            elif state == "ERROR":
                spinner.fail("A CLI error occurred during the authorisation process.")
            elif state == "AUTH_ERROR":
                spinner.fail("An error occurred while attempting to log you in.")
            elif state == "SUCCESS":
                try:
                    update_doxa_config(
                        access_token=result["access_token"],
                        refresh_token=result.get("refresh_token", None),
                        expires_at=datetime.datetime.now()
                        + datetime.timedelta(seconds=result["expires_in"]),
                    )
                    spinner.succeed("Authorisation successful - you are now logged in!")
                except:
                    spinner.fail("A CLI error occurred while logging you in.")
            else:
                spinner.fail("Ooops, a CLI error occurred.")

            break
