from enum import Enum


class ErrorType(Enum):
    ALREADY_IN_OPERATION = 1
    ENDPOINT_UNREACHABLE = 2
    INTERNAL_ERROR = 3
    INVALID_DIRECTIVE = 4
    NO_SUCH_ENDPOINT = 5
