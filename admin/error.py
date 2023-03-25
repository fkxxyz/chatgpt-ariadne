import http


class AdminError(Exception):
    HttpStatus: int = 0

    def __init__(self, *args, **kwargs):
        pass


class FriendNotFoundError(AdminError):
    HttpStatus = http.HTTPStatus.NOT_FOUND

    def __init__(self, *args, **kwargs):
        pass


class TerminatedError(AdminError):
    HttpStatus = http.HTTPStatus.RESET_CONTENT

    def __init__(self, *args, **kwargs):
        pass
