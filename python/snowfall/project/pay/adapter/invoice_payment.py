import abc

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


class DictClient(Client):
    def __init__(self) -> None:
        self._invoice_accounts = {}  # type: ignore[var-annotated]

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
