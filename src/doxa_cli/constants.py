import os
import platform

import appdirs

VERSION = "0.1"

DOXA_BASE_URL = os.environ.get("DOXA_BASE_URL", "https://doxaai.com")

LOGIN_URL = f"{DOXA_BASE_URL}/api/oauth/device/code"
TOKEN_URL = f"{DOXA_BASE_URL}/api/oauth/token"
USER_URL = f"{DOXA_BASE_URL}/api/oauth/user"
UPLOAD_SLOT_URL = f"{DOXA_BASE_URL}/api/extern/upload-slot"

CLIENT_ID = "eb594ca3-023d-477f-823a-22e48f4e5235"
SCOPE = "basic"


def get_config_directory():
    directory = os.environ.get("DOXA_CONFIG_DIRECTORY")
    if directory and os.path.isabs(directory):
        return directory

    if platform.system() == "Darwin":
        return appdirs.user_data_dir(appname="doxa", version=VERSION)

    return appdirs.user_config_dir(appname="doxa", version=VERSION)


CONFIG_DIRECTORY = get_config_directory()
CONFIG_PATH = os.path.join(CONFIG_DIRECTORY, "config.json")

DOXA_YAML = "doxa.yaml"
COMPETITION_KEY = "competition"
ENVIRONMENT_KEY = "environment"

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
