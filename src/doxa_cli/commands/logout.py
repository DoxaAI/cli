import click
from doxa_cli.utils import clear_doxa_config, show_error


@click.command()
def logout():
    """Log out of your DOXA account."""

    try:
        clear_doxa_config()
    except FileNotFoundError:
        pass
    except:
        show_error("\nAn error occurred while logging you out.")

    click.secho("\nGoodbye!", fg="cyan", bold=True)
