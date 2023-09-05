import dataclasses

from starlette import datastructures, requests

PAGE_CURSOR_KEY = "page[cursor]"
PAGE_LIMIT_KEY = "page[limit]"


@dataclasses.dataclass(frozen=True)
class Pagination(object):
    cursor: str | None = None
    limit: int | None = None


def get_pagination(request: requests.Request) -> Pagination:
    limit: int | None = None
    limit_str = request.scope.get(
        "parsed_query_string",
        request.query_params,
    ).get(PAGE_LIMIT_KEY)

    if limit_str is not None:
        limit = int(limit_str)

    return Pagination(
        limit=limit,
        cursor=request.scope.get(
            "parsed_query_string",
            request.query_params,
        ).get(PAGE_CURSOR_KEY),
    )


def get_next_url(
    url: datastructures.URL,
    next_page_token: str,
    pagination: Pagination,
) -> dict[str, str]:
    next_url = url.include_query_params(
        **{
            PAGE_CURSOR_KEY: next_page_token,
            PAGE_LIMIT_KEY: pagination.limit,
        },
    )

    return {"next": str(next_url)}
