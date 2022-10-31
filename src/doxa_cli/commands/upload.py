import click
import requests
from doxa_cli.constants import COMPETITION_KEY, ENVIRONMENT_KEY, UPLAOD_URL, SUCCESS_KEY, ERROR_KEY
from doxa_cli.utils import get_access_token, read_doxa_upload, compress_agent_dir

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

    try:
        upload_json = read_doxa_upload(directory)
    except FileNotFoundError:
        click.secho(
            "\nYou must have doxa.yaml file before upload.", fg="cyan", bold=True
        )
        return

    # we can override competition and environment with command-line options,
    # which we should validate if used

    # if the user does not specify an environment, maybe could let it be the
    # default environment (?)
    
    competition = check_variable(competition, COMPETITION_KEY, upload_json)
    environment = check_variable(environment, ENVIRONMENT_KEY, upload_json)
    upload_json.pop("competition", None)
    upload_json.pop("environment", None)

    if environment is None or competition is None:
        click.secho(
            "\nYou must specify a environment value either in doxa.yaml or command line flag.", fg="cyan", bold=True
        )
        return

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

    try:
        upload_response = get_upload_slot(competition, environment, upload_json)
    except:
        click.secho("\nAn error occurred while getting a upload slot. Please try again later.", fg="red", bold=True)
        return
    
    success = upload_response[SUCCESS_KEY]
    if not success:
        try:
            assert "error" in upload_json
        except:
            click.secho("\nIt seems like something is wrong with the api protocol. 'error' is not in the response.", fg="red", bold=True)
            return

        click.secho(f"\n{upload_json[ERROR_KEY]}", fg="red", bold=True)
        click.secho("Please change the variable and try again!", fg="red", bold=True)
        return
    else:
        try:
            assert "endpoint" in upload_json
            assert "token" in upload_json
        except:
            click.secho("\nIt seems like something is wrong with the api protocol. 'endpoint' or 'token' is not in the response.", fg="red", bold=True)
        
        end_point = upload_response["endpoint"]
        token = upload_response["token"]

    # Step 3: produce tar.gz of {directory} using `tarfile` module
    compress_agent_dir(directory)

    # Step 4:`upload the tarfile to {endpoint} making sure to pass in the header
    # - Authorization: Bearer {token from step 2}
    upload_result = upload_agent()
    print(upload_result)

    # show a fancy progress bar of the upload!

    # Step 5: print success message! (or error message)

def check_variable(v, v_key, json):
    if v is not None:
        pass
    elif v_key in json:
        v = json[v_key]
    return v

def get_upload_slot(competition, environment, metadata):
    session_stop, access_token = get_access_token()
    if session_stop:
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    result = requests.post(
        UPLAOD_URL, headers=headers,json={"competition_tag": competition, "environment_tag": environment, "metadata": metadata}, verify=True
    ).json()

    assert SUCCESS_KEY in result

    return result

def upload_agent():
    session_stop, access_token = get_access_token()
    if session_stop:
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    result = requests.post(
        UPLAOD_URL, headers=headers,files={"file": open("tarfile.tar.gz", "rb")}, verify=True
    ).json()

    #assert SUCCESS_KEY in result

    return result

