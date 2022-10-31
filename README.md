# DOXA CLI

The DOXA CLI is the primary tool for uploading and submitting agents to [DOXA](http://doxaai.com/): a powerful platform for hosting engaging artificial intelligence competitions.

🔗 Compete on [DOXA](http://doxaai.com/)

➡️ Join the [DOXA Community on Discord](https://discord.gg/MUvbQ3UYcf)


## Installation

The DOXA CLI may be installed using `pip` in the following way:

```py
pip install doxa-cli
```

## Using the DOXA CLI

Assuming you have your Python `Scripts` folder on your `PATH`, you can use the DOXA CLI via the `doxa` command in your shell. Otherwise, you will have to use `python -m doxa_cli` (or `python3 -m doxa_cli` on some systems) to access DOXA CLI commands.

### Logging into the CLI with your DOXA account

Before you can upload agents to DOXA using the CLI, you must first log in with your DOXA account by running the following command:
```bash
doxa login
```

If supported, this will open an authorisation prompt in your default browser. If you are not already logged in on [doxaai.com](https://doxaai.com/), you will first be invited to do so. Thereafter, you wil be asked to authorise the DOXA CLI to have access to your DOXA account. Once you signify your approval, the DOXA CLI will automatically log you in within a few seconds.

By default, the DOXA CLI will store its configuration in a location that follows the norm for your operating system (e.g. within `%APPDATA%\doxa\doxa` on Windows, `~/Library/Application Support/doxa` on macOS and `~/.config/doxa` on Linux). You can find this location by running `doxa config`. If for whatever reason you would like to store the DOXA CLI configuration elsewhere (e.g. due to a permissions issue), you may use a different directory by setting the `DOXA_CONFIG_DIRECTORY` environment variable.

### Logging out

You may log out by running the following command:
```bash
doxa logout
```

### Retrieving user information

You can retrieve information on the user account with which you are currently logged in by performing the following command:
```bash
doxa user
```

### Uploading agents to DOXA

You may upload and submit agents to DOXA using the following command:

```bash
doxa upload [AGENT DIRECTORY]
```

The agent directory must contain a `doxa.yaml` file informing DOXA how to process your submission.

The following is an example of the contents of one such `doxa.yaml` file:
```yaml
competition: uttt
environment: cpu
language: python
entrypoint: evaluate.py
```
