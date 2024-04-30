import grpc

from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as searches_models_pb2,
)
from snowfall.project.pay.service.companies.v1 import grpc_pb2 as companies_grpc_pb2
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_pb2_grpc,
)
from snowfall.project.pay.service.companies.v1 import models_pb2 as companies_models_pb2
from snowfall.project.pay.service.transactions.v1 import grpc_pb2 as pay_grpc_pb2
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as pay_pb2_grpc,
)
from snowfall.stdlib.logging import stdout


class PayCreateQuoteError(Exception):
    """Raised when an error occurs creating a quote in PAY."""


class PayQuotes:
    def __init__(
        self,
        pay_transactions_service: pay_pb2_grpc.QuotationsServiceStub,
        pay_companies_service: companies_pb2_grpc.CompaniesServiceStub,
    ):
        self._pay_transactions_service = pay_transactions_service
        self._pay_companies_service = pay_companies_service
        self._logger = stdout.get_logger()

    async def create_pay_quote(
        self,
        amount: int,
        provider_currency: str,
        reseller_currency: str,
        reseller_company_id: str,
        provider_pay_company_id: str,
        vertical_type: searches_models_pb2.VerticalType.ValueType,
    ) -> pay_grpc_pb2.CreateQuotationResponse:
        payer = await self._get_company(reseller_company_id)
        beneficiary = await self._get_company(provider_pay_company_id)

        if vertical_type == searches_models_pb2.VERTICAL_TYPE_AIR:
            pay_vertical_type = companies_models_pb2.VERTICAL_TYPE_AIR
        elif vertical_type == searches_models_pb2.VERTICAL_TYPE_RAIL:
            pay_vertical_type = companies_models_pb2.VERTICAL_TYPE_RAIL
        else:
            pay_vertical_type = companies_models_pb2.VERTICAL_TYPE_UNSPECIFIED

        try:
            quote: pay_grpc_pb2.CreateQuotationResponse = (
                await self._pay_transactions_service.CreateQuotation(
                    pay_grpc_pb2.CreateQuotationRequest(
                        amount=amount,
                        from_currency=provider_currency,
                        to_currency=reseller_currency,
                        payer_id=payer.company.id,
                        beneficiary_id=beneficiary.company.id,
                        vertical_type=pay_vertical_type,
                    ),
                )
            )
        except grpc.aio.AioRpcError as err:
            self._logger.exception(
                "Error creating quote in PAY",
                amount=amount,
                from_currency=provider_currency,
                to_currency=reseller_currency,
                payer_id=payer.company.id,
                beneficiary_id=beneficiary.company.id,
                vertical_type=pay_vertical_type,
            )
            raise PayCreateQuoteError() from err

        return quote

    async def _get_company(
        self,
        company_id: str,
    ) -> companies_grpc_pb2.GetCompanyResponse:
        try:
            return await self._pay_companies_service.GetCompany(
                companies_grpc_pb2.GetCompanyRequest(id=company_id),
            )
        except grpc.StatusCode.NOT_FOUND as err:
            self._logger.exception(
                "Failed to retrieve company in PAY",
                company_id=company_id,
            )
            raise PayCreateQuoteError() from err
