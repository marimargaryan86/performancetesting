from collections.abc import Mapping

from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import grpc_pb2 as pay_grpc_pb2
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as pay_pb2_grpc,
)


class Quotes(object):
    def __init__(
        self,
        pay_transactions_service: pay_pb2_grpc.QuotationsServiceStub,
        pay_companies_service: companies_pb2_grpc.CompaniesServiceStub,
        # TODO(reuben.t): pass from settings
        reseller_pay_company_mapping: Mapping[str, str],
    ):
        self._pay_transactions_service = pay_transactions_service
        self._pay_companies_service = pay_companies_service
        self._reseller_pay_company_mapping = reseller_pay_company_mapping

    async def create_pay_quote(self, reseller_id: str, provider_id: str) -> None:
        reseller_company_id = self._reseller_pay_company_mapping.get(reseller_id)
        payer = self._pay_companies_service.GetCompany(reseller_company_id)

        # TODO(reuben.t): find id of provider, e.g. junction 1 or benerail
        beneficiary = self._pay_companies_service.GetCompany(provider_id)

        # TODO(reuben.t): use payer_id to get company in pay
        if payer and beneficiary:
            await self._pay_transactions_service.CreateQuotation(
                pay_grpc_pb2.CreateQuotationRequest(
                    # TODO(reuben.t): add more info to fill out quote request in params, e.g. amounts etc
                    payer=payer,
                    beneficiary_company=beneficiary,
                ),
            )
