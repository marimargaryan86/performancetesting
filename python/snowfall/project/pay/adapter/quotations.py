from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1 import (
    models_pb2 as companies_models,
)
from snowfall.project.pay.service.transactions.v1 import grpc_pb2, grpc_pb2_grpc
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models,
)
from snowfall.stdlib import money, string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
        tax: int,
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

    async def create(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
        tax: int,
    ) -> transactions_models.Quotation:
        mock_from_amount = money.Money(amount, money.Currency(from_currency))
        mock_to_amount = money.Money(amount, money.Currency(to_currency))
        quotation = transactions_models.Quotation(
            id=string.uuid(),
            status=transactions_models.QuotationStatus.QUOTATION_STATUS_QUOTED,
            amounts=transactions_models.QuotationAmounts(
                beneficiary=mock_from_amount.protobuf(),
                base_converted=mock_to_amount.protobuf(),
                sales_margin=mock_to_amount.protobuf(),
                quotation=mock_to_amount.protobuf(),
                fx_margin=mock_to_amount.protobuf(),
                processing_margin=mock_to_amount.protobuf(),
                total_amount=mock_to_amount.protobuf(),
                total_markups=mock_to_amount.protobuf(),
                tax=money.Money(tax, money.Currency(from_currency)).protobuf(),
            ),
            rates=transactions_models.QuotationRates(
                fx_quote=1.0,
                fx_buffer=1.0,
                fx_markup=1.0,
                sales_markup=1.0,
                processing_markup=1.0,
            ),
            payer_id=payer.id,
            beneficiary_id=beneficiary_company.id,
        )
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

    async def create(
        self,
        from_currency: str,
        to_currency: str,
        amount: int,
        payer: companies_models.Company,
        beneficiary_company: companies_models.Company,
        session_token: str,
        tax: int,
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
                    tax=tax,
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
