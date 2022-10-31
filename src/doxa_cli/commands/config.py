import click
from doxa_cli.constants import CONFIG_PATH, DOXA_BASE_URL
from doxa_cli.utils import clear_doxa_config


@click.command(hidden=True)
@click.option("--reset", default=False, is_flag=True)
def config(reset):
    click.echo(f"\n{click.style('DOXA PATH:', fg='cyan', bold=True)} {DOXA_BASE_URL}")
    click.echo(f"\n{click.style('CONFIG PATH:', fg='cyan', bold=True)} {CONFIG_PATH}")

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
            click.secho(
                "\nThe DOXA CLI was unable to reset its configuration. Please delete the file manually.",
                fg="red",
                bold=True,
            )
