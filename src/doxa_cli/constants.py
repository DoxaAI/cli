import os
import platform

import platformdirs
from rich.theme import Theme

VERSION = "0.1"

IS_DEV = os.environ.get("DOXA_ENV") in ("DEV", "DEVELOPMENT")
IS_DEBUG = IS_DEV or os.environ.get("DOXA_DEBUG") in ("true", "TRUE")

DOXA_BASE_URL = os.environ.get(
    "DOXA_BASE_URL", "http://localhost:3001" if IS_DEV else "https://api.doxaai.com"
)

DOXA_STORAGE_URL = (
    "http://localhost:4002/storage" if IS_DEV else os.environ.get("DOXA_STORAGE_URL")
)

LOGIN_URL = f"{DOXA_BASE_URL}/oauth/device/authorize"
TOKEN_URL = f"{DOXA_BASE_URL}/oauth/token"
USER_URL = f"{DOXA_BASE_URL}/oauth/userinfo"
UPLOAD_SLOT_URL = f"{DOXA_BASE_URL}/upload/slot"

CLIENT_ID = "eb594ca3-023d-477f-823a-22e48f4e5235"
SCOPE = "openid profile email agent"


def get_config_directory():
    directory = os.environ.get("DOXA_CONFIG_DIRECTORY")
    if directory and os.path.isabs(directory):
        return directory

    if platform.system() == "Darwin":
        return platformdirs.user_data_dir(appname="doxa", version=VERSION)

    return platformdirs.user_config_dir(appname="doxa", version=VERSION)


CONFIG_DIRECTORY = get_config_directory()
CONFIG_PATH = os.path.join(CONFIG_DIRECTORY, "config.json")

DOXA_YAML = "doxa.yaml"
COMPETITION_KEY = "competition"
ENVIRONMENT_KEY = "environment"

EXCLUDED_FILES = {"doxa.yaml", "__pycache__", ".ipynb_checkpoints", ".DS_Store"}

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
        "▐⠠       ▌",
    ],
}

BOUNCING_BAR = {
    "interval": 80,
    "frames": [
        "[    ]",
        "[   =]",
        "[  ==]",
        "[ ===]",
        "[====]",
        "[=== ]",
        "[==  ]",
        "[=   ]",
    ],
}

theme = Theme(
    {
        "bar.pulse": "blue",
        "bar.complete": "bold green",
        "bar.finished": "bold green",
        "progress.description": "bold white",
        "progress.percentage": "bold white",
        "progress.download": "white",
        "progress.data.speed": "bold cyan",
    }
)
