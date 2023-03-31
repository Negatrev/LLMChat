class GptException(Exception):  # Base exception for gpt
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__()


class GptConnectionException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptLengthException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptContentFilterException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)


class GptTooMuchTokenException(GptException):
    def __init__(self, *, msg: str | None = None) -> None:
        self.msg = msg
        super().__init__(msg=msg)