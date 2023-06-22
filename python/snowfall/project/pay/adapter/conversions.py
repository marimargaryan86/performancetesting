from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.transactions.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Conversion:
        """Fetch a conversion resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListConversionsResponse:
        """Fetch all conversion resources."""


class DictClient(Client):
    def __init__(self, conversions: Sequence[models_pb2.Conversion]) -> None:
        self._conversions = {conversion.id: conversion for conversion in conversions}

    async def get(self, conversion_id: str) -> models_pb2.Conversion:
        try:
            return self._conversions[conversion_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListConversionsResponse:
        page = sequence.paginate(
            sequence=list(self._conversions.values()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListConversionsResponse(
            conversions=page.sequence,
            next_page_token=page.cursor,
        )


class GrpcClient(Client):
    def __init__(
        self,
        conversions: grpc_pb2_grpc.ConversionsServiceStub,
        timeout: int = 10,
    ):
        self._conversions = conversions
        self._timeout = timeout

    async def get(self, conversion_id: str) -> models_pb2.Conversion:
        response = await errors.handle_grpc_errors(
            self._conversions.GetConversion(
                grpc_pb2.GetConversionRequest(id=conversion_id),
                timeout=self._timeout,
            ),
        )

        return response.conversion

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListConversionsResponse:
        request = grpc_pb2.ListConversionsRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._conversions.ListConversions(request, timeout=self._timeout),
        )
