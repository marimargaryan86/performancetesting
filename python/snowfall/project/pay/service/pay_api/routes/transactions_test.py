from typing import Collection, Sequence

import httpx
from starlette import status

from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import Quotation


class TestTransactions(object):
    async def test_lower_limit_conversion_is_handled(
        self,
        client: httpx.AsyncClient,
        quote_is_less_than_the_limit: Quotation,
    ) -> None:
        request = self._transaction_request(quote_is_less_than_the_limit.id)

        response = await client.post("/transactions", json=request)
        error = response.json()["errors"][0]
        assert (
            error["detail"]
            == "Conversion of GBP equivalent 0.89 is less than your lower limit of 1.00"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert error["status"] == "400" and error["code"] == "bad_request"

    async def test_get_all_transactions_success(
        self,
        admin_client: httpx.AsyncClient,
        transaction_ids: Sequence[str],
    ) -> None:
        response = await admin_client.get("/transactions")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == len(transaction_ids)

    async def test_booked_quote_handled(
        self,
        client: httpx.AsyncClient,
        booked_quote: Quotation,
    ) -> None:
        request = self._transaction_request(booked_quote.id)

        response = await client.post("/transactions", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Quotation not valid"
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert error["status"] == "404" and error["code"] == "not_found"

    def _transaction_request(self, quote_id: str) -> dict[str, Collection[str]]:
        return {
            "data": {
                "type": "transactions",
                "attributes": {
                    "externalReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                    "parentExternalReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quote_id,
                            "type": "quotations",
                        },
                    },
                },
            },
        }
