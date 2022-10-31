import datetime
import json
import os

import requests
import click
import yaml
import tarfile

from doxa_cli.constants import CONFIG_DIRECTORY, CONFIG_PATH, TOKEN_URL, UPLOAD_FILE, UPLOAD_FILE


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


def is_refresh_required(expires_at):
    return datetime.datetime.now() >= datetime.datetime.strptime(
        expires_at, "%Y-%m-%d %H:%M:%S.%f"
    )


def refresh_oauth_token(data):
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

def get_access_token():
    session_stop = True
    access_token = None

    try:
        config = read_doxa_config()
    except FileNotFoundError:
        click.secho(
            "\nYou must be logged in to show user information.", fg="cyan", bold=True
        )
        return (session_stop, access_token)

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

            return (session_stop, access_token)

    if is_refresh_required(config["expires_at"]):
        try:
            access_token = refresh_oauth_token()
        except:
            click.secho(
                "\nYour session has expired. Please log in again.",
                fg="yellow",
                bold=True,
            )
            return (session_stop, access_token)
    else:
        access_token = config["access_token"]
        session_stop = False
        return (session_stop, access_token)

def read_doxa_upload(directory) -> dict:
    path = os.path.join(directory, UPLOAD_FILE)
    with open(path, 'r') as file:
        config = yaml.safe_load (file)

        #assert "competition" in config
        #assert "environment" in config

        return config

def compress_agent_dir(directory) -> None:
    print("compressing the agent directory")
    #path = os.path.join("upload.tar", UPLOAD_FILE)
    file = tarfile.open("directory", "w")
    file.close()