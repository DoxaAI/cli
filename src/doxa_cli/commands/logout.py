import click
from doxa_cli.utils import clear_doxa_config


@click.command()
def logout():
    """Log out of your DOXA account."""

    try:
        clear_doxa_config()
    except FileNotFoundError:
        pass
    except:
        click.secho("\nAn error occurred while logging you out.", fg="red", bold=True)

    click.secho("\nGoodbye!", fg="cyan", bold=True)
