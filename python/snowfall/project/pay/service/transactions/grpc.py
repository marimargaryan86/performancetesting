import grpc

from snowfall.project.pay.service.transactions.transactions import (
    TransactionsRepository,
)
from snowfall.project.pay.service.transactions.v1alpha import grpc_pb2, grpc_pb2_grpc
from snowfall.stdlib.transport.grpc import service


class TransactionsService(
    service.Service,
    grpc_pb2_grpc.TransactionsServiceServicer,
):
    def __init__(
        self,
        transactions: TransactionsRepository,
    ):
        self._transactions = transactions
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["TransactionsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_TransactionsServiceServicer_to_server(
            self,
            server,
        )

    async def ListTransactions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListTransactionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListTransactionsResponse:
        transactions = await self._transactions.list_transactions(
            cursor=request.page_token,
        )
        transactions.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return grpc_pb2.ListTransactionsResponse(
            transactions=[transaction async for transaction in transactions],
            next_page_token=await transactions.cursor(),
        )
