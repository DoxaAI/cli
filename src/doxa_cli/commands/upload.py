import os
import sys
import tempfile
import typing
from urllib.parse import urljoin

import click
import requests
from halo import Halo
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from doxa_cli.constants import (
    BOUNCING_BAR,
    COMPETITION_KEY,
    DOXA_STORAGE_URL,
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
    clear_doxa_config,
    compress_submission_directory,
    get_access_token,
    read_doxa_yaml,
    show_error,
    try_to_fix_broken_config,
)


@click.command()
@click.argument("directory", nargs=1, type=str)
@click.option("--competition", "-c", default=None, show_default=False, type=str)
@click.option("--environment", "-e", default=None, show_default=False, type=str)
def upload(directory, competition, environment):
    """Upload and submit an agent to the DOXA AI platform."""

    # Step 0: ensure that the user is logged in!

    try:
        access_token = get_access_token()
    except LoggedOutError:
        show_error(
            "\nYou must be logged in to upload a submission to the DOXA AI platform."
        )
        sys.exit(1)
    except BrokenConfigurationError:
        show_error(
            "\nOops, the DOXA AI CLI configuration file could not be read properly.\n"
        )
        try_to_fix_broken_config()
        sys.exit(1)
    except SessionExpiredError:
        show_error("\nYour session has expired. Please log in again.")
        clear_doxa_config()
        sys.exit(1)
    except Exception as e:
        show_error("\nAn error occurred while performing this command.", exception=e)
        sys.exit(1)

    # Step 1: read {directory}/doxa.yaml and verify that it is valid, e.g.

    # competition: {competition tag}
    # environment: {environment tag}
    # language: python
    # entrypoint: run.py

    if not os.path.exists(directory):
        show_error(f"\nThe directory `{directory}` does not exist.")
        sys.exit(1)

    try:
        user_config = read_doxa_yaml(directory)
    except FileNotFoundError:
        show_error(
            "\nYour submission folder must contain a `doxa.yaml` file. Please check the DOXA AI website for further guidance."
        )
        sys.exit(1)
    except Exception as e:
        show_error(
            "\nThere was an error reading the `doxa.yaml` file in your submission. Please check its syntax.",
            exception=e,
        )
        sys.exit(1)

    # we can override competition and environment with command-line options,
    competition = competition or user_config.get(COMPETITION_KEY)
    environment = environment or user_config.get(ENVIRONMENT_KEY)

    user_config.pop("competition", None)
    user_config.pop("environment", None)

    if not competition:
        show_error(
            "\nYou must specify a competition.\n\nYou can do so by inserting `competition: [COMPETITION TAG]` into the `doxa.yaml` file in your submission folder or by using the --competition/-c command-line option.\n\nRun this command with --help for more information."
        )
        sys.exit(1)

    if not environment:
        show_error(
            "\nYou must specify an execution environment.\n\nYou can do so by inserting `environment: [ENVIRONMENT TAG]` into the `doxa.yaml` file in your submission folder or by using the --environment/-e command-line option.\n\nRun this command with --help for more information."
        )
        sys.exit(1)

    # Step 2: produce tar.gz of {directory} using `tarfile` module

    try:
        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".tar.gz", delete=False, mode="w+b"
        )
    except Exception as e:
        show_error("An error occurred creating a temporary file.", exception=e)
        sys.exit(1)

    print()
    with Halo(text="Compressing your submission.", spinner=BOUNCING_BAR) as spinner:
        try:
            compress_submission_directory(temporary_file, directory)
            spinner.succeed("Successfully compressed your submission")
        except:
            spinner.fail("Unable to compress your submission directory")
            os.unlink(temporary_file.name)
            sys.exit(1)

    # Step 3: POST /api/extern/upload-slot

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

        base_url = DOXA_STORAGE_URL or upload_slot["endpoint"]
        if not base_url.endswith("/"):
            base_url += "/"

        upload_endpoint = urljoin(base_url, "upload")
        upload_token = upload_slot["token"]
    except UploadSlotDeniedError as e:
        if e.doxa_error_code in (
            "COMPETITION_TAG_INVALID",
            "ENVIRONMENT_TAG_INVALID",
            "COMPETITION_NOT_FOUND",
            "COMPETITION_CLOSED",
            "ENROLMENT_NOT_FOUND",
            "ENVIRONMENT_INVALID",
            "STORAGE_NODE_NOT_FOUND",
            "UNKNOWN",
        ):
            show_error(f"\n{e.doxa_error_message}")
        elif e.doxa_error_code == "UPLOAD_RATE_LIMIT_REACHED":
            show_error("\nYour upload could not be processed.\n")
            click.secho(e.doxa_error_message, bold=True)
        elif e.doxa_error_code == "METADATA_INVALID":
            show_error(
                "\nThe metadata provided in your `doxa.yaml` file is invalid, so your upload could not be processed."
            )

            if e.doxa_error_message:
                show_error(
                    f"\nThe server platform the following reason: {e.doxa_error_message}"
                )
        else:
            show_error(
                "\nAn error occurred while requesting an upload slot, so your upload could not be processed.",
                exception=e,
            )

        os.unlink(temporary_file.name)
        sys.exit(1)
    except Exception as e:
        show_error(
            "\nAn error occurred while requesting an upload slot. Please try again later.",
            exception=e,
        )
        os.unlink(temporary_file.name)
        sys.exit(1)

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
                    "Uploading your submission",
                    fg="cyan",
                    bold=True,
                ),
                bar_template=f"%(label)s {click.style('[', bold=True)}%(bar)s{click.style(']', bold=True)} {click.style('%(info)s', bold=True)}",
                fill_char=click.style("#", fg="blue"),
            ) as bar:

                def callback(m):
                    bar.update(m.bytes_read)

                result = upload_agent(
                    upload_endpoint, upload_token, temporary_file.name, f, callback
                )

                if result.get("success", False):
                    bar.update(size)
                else:
                    raise UploadError
    except Exception as e:
        show_error(
            "\nOops, there was an error uploading your submission to DOXA.", exception=e
        )
        sys.exit(1)
    finally:
        os.unlink(temporary_file.name)

    # Step 5: print success message!

    click.secho(
        "\nYour submission has been successfully uploaded to the DOXA AI platform!",
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
    file_name: str,
    file: typing.IO,
    callback: typing.Callable,
):
    m = MultipartEncoderMonitor(MultipartEncoder(fields={file_name: file}), callback)

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
