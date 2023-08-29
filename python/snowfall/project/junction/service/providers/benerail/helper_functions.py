from pydantic import v1 as pydantic


class UrlHasNoIdError(ValueError):
    """Raised when the URL is expected to have an ID in the path, but it hasn't."""


def last_id_of_url(url: pydantic.AnyUrl) -> str:
    if not url.path:
        raise UrlHasNoIdError

    return url.path.rsplit("/", 1)[-1]
