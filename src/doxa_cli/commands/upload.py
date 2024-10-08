import fnmatch
import os
import tarfile
import tempfile
import typing
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin

import requests
import typer
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TransferSpeedColumn,
)
from typing_extensions import Annotated

from doxa_cli.constants import (
    COMPETITION_KEY,
    DOXA_STORAGE_URL,
    ENVIRONMENT_KEY,
    EXCLUDED_FILES,
    UPLOAD_SLOT_URL,
    theme,
)
from doxa_cli.errors import (
    SessionExpiredError,
    SignedOutError,
    UploadError,
    UploadSlotDeniedError,
    show_error,
)
from doxa_cli.utils import get_request_client, read_doxa_yaml


def upload(
    directory: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="The path to the directory containing your submission.",
            show_default=False,
        ),
    ],
    competition: Annotated[
        Optional[str], typer.Option("--competition", "-c", show_default=False)
    ] = None,
    environment: Annotated[
        Optional[str], typer.Option("--environment", "-e", show_default=False)
    ] = None,
):
    """Upload and submit an agent to the DOXA AI platform."""

    console = Console()

    # Step 0: ensure that the user is logged in!

    try:
        session = get_request_client(require_auth=True)
    except SignedOutError:
        show_error(
            "You must be logged in to upload a submission to the DOXA AI platform."
        )
        raise typer.Exit(1)
    except SessionExpiredError:
        show_error("Your session has expired. Please log in again.")
        raise typer.Exit(1)
    except Exception:
        show_error()
        raise typer.Exit(1)

    # Step 1: read {directory}/doxa.yaml and verify that it is valid, e.g.

    # competition: {competition tag}
    # environment: {environment tag}
    # language: python
    # entrypoint: run.py

    path = str(directory)

    user_config = {}
    try:
        user_config = read_doxa_yaml(path)
    except FileNotFoundError:
        if not competition:
            show_error(
                "\nYour submission folder must contain a `doxa.yaml` file. Please check the DOXA AI website for further guidance."
            )
            raise typer.Exit(1)
    except:
        show_error(
            "\nThere was an error reading the `doxa.yaml` file in your submission. Please check its syntax."
        )
        raise typer.Exit(1)

    # we can override competition and environment with command-line options,
    competition = competition or user_config.get(COMPETITION_KEY)
    environment = environment or user_config.get(ENVIRONMENT_KEY)

    user_config.pop("competition", None)
    user_config.pop("environment", None)

    if not competition:
        show_error(
            "\nYou must specify a competition.\n\nYou can do so by inserting `competition: [COMPETITION TAG]` into the `doxa.yaml` file in your submission folder or by using the --competition/-c command-line option.\n\nRun this command with --help for more information."
        )
        raise typer.Exit(1)

    # Step 2: produce tar.gz of {directory} using `tarfile` module

    ignore_files = user_config.get("ignore", [])
    if not isinstance(ignore_files, list) or not all(
        isinstance(pattern, str) for pattern in ignore_files
    ):
        show_error(
            "\nIf you specify `ignore` in your `doxa.yaml` file, it must be a list of file name matching patterns."
        )
        raise typer.Exit(1)

    try:
        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".tar.gz", delete=False, mode="w+b"
        )
    except Exception as e:
        show_error("An error occurred creating a temporary file.")
        raise typer.Exit(1)

    print()

    try:
        compress_submission_directory(temporary_file, path, ignore_files)
    except:
        os.unlink(temporary_file.name)
        raise typer.Exit(1)

    size = os.path.getsize(temporary_file.name)

    # Step 3: Get an upload slot

    try:
        upload_slot = get_upload_slot(
            session=session,
            competition=competition,
            environment=environment,
            metadata=user_config,
            size=size,
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
            "SUBMISSION_TOO_LARGE",
            "UNKNOWN",
        ):
            first_line, *lines = e.doxa_error_message.split("\n")
            show_error(first_line)
            if lines:
                console.print(*lines, sep="\n\n", style="bold white")
        elif e.doxa_error_code == "UPLOAD_RATE_LIMIT_REACHED":
            show_error("Your upload could not be processed.")
            console.print(e.doxa_error_message, style="bold white")
        elif e.doxa_error_code == "METADATA_INVALID":
            show_error(
                "\nThe metadata provided in your `doxa.yaml` file is invalid, so your upload could not be processed."
            )

            if e.doxa_error_message:
                console.print(
                    f"\nThe platform gave the following reason: {e.doxa_error_message}",
                    style="bold white",
                )
        else:
            show_error(
                "\nAn error occurred while requesting an upload slot, so your upload could not be processed."
            )

        os.unlink(temporary_file.name)
        raise typer.Exit(1)
    except Exception:
        show_error(
            "\nAn error occurred while requesting an upload slot. Please try again later."
        )
        os.unlink(temporary_file.name)
        raise typer.Exit(1)

    # Step 4: upload the tarfile to {endpoint}

    print()
    try:
        with open(temporary_file.name, "rb") as f:
            # show a fancy progress bar of the upload!
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                "    ",
                DownloadColumn(),
                "    ",
                TransferSpeedColumn(),
                console=Console(theme=theme),
            ) as progress:
                task = progress.add_task("Uploading your submission  ", total=size)

                def callback(m):
                    progress.update(task, completed=m.bytes_read)

                upload_agent(upload_endpoint, upload_token, f, callback)
                progress.update(task, completed=size)
    except UploadError as e:
        console.print(f"\n  [bold red]ERROR[white]: {e.doxa_error_message}")
        raise typer.Exit(1)
    except Exception:
        show_error("\nOops, there was an error uploading your submission to DOXA.")
        raise typer.Exit(1)
    finally:
        os.unlink(temporary_file.name)

    # Step 5: print success message!

    console.print(
        "\n  [bold cyan]Your submission has been successfully uploaded to the DOXA AI platform!"
    )


