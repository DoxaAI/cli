import datetime
import json
import os

import requests
import rich
import typer
import yaml

from doxa_cli.constants import (
    CONFIG_DIRECTORY,
    CONFIG_PATH,
    DOXA_YAML,
    IS_DEBUG,
    IS_DEV,
    TOKEN_URL,
)
from doxa_cli.errors import LoggedOutError, SessionExpiredError


def read_doxa_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

        assert "access_token" in config
        assert "expires_at" in config

        return config


def update_doxa_config(**kwargs) -> None:
    try:
        os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(kwargs, f, default=str)
    except OSError:
        show_error(
            f"\nThe DOXA CLI configuration file at `{CONFIG_PATH}` could not be written properly. If this location is not writable, you may specify an alternative configuration directory by setting the `DOXA_CONFIG_DIRECTORY` environment variable."
        )
        raise typer.Exit(1)


def clear_doxa_config() -> None:
    try:
        os.remove(CONFIG_PATH)
        os.rmdir(CONFIG_DIRECTORY)
    except:
        show_error(
            f"\nThe DOXA CLI was unable to reset its configuration.\n\nPlease manually delete the file at the following path: {CONFIG_PATH}\n\n",
        )
        raise typer.Exit(1)


def is_refresh_required(expires_at) -> bool:
    return datetime.datetime.now() >= datetime.datetime.strptime(
        expires_at, "%Y-%m-%d %H:%M:%S.%f"
    )


def refresh_oauth_token(refresh_token: str) -> str:
    now = datetime.datetime.now()
    data = requests.post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        verify=True,
    ).json()

    with open(os.path.join(CONFIG_DIRECTORY, "config.json"), "w") as f:
        json.dump(
            {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": now + datetime.timedelta(seconds=data["expires_in"]),
            },
            f,
            default=str,
        )

    return data["access_token"]


def get_access_token() -> str:
    try:
        config = read_doxa_config()
    except FileNotFoundError:
        raise LoggedOutError
    except OSError:
        show_error(
            f"\nThe DOXA CLI configuration file at `{CONFIG_PATH}` could not be read properly. If this location is not readable, you may specify an alternative configuration directory by setting the `DOXA_CONFIG_DIRECTORY` environment variable."
        )
        raise typer.Exit(1)
    except (ValueError, AssertionError):
        # oops, the config is corrupted!
        show_error(
            "\nOops, the DOXA CLI configuration file could not be read properly. You may need to log in again to fix the issue.\n"
        )
        clear_doxa_config()
        raise typer.Exit(1)

    if is_refresh_required(config["expires_at"]):
        try:
            return refresh_oauth_token(config["refresh_token"])
        except:
            clear_doxa_config()
            raise SessionExpiredError

    return config["access_token"]


def read_doxa_yaml(directory: str) -> dict:
    path = os.path.join(directory, DOXA_YAML)
    with open(path, "r") as file:
        return yaml.safe_load(file)


def show_error(
    message: str = "An error occurred while performing this command.",
    color: str = "red",
) -> None:
    console = rich.console.Console()
    console.print(f"\n{message}\n", style=f"bold {color}")

    if IS_DEV or IS_DEBUG:
        console.print_exception()
