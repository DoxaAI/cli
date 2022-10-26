import click


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
