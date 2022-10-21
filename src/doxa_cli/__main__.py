import click


@click.command()
def main():
    """The DOXA CLI is the primary tool for uploading agents to DOXA."""

    # Fancy welcome message!

    click.secho("Hello, world!", bold=True, fg="green")


@click.command()
def login():
    """Log in with your DOXA account."""

    # Step 1: POST https://doxaai.com/api/oauth/device/code

    # Request:
    # {
    #     "client_id": "eb594ca3-023d-477f-823a-22e48f4e5235",
    #     "scope": "basic"
    # }

    # Response:
    # {
    #     "device_code": "UUID",
    #     "user_code": "{user_code}",
    #     "expires_in": 900,
    #     "interval": 5,
    #     "verification_uri": "https://doxaai.com/oauth/device",
    #     "verification_uri_complete": "https://doxaai.com/oauth/device/{user_code}"
    # }

    # Step 2: display `verification_uri_complete` and automatically open
    #         the URL in their browser using the webbrowser module

    # while the user is authorising the CLI, show a fun spinner!

    # Step 3: POST https://doxaai.com/api/oauth/token
    #         we want to poll this endpoint every {interval} seconds no longer
    #         than for {expires_in} seconds

    # Request:
    # {
    #     "grant_type": "device_code",
    #     "client_id": "eb594ca3-023d-477f-823a-22e48f4e5235",
    #     "device_code": "{device_code from the previous request}"
    # }

    # Response (while the user has not yet authorised the CLI application):
    # { "error": { "code": "authorization_pending" } }

    # Response (when the user has authorised the CLI application):
    # {
    #     "access_token": "{access_token}",
    #     "expires_in": 86400,
    #     "refresh_token": "{refresh_token}",
    #     "token_type": "Bearer"
    # }
    # in the future, there will also be an id_token we will want to handle!

    # Step 4: Store the access_token and refresh_token in ~/.doxa/config.json

    click.secho("TODO", bold=True, fg="green")


@click.command()
def logout():
    """Log out of your DOXA account."""

    # clear the values from ~/.doxa/config.json

    click.secho("TODO", bold=True, fg="green")


@click.command()
def user():
    """Display information on the currently logged in user."""

    # Step 1: GET https://doxaai.com/api/oauth/user
    # Headers:
    # - Authorization: Bearer {access_token}

    # Response:
    # {
    #     "user": {
    #         "id": 123,
    #         "email": "{email}",
    #         "username": "{username}",
    #         "admin": false,
    #         "metadata": {},
    #         "created_at": "2022-10-17T19:09:51.618838+00:00",
    #         "updated_at": "2022-10-17T19:09:51.618838+00:00",
    #         "verified": false
    #     }
    # }

    # Step 2: print it out prettily (with colour!)

    click.secho("TODO", bold=True, fg="green")


@click.command()
@click.argument("directory", nargs=1, type=str)
@click.option("--competition", "-c", default=None, show_default=False, type=str)
@click.option("--environment", "-e", default=None, show_default=False, type=str)
def upload(directory, competition, environment):
    """Upload and submit an agent to DOXA."""

    # Step 1: read {directory}/doxa.yaml and verify that it is valid, e.g.

    # competition: uttt
    # environment: cpu
    # language: python
    # entrypoint: evaluate.py

    # we can override competition and environment with command-line options,
    # which we should validate if used

    # if the user does not specify an environment, maybe could let it be the
    # default environment (?)

    # Step 2: POST /api/extern/upload-slot

    # Headers:
    # - Authorization: Bearer {access token}

    # Request:
    # {
    #   "competition_tag": "uttt",
    #   "environment_tag": "cpu"
    # }

    # Response (success):
    # { "success": true, "endpoint": "https://local-1.storage.doxaai.com/...", "token": "..." }

    # Response (failure):
    # { "success": false, "error": { "message": "error msg" } }

    # Step 3: produce tar.gz of {directory} using `tarfile` module

    # Step 4:`upload the tarfile to {endpoint} making sure to pass in the header
    # - Authorization: Bearer {token from step 2}

    # show a fancy progress bar of the upload!

    # Step 5: print success message! (or error message)

    click.secho("TODO", bold=True, fg="green")


if __name__ == "__main__":
    main()
