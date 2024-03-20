import click

from doxa_cli.config import CONFIG
from doxa_cli.errors import show_error


def logout():
    """Log out of your DOXA AI platform account."""

    try:
        CONFIG.clear()
    except FileNotFoundError:
        pass
    except:
        show_error("\nAn error occurred while logging you out.")

    click.secho("\nGoodbye!", fg="cyan", bold=True)
