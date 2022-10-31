import datetime
import json
import os
import tarfile
import typing

import click
import requests
import yaml

from doxa_cli.constants import CONFIG_DIRECTORY, CONFIG_PATH, DOXA_YAML, TOKEN_URL
from doxa_cli.errors import (
    BrokenConfigurationError,
    LoggedOutError,
    SessionExpiredError,
)


def read_doxa_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

        assert "access_token" in config
        assert "expires_at" in config

        return config


def update_doxa_config(**kwargs) -> None:
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(kwargs, f, default=str)


def clear_doxa_config() -> None:
    os.remove(CONFIG_PATH)
    os.rmdir(CONFIG_DIRECTORY)


def is_refresh_required(expires_at) -> bool:
    return datetime.datetime.now() >= datetime.datetime.strptime(
        expires_at, "%Y-%m-%d %H:%M:%S.%f"
    )


def refresh_oauth_token(data) -> str:
    now = datetime.datetime.now()
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": data["refresh_token"]},
        verify=True,
    )
    access_time = now + r.elapsed
    token = json.loads(r.text)
    access_token = token["access_token"]
    refresh_token = token["refresh_token"]
    expires_in = datetime.timedelta(0, token["expires_in"])

    with open(os.path.join(CONFIG_DIRECTORY, "config.json"), "w") as f:
        json.dump(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": access_time + expires_in,
            },
            f,
            default=str,
        )
    return token["access_token"]


def try_to_fix_broken_config() -> None:
    try:
        clear_doxa_config()
        click.secho("Please log in again to fix this issue.", fg="green", bold=True)
    except:
        show_error("The DOXA CLI was unable to reset its configuration.\n")
        click.echo(
            f"Please manually delete the file at the following path: {CONFIG_PATH}."
        )


def get_access_token() -> None:
    try:
        config = read_doxa_config()
    except FileNotFoundError:
        raise LoggedOutError
    except (ValueError, AssertionError):
        # oops, the config is corrupted!
        raise BrokenConfigurationError

    if is_refresh_required(config["expires_at"]):
        try:
            return refresh_oauth_token()
        except:
            raise SessionExpiredError

    return config["access_token"]


def read_doxa_yaml(directory: str) -> dict:
    path = os.path.join(directory, DOXA_YAML)
    with open(path, "r") as file:
        return yaml.safe_load(file)


def compress_submission_directory(f: typing.IO, directory: str) -> None:
    def reset(tarinfo):
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        return tarinfo

    with tarfile.open(fileobj=f, mode="x:gz", format=tarfile.GNU_FORMAT) as tar:
        for file_name in os.listdir(directory):
            tar.add(os.path.join(directory, file_name), arcname=file_name, filter=reset)

    f.close()


def show_error(message: str, color: str = "red") -> None:
    click.secho(message, fg=color, bold=True)


def print_line(key: str, value: str) -> None:
    click.echo(
        click.style(f"{key + ':':<24}", fg="cyan", bold=True)
        + click.style(value, bold=True)
    )
