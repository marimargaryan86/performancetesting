from __future__ import annotations

import abc
from collections.abc import Sequence

from google.protobuf.field_mask_pb2 import FieldMask

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
    resellers_pb2,
    resellers_pb2_grpc,
)
from snowfall.stdlib import sequence, string


class Client(abc.ABC):
    @abc.abstractmethod
    async def list_resellers(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> resellers_pb2.ListResellersResponse:
        """Fetch all reseller resources."""

    @abc.abstractmethod
    async def get_reseller(
        self,
        identifier: str,
        *,
        fetch_child_resellers: bool = False,
    ) -> models_pb2.Reseller:
        """Fetch a reseller resource."""

    @abc.abstractmethod
    async def create_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        """Fetch a reseller resource."""

    @abc.abstractmethod
    async def update_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        """Update a reseller resource."""


class DictClient(Client):
    def __init__(
        self,
        resellers: Sequence[models_pb2.Reseller],
    ):
        self._resellers = {reseller.id: reseller for reseller in resellers}

    async def list_resellers(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> resellers_pb2.ListResellersResponse:
        resellers = list(self._resellers.values())
        if identifiers:
            resellers = [
                reseller for reseller in resellers if reseller.id in identifiers
            ]

        page = sequence.paginate(
            sequence=resellers,
            cursor=cursor,
            limit=limit,
        )

        return resellers_pb2.ListResellersResponse(
            resellers=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_reseller(
        self,
        identifier: str,
        *,
        fetch_child_resellers: bool = False,
    ) -> models_pb2.Reseller:
        if identifier not in self._resellers:
            raise errors.NotFoundError()

        child_reseller_ids = []
        if fetch_child_resellers:
            for res_id, res in self._resellers.items():
                if identifier in res.parent_reseller_ids:
                    child_reseller_ids.append(res_id)

        reseller = self._resellers[identifier]

        return models_pb2.Reseller(
            id=reseller.id,
            name=reseller.name,
            company_id=reseller.company_id,
            default_currency=reseller.default_currency,
            provider_ids=reseller.provider_ids,
            parent_reseller_ids=reseller.parent_reseller_ids,
            child_reseller_ids=child_reseller_ids if child_reseller_ids else None,
        )

    async def create_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        reseller.id = string.uuid()
        self._resellers[reseller.id] = reseller

        return self._resellers[reseller.id]

    async def update_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        if reseller.id not in self._resellers:
            raise errors.NotFoundError()

        if reseller.provider_ids:
            self._resellers[reseller.id].ClearField("provider_ids")

        self._resellers[reseller.id].MergeFrom(
            models_pb2.Reseller(
                name=reseller.name,
                default_currency=reseller.default_currency,
                provider_ids=reseller.provider_ids,
                company_id=reseller.company_id,
            ),
        )

        return self._resellers[reseller.id]


class GrpcClient(Client):
    def __init__(
        self,
        resellers: resellers_pb2_grpc.ResellerServiceStub,
        timeout: int = 10,
    ):
        self._resellers = resellers
        self._timeout = timeout

    async def list_resellers(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> resellers_pb2.ListResellersResponse:
        request = resellers_pb2.ListResellersRequest(
            ids=models_pb2.ListOfIds(ids=identifiers or []),
            page_token=cursor or "",
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._resellers.ListResellers(request, timeout=self._timeout),
        )

    async def get_reseller(
        self,
        identifier: str,
        *,
        fetch_child_resellers: bool = False,
    ) -> models_pb2.Reseller:
        response = await errors.handle_grpc_errors(
            self._resellers.GetReseller(
                resellers_pb2.GetResellerRequest(
                    id=identifier,
                    fetch_child_resellers=fetch_child_resellers,
                ),
                timeout=self._timeout,
            ),
        )

        return response.reseller

    async def create_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        response = await errors.handle_grpc_errors(
            self._resellers.CreateReseller(
                resellers_pb2.CreateResellerRequest(
                    reseller=reseller,
                ),
                timeout=self._timeout,
            ),
        )

        return response.reseller

    async def update_reseller(
        self,
        reseller: models_pb2.Reseller,
    ) -> models_pb2.Reseller:
        response = await errors.handle_grpc_errors(
            self._resellers.UpdateReseller(
                resellers_pb2.UpdateResellerRequest(
                    reseller=reseller,
                    update_mask=FieldMask(
                        paths=[
                            field.name
                            for field in reseller.DESCRIPTOR.fields
                            if getattr(reseller, field.name) is not None
                        ],
                    ),
                ),
                timeout=self._timeout,
            ),
        )

        return response.reseller
