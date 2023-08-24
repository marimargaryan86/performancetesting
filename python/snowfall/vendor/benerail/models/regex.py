from pydantic.v1 import ConstrainedStr


class UrlRegex(ConstrainedStr):
    regex = (
        r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,"
        r"6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*) "
    )


class NumberRegex(ConstrainedStr):
    regex = "^[0-9]*$"


class URNRegex(ConstrainedStr):
    regex = "^urn:.*$"
