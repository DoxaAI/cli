import typer

from doxa_cli.commands.config import config_info
from doxa_cli.commands.login import login
from doxa_cli.commands.logout import logout
from doxa_cli.commands.surprise import surprise
from doxa_cli.commands.upload import upload
from doxa_cli.commands.user import user
from doxa_cli.commands.version import version

main = typer.Typer(
    name="DOXA AI CLI",
    no_args_is_help=True,
    help="This CLI application allows you to interact with the DOXA AI platform: a powerful platform for hosting engaging competitions in artificial intelligence and machine learning.",
)

main.command()(login)
main.command()(logout)
main.command()(user)
main.command()(version)

main.command(name="config", hidden=True)(config_info)
main.command(hidden=True)(surprise)

main.command(no_args_is_help=True)(upload)
