from enum import Enum


class DefaultErrorCodes(Enum):
    internal_server_error = "internal.server.error"
    not_found = "not.found"


class ContentType(Enum):
    boolean = "boolean"
    string = "string"
    number = "number"
