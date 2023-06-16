from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1alpha import (
    models_pb2 as companies_models,
)
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.project.pay.service.transactions.v1alpha import grpc_pb2, grpc_pb2_grpc
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transactions_models,
)
from snowfall.stdlib import money


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(  # noqa: WPS211
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
    ) -> transactions_models.Quotation:
        """Create a quotation resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> transactions_models.Quotation:
        """Fetch a quotation resource."""

    @abc.abstractmethod
    async def update_status(
        self,
        identifier: str,
        status: transactions_models.QuotationStatus.ValueType,
    ) -> bool:
        """Update quotation status."""


class DictClient(Client):
    def __init__(self, quotations: Sequence[transactions_models.Quotation]):
        self._quotations: dict[str, transactions_models.Quotation] = {
            quotation.id: quotation for quotation in quotations
        }

    async def create(  # noqa: WPS211
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
    ) -> transactions_models.Quotation:
        quote = Quote(
            amount,
            money.Currency(from_currency),
            money.Currency(to_currency),
            1.0,
            payer,
            beneficiary_company.id,
        )
        quotation = quote.to_proto()
        self._quotations[quotation.id] = quotation

        return quotation

    async def get(self, identifier: str) -> transactions_models.Quotation:
        try:
            return self._quotations[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update_status(
        self,
        identifier: str,
        status: transactions_models.QuotationStatus.ValueType,
    ) -> bool:
        self._quotations[identifier].status = status
        return True


class GrpcClient(Client):
    def __init__(
        self,
        quotations: grpc_pb2_grpc.QuotationsServiceStub,
        timeout: int = 10,
    ):
        self._quotations = quotations
        self._timeout = timeout

    async def create(  # noqa: WPS211
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
    ) -> transactions_models.Quotation:
        response = await errors.handle_grpc_errors(
            self._quotations.CreateQuotation(
                grpc_pb2.CreateQuotationRequest(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=amount,
                    payer=payer,
                    beneficiary_company=beneficiary_company,
                    session_token=session_token,
                ),
            ),
        )

        return response.quotation

    async def get(self, identifier: str) -> transactions_models.Quotation:
        response = await errors.handle_grpc_errors(
            self._quotations.GetQuotation(
                grpc_pb2.GetTransactionRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

        return response.quotation

    async def update_status(
        self,
        identifier: str,
        status: transactions_models.QuotationStatus.ValueType,
    ) -> bool:
        update_status = await errors.handle_grpc_errors(
            self._quotations.UpdateQuotationStatus(
                grpc_pb2.UpdateQuotationStatusRequest(
                    id=identifier,
                    status=status,
                ),
                timeout=self._timeout,
            ),
        )
        return update_status.is_success
