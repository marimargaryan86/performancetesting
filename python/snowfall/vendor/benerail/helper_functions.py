from pydantic.v1 import AnyUrl


class UrlHasNoIdError(ValueError):
    """Raised when the URL is expected to have an ID in the path, but it hasn't."""


def last_id_of_url(url: AnyUrl) -> str:
    if not url.path:
        raise UrlHasNoIdError

    return url.path.rsplit("/", 1)[-1]
