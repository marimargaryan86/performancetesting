from typing import Any, Mapping, Sequence

from starlette import status, testclient


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

        assert isinstance(body["data"], list)

        if not body["data"]:
            break

        resources = [*resources, *body["data"]]
        url = body["links"]["next"]

    assert set(expected_ids) == {resource["id"] for resource in resources}

    _test_view_endpoint(client, resources)


def _test_view_endpoint(
    client: testclient.TestClient,
    resources: Sequence[Mapping[str, Any]],
) -> None:
    current_link = None

    for resource in resources:
        current_link = resource["links"]["self"]
        response = client.get(current_link)

        assert response.status_code == status.HTTP_200_OK

        body = response.json()

        assert body["data"] == resource

    response = client.get("{0}foobar".format(current_link))

    assert response.status_code == status.HTTP_404_NOT_FOUND
