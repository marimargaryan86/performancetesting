import abc
import datetime
from collections.abc import Sequence

import grpc

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib.format import protobuf


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
        filter_by: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        """Fetch sequence of accounts."""

    @abc.abstractmethod
    async def update_account_status(
        self,
        document_id: str,
        status: str,
    ) -> models_pb2.Account:
        """Update status field of account."""


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
        filter_by: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        statuses = [
            protobuf.slug_to_enum_value(
                models_pb2.Status,
                filter_status,
            )
            for filter_status in filter_by
        ]
        return grpc_pb2.ListAccountsResponse(
            accounts=[
                account
                for account in self._accounts.values()
                if account.status in statuses
            ],
        )

    async def update_account_status(
        self,
        document_id: str,
        status: str,
    ) -> models_pb2.Account:
        account = self._accounts.get(document_id)
        if account is None:
            raise errors.NotFoundError("Account is not found")
        account.status = protobuf.slug_to_enum_value(models_pb2.Status, status)
        account.updated_at.CopyFrom(
            protobuf.datetime_to_protobuf(
                datetime.datetime.now(tz=datetime.UTC),
            ),
        )
        self._accounts[document_id] = account
        return account


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
        filter_by: Sequence[str],
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListAccountsResponse:
        return await self._client.ListAccounts(
            grpc_pb2.ListAccountsRequest(
                page_size=limit or self._default_page_size,
                page_token=cursor or "",
                filter_by=filter_by,
            ),
        )

    async def update_account_status(
        self,
        document_id: str,
        status: str,
    ) -> models_pb2.Account:
        response = await errors.handle_grpc_errors(
            self._client.UpdateAccountStatus(
                grpc_pb2.UpdateAccountStatusRequest(
                    id=document_id,
                    status=protobuf.slug_to_enum_value(
                        models_pb2.Status,
                        status,
                    ),
                ),
            ),
        )
        return response.account
