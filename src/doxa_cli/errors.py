class DoxaError(Exception):
    pass


class LoggedOutError(DoxaError):
    pass


class SessionExpiredError(DoxaError):
    pass


class BrokenConfigurationError(DoxaError):
    pass


class UploadSlotDeniedError(DoxaError):
    def __init__(self, code, message, *args: object) -> None:
        super().__init__(*args)
        self.doxa_error_code = code
        self.doxa_error_message = message


class UploadError(DoxaError):
    pass
