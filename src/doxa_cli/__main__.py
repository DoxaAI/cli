import datetime
import os
import time
import webbrowser

import click
import requests
import json
from termcolor import colored

login_url = 'https://doxaai.com/api/oauth/device/code'
token_url = 'https://doxaai.com/api/oauth/token'
client_id = 'eb594ca3-023d-477f-823a-22e48f4e5235'
scope = 'basic'
token_path = "~/.doxa"


@click.command()
def login():
    """Log in with your DOXA account."""

    now = datetime.datetime.now()
    r = requests.post(login_url, data={"client_id": client_id, "scope": scope}, verify=True)
    get_device_time = now + r.elapsed
    expire = 0

    data = json.loads(r.text)
    device_code = data['device_code']
    interval = data['interval']
    expire = datetime.timedelta(0,data['expires_in'])
    click.secho("Use the link below to login and authorize your device in Doxa website:")
    click.secho(data['verification_uri_complete'])
    webbrowser.open(data['verification_uri_complete'], 2, False)

    grant = "device_code"
    access_time = 0.0

    while True:
        if datetime.datetime.now()<get_device_time+expire:
            try:
                now = datetime.datetime.now()
                r = requests.post(token_url,
                                  data={"grant_type": grant, "client_id": client_id, "device_code": device_code}, verify=True)

                if "error" in r.text:
                    click.secho("[INFO] Authorization Pending...")

                else:
                    access_time = now + r.elapsed
                    click.secho(colored("[INFO] Authorization Succesful!", 'yellow'))

                    token = json.loads(r.text)

                    access_token = token['access_token']
                    refresh_token = token['refresh_token']
                    token_type = token['token_type']
                    expires_in = datetime.timedelta(0,token['expires_in'])

                    if not os.path.exists(token_path):
                        os.makedirs(token_path)
                    with open(os.path.join(token_path,"config.json"), "w") as f:
                        json.dump({'access_token': access_token, 'refresh_token': refresh_token, 'expire':access_time+ expires_in}, f, default = str)
                    break
            except ValueError:
                click.secho("[ERROR] Something Went Wrong!")

            time.sleep(interval)
        else:
            click.secho("Device code expired. Please try login command again.")
            break

def getNewestToken():
    grant = "refresh_token"

    if not os.path.exists(token_path):
        os.makedirs(token_path)

    with open(os.path.join(token_path,"config.json"), 'r') as f:
        data = json.load(f)

    if datetime.datetime.now()<datetime.datetime.strptime(data['expire'], '%Y-%m-%d %H:%M:%S.%f'):
        return data['access_token']
    else:
        now = datetime.datetime.now()
        r = requests.post(token_url, data={"grant_type": grant, "refresh_token": data["refresh_token"]}, verify=True)
        access_time = r.elapsed
        token = json.loads(r.text)
        access_token = token['access_token']
        refresh_token = token['refresh_token']
        token_type = token['token_type']
        expires_in = datetime.timedelta(0,token['expires_in'])

        with open(os.path.join(token_path,"config.json"), "w") as f:
            json.dump(
                {'access_token': access_token, 'refresh_token': refresh_token, 'expire': access_time + expires_in}, f, default = str)
        return token['access_token']

@click.command()
def logout():
    """Log out of your DOXA account."""
    click.secho("Start to clear config file!")
    os.remove(os.path.join(token_path,"config.json"))
    os.rmdir(token_path)
    #open(os.path.join(token_path,"config.json"), 'w').close()
    click.secho("GoodBye!")

@click.command()
def user():
    """Display information on the currently logged in user."""
    user_url = "https://doxaai.com/api/oauth/user"
    headers = {"Authorization": 'Bearer %s' % getNewestToken()}

    r = requests.post(user_url, headers=headers, verify=True)
    data = json.loads(r.text)["user"]

    click.secho("Hello, you are currently logged in as %s with email %s!"%(data["username"],data["email"]))
    if data["admin"]:
        click.secho("[You are an admin.]",fg="blue")
    diff = datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.strptime(data["created_at"], '%Y-%m-%dT%H:%M:%S.%f%z')
    click.secho("You created your account %s days ago."%str(diff.days))

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


@click.command()
def main():
    """The DOXA CLI is the primary tool for uploading agents to DOXA."""

    click.secho("Hi! Welcome to the Doxa Cli service!", bold=True, fg="green")



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
