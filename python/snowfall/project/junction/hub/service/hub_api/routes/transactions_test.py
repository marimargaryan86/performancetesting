from collections.abc import Sequence

import httpx
from starlette import status


class TestTransactions:
    async def test_get_all_transactions_success(
        self,
        client: httpx.AsyncClient,
        transaction_ids: Sequence[str],
    ) -> None:
        response = await client.get("/transactions")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == len(transaction_ids)

    async def test_get_all_transactions_success_with_filter(
        self,
        client: httpx.AsyncClient,
        transaction_ids: Sequence[str],
    ) -> None:
        filter_params = [
            "filter[ids][eq]={0}".format(transaction_id)
            for transaction_id in transaction_ids
        ]
        req_url = "/transactions?{0}".format("&".join(filter_params))

        response = await client.get(req_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == len(transaction_ids)

    async def test_get_transactions_with_sort(
        self,
        client: httpx.AsyncClient,
        transaction_ids: Sequence[str],
    ) -> None:
        response_ascending = await client.get("/transactions?sort=createdAt")
        response_descending = await client.get("/transactions?sort=-createdAt")
        assert len(response_ascending.json()["data"]) == len(
            response_descending.json()["data"],
        )
