import httpx
from starlette import status

from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import Quotation


class TestTransactions(object):
    async def test_lower_limit_conversion_is_handled(
        self,
        client: httpx.AsyncClient,
        quote_is_less_than_the_limit: Quotation,
    ) -> None:
        request = {
            "data": {
                "type": "transactions",
                "attributes": {
                    "externalReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                    "parentExternalReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quote_is_less_than_the_limit.id,
                            "type": "quotations",
                        },
                    },
                },
            },
        }

        response = await client.post("/transactions", json=request)
        error = response.json()["errors"][0]
        assert (
            error["detail"]
            == "Conversion of GBP equivalent 0.89 is less than your lower limit of 1.00"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert error["status"] == "400" and error["code"] == "bad_request"
