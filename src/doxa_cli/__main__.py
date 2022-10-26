import click

from doxa_cli.commands.login import login
from doxa_cli.commands.logout import logout
from doxa_cli.commands.upload import upload
from doxa_cli.commands.user import user


@click.group()
@click.pass_context
def main(ctx):
    """The DOXA CLI is the primary tool for uploading agents to DOXA."""

    if ctx.invoked_subcommand is None:
        click.secho("Hi! Welcome to the DOXA CLI!", bold=True, fg="green")


main.add_command(login)
main.add_command(logout)
main.add_command(user)
main.add_command(upload)


if __name__ == "__main__":
    main()
