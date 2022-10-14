from __future__ import annotations

import abc
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.adapter import common
from snowfall.project.junction.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib import sequence
from snowfall.stdlib.v1alpha import models_pb2


class NotFoundError(Exception):
    """Raised when a segment is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> common.ItemsPage[models_pb2.SegmentReference]:
        """Fetch all segment resources."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.SegmentReference:
        """Fetch a segment resource."""


class DictClient(Client):
    def __init__(self, segments: Sequence[models_pb2.SegmentReference]) -> None:
        self._segments = {segment.id: segment for segment in segments}

    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> common.ItemsPage[models_pb2.SegmentReference]:
        all_segments = list(self._segments.values())

        if identifiers:
            all_segments = [
                segment for segment in all_segments if segment.id in identifiers
            ]

        page = sequence.paginate(
            sequence=all_segments,
            cursor=cursor,
            limit=limit,
        )

        return common.ItemsPage(protos=page.sequence, next_page_token=page.cursor)

    async def get(self, segment_id: str) -> models_pb2.SegmentReference:
        if segment_id not in self._segments:
            raise NotFoundError()

        return self._segments[segment_id]


class GrpcClient(Client):
    def __init__(self, segments: trips_pb2_grpc.TripServiceStub, timeout: int = 10):
        self._segments = segments
        self._timeout = timeout

    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> common.ItemsPage[models_pb2.SegmentReference]:
        # todo: handle INVALID_ARGUMENT
        request = trips_pb2.ListSegmentsRequest(
            page_token=cursor or "",
            ids=identifiers or [],
        )

        if limit is not None:
            request.page_size = limit

        response = await common.handle_grpc_errors(
            self._segments.ListSegments(request, timeout=self._timeout),
        )

        return common.ItemsPage(
            protos=response.segments,
            next_page_token=response.next_page_token,
        )

    async def get(self, segment_id: str) -> models_pb2.SegmentReference:
        try:
            response = await self._segments.GetSegment(
                trips_pb2.GetSegmentRequest(id=segment_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Segment with ID '{id}' not found.".format(id=segment_id),
                ) from exc

            raise UnknownError() from exc

        return response.segment
