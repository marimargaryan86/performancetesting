import abc
from typing import Sequence

from snowfall.project.pay.service.accounts.v1alpha import (
    accounts_pb2,
    accounts_pb2_grpc,
    models_pb2,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        account: models_pb2.Account,
    ) -> models_pb2.Account:
        """Create account."""

    @abc.abstractmethod
    async def get(
        self,
        account_id: str,
    ) -> models_pb2.Account:
        """Fetch account."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Sequence[models_pb2.Account]:
        """Fetch sequence of accounts."""


class GrpcClient(Client):
    def __init__(
        self,
        account_stub: accounts_pb2_grpc.AccountsServiceStub,
        timeout: int = 5,
    ):
        self._client = account_stub
        self._timeout = timeout

    async def create(
        self,
        account: models_pb2.Account,
    ) -> models_pb2.Account:
        return await self._client.CreateAccount(
            accounts_pb2.CreateAccountRequest(
                account=account,
            ),
        ).account

    async def get(self, account_id: str) -> models_pb2.Account:
        response = await self._client.GetAccount(
            accounts_pb2.GetAccountRequest(id=account_id),
        )

        return response.account

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Sequence[models_pb2.Account]:
        if limit is None:
            limit = 20

        response = await self._client.ListAccounts(
            accounts_pb2.ListAccountsRequest(
                page_size=limit,
                page_token=cursor or "",
            ),
        )

        return response.accounts
