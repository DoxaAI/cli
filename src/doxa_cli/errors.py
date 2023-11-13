class DoxaError(Exception):
    pass


class LoggedOutError(DoxaError):
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
