import grpc

from snowfall.project.pay.service.accounts.accounts import AccountsRepository
from snowfall.project.pay.service.accounts.v1alpha import (
    accounts_pb2,
    accounts_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class AccountsService(service.Service, accounts_pb2_grpc.AccountsServiceServicer):
    def __init__(self, accounts_repository: AccountsRepository):
        self._accounts = accounts_repository
        self._default_page_size = 20

    def get_name(self) -> str:
        return accounts_pb2.DESCRIPTOR.services_by_name["AccountsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        accounts_pb2_grpc.add_AccountsServiceServicer_to_server(self, server)

    async def CreateAccount(  # type: ignore[override] # noqa: N802
        self,
        request: accounts_pb2.CreateAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> accounts_pb2.CreateAccountResponse:
        inserted_account = await self._accounts.insert(request.account)

        return accounts_pb2.CreateAccountResponse(account=inserted_account)

    async def GetAccount(  # type: ignore[override] # noqa: N802
        self,
        request: accounts_pb2.GetAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> accounts_pb2.GetAccountResponse:
        account = await self._accounts.find_by_id(request.id)

        if account is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return accounts_pb2.GetAccountResponse(account=account)

    async def ListAccounts(  # type: ignore[override] # noqa: N802
        self,
        request: accounts_pb2.ListAccountsRequest,
        context: grpc.aio.ServicerContext,
    ) -> accounts_pb2.ListAccountsResponse:
        db_accounts = await self._accounts.find(
            cursor=request.page_token,
        )
        db_accounts.limit(request.page_size or self._default_page_size)

        return accounts_pb2.ListAccountsResponse(
            accounts=[account async for account in db_accounts],
            next_page_token=await db_accounts.cursor(),
        )
