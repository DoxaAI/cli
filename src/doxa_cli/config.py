import json
import os
import shutil
from typing import Any

import typer

from doxa_cli.constants import CONFIG_DIRECTORY, CONFIG_PATH, VERSION
from doxa_cli.errors import show_error

DEFAULT_PROFILE = "default"


class Config:
    config: dict[str, Any]
    profile: str

    def __init__(self) -> None:
        self.config = {}
        self.profile = DEFAULT_PROFILE

    def _generate_fresh_config(self):
        return {"version": VERSION, "profiles": {DEFAULT_PROFILE: {}}}

    def _load(self) -> None:
        try:
            with open(CONFIG_PATH, "r") as f:
                self.config = json.load(f)
                if self.config.get("version") != VERSION:
                    raise ValueError

                self.profile = self.config.get("profile", DEFAULT_PROFILE)
                assert self.profile in self.config.get("profiles", {})
        except (json.JSONDecodeError, ValueError):
            self.clear()  # clear invalid configuration files
            self.config = self._generate_fresh_config()
        except FileNotFoundError:
            self.config = self._generate_fresh_config()
        except OSError:
            show_error(
                f"\nThe DOXA CLI configuration file at `{CONFIG_PATH}` could not be read properly. If this location is not readable, you may specify an alternative configuration directory by setting the `DOXA_CONFIG_DIRECTORY` environment variable."
            )
            raise typer.Exit(1)

    def get(self, key: str, default=None):
        if not self.config:
            self._load()

        return self.config["profiles"][self.profile].get(key, default)

    def update(self, values: dict[str, Any]):
        if not self.config:
            self._load()

        self.config["profiles"][self.profile].update(values)

        try:
            os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f, default=str)
        except OSError:
            show_error(
                f"\nThe DOXA CLI configuration file at `{CONFIG_PATH}` could not be written properly. If this location is not writable, you may specify an alternative configuration directory by setting the `DOXA_CONFIG_DIRECTORY` environment variable."
            )
            raise typer.Exit(1)

    def clear(self):
        try:
            shutil.rmtree(CONFIG_DIRECTORY)
        except:
            show_error(
                f"\nThe DOXA CLI was unable to reset its configuration.\n\nPlease manually delete the file at the following path: {CONFIG_PATH}\n\n",
            )
            raise typer.Exit(1)


CONFIG = Config()
