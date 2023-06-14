import abc

import grpc

from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
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
    ) -> models_pb2.Account | None:
        """Fetch account."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        """Fetch sequence of accounts."""


class DictClient(Client):
    def __init__(
        self,
    ) -> None:
        self._accounts: dict[str, models_pb2.Account] = {}

    async def create(
        self,
        account: models_pb2.Account,
    ) -> models_pb2.Account:
        self._accounts[account.id] = account
        return account

    async def get(self, account_id: str) -> models_pb2.Account | None:
        return self._accounts.get(account_id)

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        return grpc_pb2.ListAccountsResponse(
            accounts=list(self._accounts.values()),
        )


class GrpcClient(Client):
    def __init__(
        self,
        account_stub: grpc_pb2_grpc.AccountsServiceStub,
        timeout: int = 5,
    ):
        self._client = account_stub
        self._timeout = timeout
        self._default_page_size = 20

    async def create(
        self,
        account: models_pb2.Account,
    ) -> models_pb2.Account:
        return (
            await self._client.CreateAccount(
                grpc_pb2.CreateAccountRequest(
                    account=account,
                ),
            )
        ).account

    async def get(self, account_id: str) -> models_pb2.Account | None:
        try:
            response = await self._client.GetAccount(
                grpc_pb2.GetAccountRequest(id=account_id),
            )
        except grpc.aio.AioRpcError:
            return None
        return response.account

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        return await self._client.ListAccounts(
            grpc_pb2.ListAccountsRequest(
                page_size=limit or self._default_page_size,
                page_token=cursor or "",
            ),
        )