def get_upload_slot(
    session: requests.Session,
    competition: str,
    environment: str | None,
    metadata: dict[Any, Any],
    size: int,
):
    result = session.post(
        UPLOAD_SLOT_URL,
        json={
            "competition_tag": competition,
            "environment_tag": environment,
            "metadata": metadata,
            "size": size,
        },
        verify=True,
    ).json()

    if "error" in result:
        raise UploadSlotDeniedError(
            result["error"].get("code"), result["error"].get("message")
        )

    assert "endpoint" in result
    assert "token" in result

    return result


def compress_submission_directory(
    f: typing.IO, directory: str, ignore_files: list[str]
) -> None:
    excluded_file_patterns = EXCLUDED_FILES | set(ignore_files)

    def filter_tar(tarinfo: tarfile.TarInfo):
        # Exclude certain files (e.g. the `doxa.yaml` file, symbolic links, etc)
        if not (tarinfo.isfile() or tarinfo.isdir()) or any(
            fnmatch.fnmatch(tarinfo.name, pattern) for pattern in excluded_file_patterns
        ):
            return None

        # Reset user & group information
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"

        # Normalise permissions
        tarinfo.mode |= 0o777 if tarinfo.isfile() else 0o775

        return tarinfo

    try:
        with tarfile.open(fileobj=f, mode="w:gz", format=tarfile.PAX_FORMAT) as tar:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                "    ",
                MofNCompleteColumn(),
                "files",
                console=Console(theme=theme),
            ) as progress:
                for file_name in progress.track(
                    os.listdir(directory),
                    description="Compressing your submission",
                ):
                    tar.add(
                        os.path.join(directory, file_name),
                        arcname=file_name,
                        filter=filter_tar,
                    )
    finally:
        f.close()


def upload_agent(
    upload_endpoint: str,
    upload_token: str,
    file: typing.IO,
    callback: typing.Callable,
) -> None:
    m = MultipartEncoderMonitor(MultipartEncoder(fields={file.name: file}), callback)

    response = requests.post(
        upload_endpoint,
        headers={
            "Authorization": f"Bearer {upload_token}",
            "Content-Type": m.content_type,
        },
        data=m,
        verify=True,
    )

    body = response.json()
    if response.ok and "error" not in body:
        return

    # New response format: { "error": { "code": "ERROR_CODE", "message": "..." } }
    if "error" in body:
        raise UploadError(body["error"].get("code"), body["error"].get("message"))

    # Other error
    raise UploadError("UNKNOWN", body.get("message"))
