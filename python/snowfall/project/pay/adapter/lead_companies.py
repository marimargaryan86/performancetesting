from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence, string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        """Create a lead company resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        """Fetch a lead company resource."""

    @abc.abstractmethod
    async def update(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        """Update a lead company resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListLeadCompaniesResponse:
        """Fetch all lead company resources."""


class DictClient(Client):
    def __init__(self, lead_companies: Sequence[models_pb2.LeadCompany]):
        self._lead_companies = {
            lead_company.id: lead_company for lead_company in lead_companies
        }

    async def create(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        lead_company.id = string.uuid()
        self._lead_companies[lead_company.id] = lead_company

        return lead_company

    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        try:
            return self._lead_companies[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        self._lead_companies[lead_company.id] = lead_company

        return lead_company

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListLeadCompaniesResponse:
        page = sequence.paginate(
            sequence=list(self._lead_companies.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListLeadCompaniesResponse(
            lead_companies=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(
        self,
        lead_companies: grpc_pb2_grpc.LeadCompaniesServiceStub,
        timeout: int = 10,
    ):
        self._lead_companies = lead_companies
        self._timeout = timeout

    async def create(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        response = await errors.handle_grpc_errors(
            self._lead_companies.CreateLeadCompany(
                grpc_pb2.CreateLeadCompanyRequest(
                    lead_company=lead_company,
                ),
                timeout=self._timeout,
            ),
        )

        return response.lead_company

    async def get(self, identifier: str) -> models_pb2.LeadCompany:
        response = await errors.handle_grpc_errors(
            self._lead_companies.GetLeadCompany(
                grpc_pb2.GetLeadCompanyRequest(id=identifier),
                timeout=self._timeout,
            ),
        )

        return response.lead_company

    async def update(
        self,
        lead_company: models_pb2.LeadCompany,
    ) -> models_pb2.LeadCompany:
        response = await errors.handle_grpc_errors(
            self._lead_companies.UpdateLeadCompany(
                grpc_pb2.UpdateLeadCompanyRequest(
                    lead_company=lead_company,
                ),
                timeout=self._timeout,
            ),
        )

        return response.lead_company

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListLeadCompaniesResponse:
        # TODO: handle INVALID_ARGUMENT
        request = grpc_pb2.ListLeadCompaniesRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._lead_companies.ListLeadCompanies(request, timeout=self._timeout),
        )
