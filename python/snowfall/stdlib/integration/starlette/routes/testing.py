from typing import Any, Mapping, Sequence, cast

from starlette import status, testclient

from snowfall import fixtures

_DATA_KEY = "data"


def test_list_and_view_endpoints(
    client: testclient.TestClient,
    url: str,
    expected_ids: Sequence[str],
) -> None:
    url = "{0}?page[limit]=1".format(url)
    resources: list[dict[str, Any]] = []

    while True:
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

        body = response.json()

        assert isinstance(body[_DATA_KEY], list)

        if not body[_DATA_KEY]:
            break

        resources = [*resources, *body[_DATA_KEY]]
        url = body["links"]["next"]

    assert set(expected_ids) == {resource["id"] for resource in resources}

    _test_view_endpoint(client, resources)


def _test_view_endpoint(
    client: testclient.TestClient,
    resources: Sequence[Mapping[str, Any]],
) -> None:
    current_link = None

    for resource in resources:
        current_link = cast(str, resource["links"]["self"])
        response = client.get(current_link)

        assert response.status_code == status.HTTP_200_OK

        body = response.json()

        assert body[_DATA_KEY] == resource

    if not current_link:
        return

    response = client.get(
        "{0}/{1}".format(current_link.rsplit("/", maxsplit=1), fixtures.NOT_FOUND),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
