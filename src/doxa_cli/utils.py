import datetime
import json
import os

import requests

from doxa_cli.constants import CONFIG_DIRECTORY, CONFIG_PATH, TOKEN_URL


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
