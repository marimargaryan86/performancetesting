import abc

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.payments.v1 import (
    invoice_models_pb2,
    invoice_pb2,
    invoice_pb2_grpc,
)
from snowfall.stdlib import string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create_account(
        self,
        email: str,
        name: str,
    ) -> invoice_models_pb2.InvoiceAccount:
        """Create an invoice account."""

    @abc.abstractmethod
    async def create_invoice(
        self,
        invoice_account_id: str,
        days_until_due: int,
    ) -> invoice_models_pb2.Invoice:
        """Create an invoice."""


class DictClient(Client):
    def __init__(self) -> None:
        self._invoice_accounts = {}  # type: ignore[var-annotated]
        self._invoices = {}  # type: ignore[var-annotated]

    async def create_account(
        self,
        email: str,
        name: str,
    ) -> invoice_models_pb2.InvoiceAccount:
        invoice_id = string.uuid()
        account = invoice_models_pb2.InvoiceAccount(
            id=invoice_id,
            email=email,
            name=name,
        )
        self._invoice_accounts[invoice_id] = account

        return account

    async def create_invoice(
        self,
        invoice_account_id: str,
        days_until_due: int,
    ) -> invoice_models_pb2.Invoice:
        if invoice_account_id not in self._invoice_accounts:
            raise errors.NotFoundError()

        invoice = invoice_models_pb2.Invoice(
            id=string.uuid(),
        )

        self._invoices[invoice.id] = invoice
        return invoice


class GrpcClient(Client):
    def __init__(
        self,
        invoice_payment_stub: invoice_pb2_grpc.InvoiceServiceStub,
        timeout: int = 10,
    ):
        self._client = invoice_payment_stub
        self._timeout = timeout

    async def create_account(
        self,
        email: str,
        name: str,
    ) -> invoice_models_pb2.InvoiceAccount:
        create_invoice_account_request = invoice_pb2.CreateInvoiceAccountRequest(
            email=email,
            name=name,
        )
        return await self._client.CreateInvoiceAccount(
            create_invoice_account_request,
            timeout=self._timeout,
        )

    async def create_invoice(
        self,
        invoice_account_id: str,
        days_until_due: int,
    ) -> invoice_models_pb2.Invoice:
        response = await errors.handle_grpc_errors(
            self._client.CreateInvoice(
                invoice_pb2.CreateInvoiceRequest(
                    invoice_account_id=invoice_account_id,
                    days_until_due=days_until_due,
                ),
            ),
        )

        return response.invoice
