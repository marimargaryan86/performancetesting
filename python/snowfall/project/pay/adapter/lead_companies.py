from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        """Fetch a lead company resource."""


class DictClient(Client):
    def __init__(self, lead_companies: Sequence[models_pb2.LeadCompany]):
        self._lead_companies = {
            lead_company.id: lead_company for lead_company in lead_companies
        }

    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        try:
            return self._lead_companies[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err


class GrpcClient(Client):
    def __init__(
        self,
        lead_companies: grpc_pb2_grpc.LeadCompaniesServiceStub,
        timeout: int = 10,
    ):
        self._lead_companies = lead_companies
        self._timeout = timeout

    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        response = await errors.handle_grpc_errors(
            self._lead_companies.GetLeadCompany(
                grpc_pb2.GetLeadCompanyRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

        return response.lead_company
