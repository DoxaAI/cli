import click
from doxa_cli.constants import CONFIG_PATH, DOXA_BASE_URL
from doxa_cli.utils import clear_doxa_config, print_line, read_doxa_config, show_error


@click.command(hidden=True)
@click.option("--reset", "-r", default=False, is_flag=True)
@click.option("--debug", "-d", default=False, is_flag=True)
def config(reset, debug):

    print_line("\nDOXA base URL", DOXA_BASE_URL)
    print_line("\nConfiguration path", CONFIG_PATH)

    if debug:
        try:
            config = read_doxa_config()

            print_line("\nAccess token", config.get("access_token"))
            print_line("\nAccess token (expiry)", config.get("expires_at"))
            print_line("\nRefresh token", config.get("refresh_token"))
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
