from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.fixtures import ACCOUNTLESS_COMPANIES
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, company: models_pb2.Company) -> models_pb2.Company:
        """Create a company resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Company:
        """Fetch a company resource."""

    @abc.abstractmethod
    async def update(self, company: models_pb2.Company) -> models_pb2.Company:
        """Update a company resource."""

    @abc.abstractmethod
    async def find(
        self,
        identifiers: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        """Fetch all company resources."""

    @abc.abstractmethod
    async def find_accountless(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        """Fetch accountless company resources."""


class DictClient(Client):
    def __init__(self, companies: Sequence[models_pb2.Company]):
        self._companies = {company.id: company for company in companies}
        self._accountless_companies = {
            company_id: self._companies[company_id]
            for company_id in ACCOUNTLESS_COMPANIES
        }

    async def create(self, company: models_pb2.Company) -> models_pb2.Company:
        self._companies[company.id] = company

        return company

    async def get(self, company_id: str) -> models_pb2.Company:
        try:
            return self._companies[company_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def update(self, company: models_pb2.Company) -> models_pb2.Company:
        self._companies[company.id] = company

        return company

    async def find(
        self,
        identifiers: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        if identifiers:
            companies = [
                company
                for company in self._companies.values()
                if company.id in identifiers
            ]
        else:
            companies = list(self._companies.values())
        page = sequence.paginate(
            sequence=companies,
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListCompaniesResponse(
            companies=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_accountless(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        page = sequence.paginate(
            sequence=list(self._accountless_companies.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListCompaniesResponse(
            companies=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(
        self,
        companies: grpc_pb2_grpc.CompaniesServiceStub,
        timeout: int = 10,
    ):
        self._companies = companies
        self._timeout = timeout

    async def create(
        self,
        company: models_pb2.Company,
    ) -> models_pb2.Company:
        response = await errors.handle_grpc_errors(
            self._companies.CreateCompany(
                grpc_pb2.CreateCompanyRequest(
                    company=company,
                ),
            ),
        )

        return response.company

    async def get(self, company_id: str) -> models_pb2.Company:
        response = await errors.handle_grpc_errors(
            self._companies.GetCompany(
                grpc_pb2.GetCompanyRequest(id=company_id),
                timeout=self._timeout,
            ),
        )

        return response.company

    async def update(self, company: models_pb2.Company) -> models_pb2.Company:
        response = await errors.handle_grpc_errors(
            self._companies.UpdateCompany(
                grpc_pb2.UpdateCompanyRequest(
                    company=company,
                ),
                timeout=self._timeout,
            ),
        )

        return response.company

    async def find(
        self,
        identifiers: Sequence[str] = (),
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        # TODO: handle INVALID_ARGUMENT
        request = grpc_pb2.ListCompaniesRequest(
            ids=models_pb2.ListOfIds(ids=identifiers or []),
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._companies.ListCompanies(request, timeout=self._timeout),
        )

    async def find_accountless(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListCompaniesResponse:
        # TODO: handle INVALID_ARGUMENT
        request = grpc_pb2.ListCompaniesRequest(
            page_token=cursor or "",
            is_accountless=True,
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._companies.ListCompanies(request, timeout=self._timeout),
        )
