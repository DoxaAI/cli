import datetime
import os

import requests
import typer
import yaml

from doxa_cli.config import CONFIG
from doxa_cli.constants import DOXA_YAML, SCOPE, TOKEN_URL, __version__
from doxa_cli.errors import SessionExpiredError, SignedOutError, show_error


def _handle_outdated_cli(r, *args, **kwargs):
    if r.status_code == requests.codes.bad_request:
        body = r.json()
        if (
            "error" in body
            and isinstance(body["error"], dict)
            and body["error"].get("code") == "CLIENT_OUTDATED"
        ):
            show_error(
                body["error"].get(
                    "message",
                    "The version of the DOXA CLI you have installed is outdated. Please install the latest version.",
                )
            )
            raise typer.Exit(1)


def get_request_client(require_auth: bool = False) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": f"DOXA-CLI/{__version__}"})
    session.hooks["response"].append(_handle_outdated_cli)

    if require_auth:
        token = get_access_token()
        if not token:
            raise SignedOutError

        session.headers.update({"Authorization": f"Bearer {token}"})

    return session


def refresh_oauth_token(refresh_token: str) -> str:
    now = datetime.datetime.now()
    data = (
        get_request_client()
        .post(
            TOKEN_URL,
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": SCOPE,
            },
            verify=True,
        )
        .json()
    )

    if "error" in data:
        raise ValueError("Unable to get a refreshed access token")

    CONFIG.update(
        {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token") or refresh_token,
            "expires_at": now + datetime.timedelta(seconds=data["expires_in"]),
        }
    )

    return data["access_token"]


def get_access_token() -> str:
    access_token = CONFIG.get("access_token")
    token_expiry = CONFIG.get("expires_at")

    if not access_token or not token_expiry:
        raise SignedOutError

    if datetime.datetime.now() < datetime.datetime.strptime(
        token_expiry, "%Y-%m-%d %H:%M:%S.%f"
    ):
        return access_token

    refresh_token = CONFIG.get("refresh_token")
    if refresh_token:
        try:
            return refresh_oauth_token(refresh_token)
        except:
            # The refresh token has expired, so clear the config
            CONFIG.clear()

    raise SessionExpiredError


def read_doxa_yaml(directory: str) -> dict:
    path = os.path.join(directory, DOXA_YAML)
    with open(path, "r") as file:
        return yaml.safe_load(file)
