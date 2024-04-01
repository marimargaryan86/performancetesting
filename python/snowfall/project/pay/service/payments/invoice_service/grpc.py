import grpc

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import (
    invoice_pb2,
    invoice_pb2_grpc,
)
from snowfall.stdlib import money
from snowfall.stdlib.transport.grpc import service


class InvoiceService(
    service.Service,
    invoice_pb2_grpc.InvoiceServiceServicer,
):
    def __init__(
        self,
        provider: interfaces.InvoiceProvider,
    ):
        self._provider = provider

    def get_name(self) -> str:
        return invoice_pb2.DESCRIPTOR.services_by_name["InvoiceService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        invoice_pb2_grpc.add_InvoiceServiceServicer_to_server(
            self,
            server,
        )

    async def CreateInvoiceAccount(  # type: ignore[override] # noqa: N802
        self,
        request: invoice_pb2.CreateInvoiceAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> invoice_pb2.CreateInvoiceAccountResponse:
        account = self._provider.create_account(
            email=request.email,
            name=request.name,
        )

        return invoice_pb2.CreateInvoiceAccountResponse(account=account)

    async def CreateInvoice(  # type: ignore[override] # noqa: N802
        self,
        request: invoice_pb2.CreateInvoiceRequest,
        context: grpc.aio.ServicerContext,
    ) -> invoice_pb2.CreateInvoiceResponse:
        invoice = self._provider.create_invoice(
            invoice_account_id=request.invoice_account_id,
            days_until_due=request.days_until_due,
            currency=request.currency,
        )

        if invoice is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return invoice_pb2.CreateInvoiceResponse(invoice=invoice)

    async def CreateInvoiceItem(  # type: ignore[override] # noqa: N802
        self,
        request: invoice_pb2.CreateInvoiceItemRequest,
        context: grpc.aio.ServicerContext,
    ) -> invoice_pb2.CreateInvoiceItemResponse:
        invoice_item = self._provider.create_invoice_item(
            request.invoice_account_id,
            request.invoice_id,
            money.from_protobuf(request.amount),
            request.description,
        )

        if invoice_item is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return invoice_pb2.CreateInvoiceItemResponse(
            invoice_item=invoice_item,
        )

    async def FinalizeInvoice(  # type: ignore[override] # noqa: N802
        self,
        request: invoice_pb2.FinalizeInvoiceRequest,
        context: grpc.aio.ServicerContext,
    ) -> invoice_pb2.FinalizeInvoiceResponse:
        if not self._provider.finalize_invoice(request.invoice_id):
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return invoice_pb2.FinalizeInvoiceResponse()
