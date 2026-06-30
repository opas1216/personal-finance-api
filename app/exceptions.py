class NotFoundException(Exception):
    """
    Exception raised when a requested resource is not found.

    Attributes:
        detail (str): A message describing the error.
    """
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ForbiddenException(Exception):
    """
    Exception raised for forbidden access, such as when a user does not have permission to access a resource.

    Attributes:
        detail (str): A message describing the error.
    """
    def __init__(self, detail: str = "Access forbidden"):
        self.detail = detail

class ConflictException(Exception):
    """
    Exception raised for conflicts, such as when a resource already exists.

    Attributes:
        detail (str): A message describing the conflict.
    """
    def __init__(self, detail: str = "Resource already exists"):
        self.detail = detail

class BadRequestException(Exception):
    """
    Exception raised for bad requests, such as when the request data is invalid or missing required fields.

    Attributes:
        detail (str): A message describing the error.
    """
    def __init__(self, detail: str = "Bad request"):
        self.detail = detail