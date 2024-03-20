import rich

from doxa_cli.constants import IS_DEBUG, IS_DEV


class DoxaError(Exception):
    pass


class SignedOutError(DoxaError):
    pass


class SessionExpiredError(DoxaError):
    pass


class UploadSlotDeniedError(DoxaError):
    def __init__(self, code, message, *args: object) -> None:
        super().__init__(*args)
        self.doxa_error_code: str = code
        self.doxa_error_message: str = message


class UploadError(DoxaError):
    def __init__(self, code, message, *args: object) -> None:
        super().__init__(*args)
        self.doxa_error_code: str = code
        self.doxa_error_message: str = message


def show_error(
    message: str = "An error occurred while performing this command.",
    color: str = "red",
) -> None:
    console = rich.console.Console()
    console.print(f"\n{message}\n", style=f"bold {color}")

    if IS_DEV or IS_DEBUG:
        console.print_exception()
