import webbrowser
from time import sleep

import click
from halo import Halo


@click.command(hidden=True)
def surprise():
    print()

    with Halo(
        "Enjoy this surprise ;)",
        spinner={"interval": 300, "frames": ["🙈 ", "🙈 ", "🙉 ", "🙊 "]},
    ) as spinner:
        try:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 2, False)
            sleep(212)
            spinner.succeed("Hope you had fun ;)")
        except KeyboardInterrupt:
            spinner.fail(
                "Booo! How dare you not listen to the whole song - it's an absolute bop!"
            )
        except:
            spinner.fail("Booo! Your device is not supported.")
