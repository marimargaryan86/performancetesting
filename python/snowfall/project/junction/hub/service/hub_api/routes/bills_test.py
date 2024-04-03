import httpx
from starlette import status

from snowfall.project.pay.fixtures import BILLS
from snowfall.stdlib.integration.starlette import testing


class TestBills:
    async def test_get_all_bills(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/bills",
            expected_ids=BILLS,
        )

    async def test_update_bill_reconciliation(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.patch(
            "/bills/{id}".format(id=BILLS[0]),
            json={
                "data": {
                    "type": "bills",
                    "attributes": {
                        "isReconciled": True,
                    },
                },
            },
            headers={"Content-Type": "application/vnd.api+json"},
        )

        assert response.status_code == status.HTTP_200_OK
