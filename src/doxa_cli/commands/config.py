import os

import click

from doxa_cli.constants import CONFIG_PATH, DOXA_BASE_URL, DOXA_STORAGE_URL
from doxa_cli.utils import clear_doxa_config, print_line, read_doxa_config, show_error


@click.command(hidden=True)
@click.option("--reset", "-r", default=False, is_flag=True)
@click.option("--debug", "-d", default=False, is_flag=True)
def config(reset, debug):
    print_line("\nDOXA API Base URL", DOXA_BASE_URL)

    if DOXA_STORAGE_URL:
        print_line("\nDOXA Storage Override URL", DOXA_STORAGE_URL)

    print_line("\nConfiguration Path", CONFIG_PATH)

    if debug:
        try:
            config = read_doxa_config()

            print_line("\nAccess Token", config.get("access_token", "None"))
            print_line("\nAccess Token Expiry", config.get("expires_at", "None"))
            print_line("\nRefresh Token", config.get("refresh_token", "None"))
        except FileNotFoundError:
            show_error("Oops, your configuration file could not be read.")
        except:
            show_error("\nSorry, no debug information is available!")

    if reset:
        try:
            clear_doxa_config()
            click.secho(
                "\nThe configuration file was deleted successfully.",
                fg="green",
                bold=True,
            )
        except FileNotFoundError:
            click.secho(
                "\nThere is no configuration file at that location to delete.",
                fg="yellow",
                bold=True,
            )
        except:
            show_error(
                "\nThe DOXA CLI was unable to reset its configuration. Please delete the file manually."
            )
