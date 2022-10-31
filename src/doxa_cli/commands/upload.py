import os
import tempfile
import typing
from urllib.parse import urljoin

import click
import requests
from doxa_cli.constants import (
    BOUNCING_BAR,
    COMPETITION_KEY,
    ENVIRONMENT_KEY,
    UPLOAD_SLOT_URL,
)
from doxa_cli.errors import (
    BrokenConfigurationError,
    LoggedOutError,
    SessionExpiredError,
    UploadError,
    UploadSlotDeniedError,
)
from doxa_cli.utils import (
    compress_submission_directory,
    get_access_token,
    read_doxa_yaml,
    show_error,
    try_to_fix_broken_config,
)
from halo import Halo
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


@click.command()
@click.argument("directory", nargs=1, type=str)
@click.option("--competition", "-c", default=None, show_default=False, type=str)
@click.option("--environment", "-e", default=None, show_default=False, type=str)
def upload(directory, competition, environment):
    """Upload and submit an agent to DOXA."""

    # Step 0: ensure that the user is logged in!

    try:
        access_token = get_access_token()
    except LoggedOutError:
        show_error("\nYou must be logged in to upload a submission to DOXA.")
        return
    except BrokenConfigurationError:
        show_error(
            "\nOops, the DOXA CLI configuration file could not be read properly.\n"
        )
        try_to_fix_broken_config()
        return
    except SessionExpiredError:
        show_error("\nYour session has expired. Please log in again.")
        return
    except:
        show_error("\nAn error occurred while performing this command.")
        return

    # Step 1: read {directory}/doxa.yaml and verify that it is valid, e.g.

    # competition: {competition tag}
    # environment: {environment tag}
    # language: python
    # entrypoint: run.py

    if not os.path.exists(directory):
        show_error(f"\nThe directory `{directory}` does not exist.")
        return

    try:
        user_config = read_doxa_yaml(directory)
    except FileNotFoundError:
        show_error(
            "\nYour submission folder must contain a `doxa.yaml` file. Please check the DOXA website for guidance on what to include within it."
        )
        return
    except:
        show_error(
            "\nThere was an error reading the `doxa.yaml` file in your submission. Please check its syntax."
        )
        return

    # we can override competition and environment with command-line options,
    competition = competition or user_config.get(COMPETITION_KEY)
    environment = environment or user_config.get(ENVIRONMENT_KEY)

    user_config.pop("competition", None)
    user_config.pop("environment", None)

    if not competition:
        show_error(
            "\nYou must specify a competition.\n\nYou can do so by inserting `competition: [COMPETITION TAG]` into the `doxa.yaml` file in your submission folder or by using the --competition/-c command-line option.\n\nRun this command with --help for more information."
        )
        return

    if not environment:
        show_error(
            "\nYou must specify an execution environment.\n\nYou can do so by inserting `environment: [ENVIRONMENT TAG]` into the `doxa.yaml` file in your submission folder or by using the --environment/-e command-line option.\n\nRun this command with --help for more information."
        )
        return

    # Step 2: POST /api/extern/upload-slot

    # Headers:
    # - Authorization: Bearer {access token}

    # Request:
    # {
    #   "competition_tag": "uttt",
    #   "environment_tag": "cpu",
    #   "metadata": { ... }
    # }

    # Response (success):
    # { "success": true, "endpoint": "https://local.storage.doxaai.com/...", "token": "..." }

    # Response (failure):
    # { "success": false, "error": { "code": "ERROR_CODE", "message": "error msg" } }

    try:
        upload_slot = get_upload_slot(
            access_token, competition, environment, user_config
        )

        upload_endpoint = urljoin(upload_slot["endpoint"], "upload")
        upload_token = upload_slot["token"]
    except UploadSlotDeniedError as e:
        if e.doxa_error_code in (
            "INVALID_COMPETITION_TAG",
            "INVALID_ENVIRONMENT_TAG",
            "COMPETITION_NOT_FOUND",
            "ENROLMENT_NOT_FOUND",
            "ENVIRONMENT_NOT_FOUND",
            "STORAGE_NODE_NOT_FOUND",
        ):
            show_error(f"\n{e.doxa_error_message}")
        elif e.doxa_error_code == "INVALID_METADATA":
            show_error(
                "\nYour upload could not be processed; the metadata provided in your `doxa.yaml` file is invalid."
            )

            if e.doxa_error_message:
                show_error(
                    f"\nThe server gave the following reason: {e.doxa_error_message}"
                )
        else:
            show_error(
                "\nAn error occurred while requesting an upload slot, so your upload could not be processed."
            )

        return
    except:
        show_error(
            "\nAn error occurred while requesting an upload slot. Please try again later."
        )
        return

    # Step 3: produce tar.gz of {directory} using `tarfile` module

    try:
        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".tar.gz", delete=False, mode="w+b"
        )
    except:
        show_error("An error occurred creating a temporary file.")
        return

    print()
    with Halo(text="Compressing your submission.", spinner=BOUNCING_BAR) as spinner:
        try:
            compress_submission_directory(temporary_file, directory)
            spinner.succeed("Successfully compressed your submission")
        except:
            spinner.fail("Unable to compress your submission directory")
            return

    # Step 4:`upload the tarfile to {endpoint} making sure to pass in the header
    # - Authorization: Bearer {token from step 2}

    print()
    try:
        size = os.path.getsize(temporary_file.name)
        with open(temporary_file.name, "rb") as f:
            # show a fancy progress bar of the upload!
            with click.progressbar(
                length=size,
                label=click.style(
                    "Uploading your submission to DOXA",
                    fg="cyan",
                    bold=True,
                ),
                bar_template=f"%(label)s {click.style('[', bold=True)}%(bar)s{click.style(']', bold=True)} {click.style('%(info)s', bold=True)}",
                fill_char=click.style("#", fg="blue"),
            ) as bar:

                def callback(m):
                    bar.update(m.bytes_read)

                result = upload_agent(upload_endpoint, upload_token, f, callback)
                if result.get("success", False):
                    bar.update(size)
                else:
                    raise UploadError
    except:
        show_error("Oops, there was an error uploading your submission to DOXA.")
        return
    finally:
        os.unlink(temporary_file.name)

    # Step 5: print success message!

    click.secho(
        "\nCongratulations - your submission was successfully uploaded to DOXA!",
        fg="green",
        bold=True,
    )


def get_upload_slot(access_token, competition, environment, metadata):
    result = requests.post(
        UPLOAD_SLOT_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "competition_tag": competition,
            "environment_tag": environment,
            "metadata": metadata,
        },
        verify=True,
    ).json()

    try:
        assert "success" in result
        assert "endpoint" in result
        assert "token" in result
        assert "error" not in result
    except:
        if "error" in result:
            raise UploadSlotDeniedError(
                result["error"].get("code"), result["error"].get("message")
            )

        raise AssertionError

    return result


def upload_agent(
    upload_endpoint: str,
    upload_token: str,
    f: typing.IO,
    callback: typing.Callable,
):
    m = MultipartEncoderMonitor(MultipartEncoder(fields={"file": f}), callback)

    result = requests.post(
        upload_endpoint,
        headers={
            "Authorization": f"Bearer {upload_token}",
            "Content-Type": m.content_type,
        },
        data=m,
        verify=True,
    ).json()

    return result
