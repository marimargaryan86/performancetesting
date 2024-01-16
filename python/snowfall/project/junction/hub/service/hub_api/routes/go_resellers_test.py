import httpx
from starlette import status

from snowfall.project.junction.go.fixtures import NOT_FOUND, RESELLERS
from snowfall.stdlib.integration.starlette import testing


async def test_get_resellers(client: httpx.AsyncClient) -> None:
    await testing.test_list_and_view_endpoints(
        client=client,
        url="/resellers",
        expected_ids=RESELLERS,
    )


async def test_create_reseller(client: httpx.AsyncClient) -> None:
    payload = {
        "type": "resellers",
        "attributes": {
            "name": "test_reseller",
            "providers": [
                "f3639035-5e43-4b8d-9737-69684e57009f",
                "f3639035-5e43-4b8d-9737-69684e57008d",
            ],
        },
        "relationships": {
            "company": {
                "data": {
                    "id": "f3639035-5e43-4b8d-9737-69684e57006f",
                    "type": "companies",
                },
            },
            "currency": {
                "data": {
                    "id": "USD",
                    "type": "currencies",
                },
            },
            "parentResellers": {"data": []},
        },
    }

    response = await client.post(
        url="/resellers",
        json={
            "data": payload,
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["id"]


async def test_update_reseller(client: httpx.AsyncClient) -> None:
    response = await client.patch(
        url="/resellers/{resellerId}".format(resellerId=RESELLERS[0]),
        json={
            "data": {
                "type": "resellers",
                "attributes": {
                    "name": "updated_reseller",
                },
            },
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["attributes"]["name"] == "updated_reseller"


async def test_update_reseller_not_found(client: httpx.AsyncClient) -> None:
    response = await client.patch(
        url="/resellers/{resellerId}".format(resellerId=NOT_FOUND),
        json={
            "data": {
                "type": "resellers",
                "attributes": {
                    "name": "updated_reseller",
                },
            },
        },
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
