from collections.abc import Mapping, Sequence
from typing import Any, cast
from urllib.parse import ParseResult, urlparse

import httpx
from starlette import status

from snowfall.stdlib.integration.starlette import request_helpers

_DATA_KEY = "data"
_NOT_FOUND = "00000000-0000-0000-0000-000000000000"


async def test_list_and_view_endpoints(
    client: httpx.AsyncClient,
    url: str,
    expected_ids: Sequence[str],
    invalid_id: str = _NOT_FOUND,
) -> None:
    url_parsed = urlparse(url)
    url = ParseResult(
        url_parsed.scheme,
        url_parsed.netloc,
        url_parsed.path,
        url_parsed.params,
        "{0}&page[limit]=1".format(url_parsed.query),
        url_parsed.fragment,
    ).geturl()
    resources: list[dict[str, Any]] = []

    while True:
        response = await client.get(url)

        assert response.status_code == status.HTTP_200_OK

        body = response.json()

        assert isinstance(body[_DATA_KEY], list)

        if not body[_DATA_KEY]:
            break

        assert len(body[_DATA_KEY]) == 1

        resources.extend(body[_DATA_KEY])
        url = body["links"]["next"]

    assert set(expected_ids) == {resource["id"] for resource in resources}

    await _test_view_endpoint(client, resources, invalid_id)


async def _test_view_endpoint(
    client: httpx.AsyncClient,
    resources: Sequence[Mapping[str, Any]],
    invalid_id: str = _NOT_FOUND,
) -> None:
    current_link = None
    for resource in resources:
        current_link = cast(str, resource["links"]["self"])
        await test_resource_is_fetchable(client, resource)

    if not current_link:
        return
    response = await client.get(
        "{0}/{1}".format(current_link.rsplit("/", maxsplit=1)[0], invalid_id),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_resource_is_fetchable(
    client: httpx.AsyncClient,
    resource: Mapping[str, Any],
) -> None:
    response = await client.get(cast(str, resource["links"]["self"]))

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body[_DATA_KEY] == resource


def resource_is_subset(
    resource_a: Mapping[str, Any],
    resource_b: Mapping[str, Any],
) -> bool:
    flatten_a = request_helpers.flatten_request_body({"data": resource_a})
    flatten_b = request_helpers.flatten_request_body({"data": resource_b})

    return flatten_a.items() <= flatten_b.items()
