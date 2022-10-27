import os
from pathlib import Path

DOXA_BASE_URL = os.environ.get("DOXA_BASE_URL", "https://doxaai.com")

LOGIN_URL = f"{DOXA_BASE_URL}/api/oauth/device/code"
TOKEN_URL = f"{DOXA_BASE_URL}/api/oauth/token"
USER_URL = f"{DOXA_BASE_URL}/api/oauth/user"

CLIENT_ID = "eb594ca3-023d-477f-823a-22e48f4e5235"
SCOPE = "basic"

CONFIG_DIRECTORY = os.environ.get("DOXA_CONFIG_DIRECTORY", os.path.join(Path.home(), ".doxa"))
CONFIG_PATH = os.path.join(CONFIG_DIRECTORY, "config.json")

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
