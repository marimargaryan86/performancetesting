from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib import sequence
from snowfall.stdlib.v1alpha import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListSegmentsResponse:
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
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListSegmentsResponse:
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

        return trips_pb2.ListSegmentsResponse(
            segments=page.sequence,
            next_page_token=page.cursor,
        )

    async def get(self, segment_id: str) -> models_pb2.SegmentReference:
        if segment_id not in self._segments:
            raise errors.NotFoundError()

        return self._segments[segment_id]


class GrpcClient(Client):
    def __init__(self, segments: trips_pb2_grpc.TripServiceStub, timeout: int = 10):
        self._segments = segments
        self._timeout = timeout

    async def find(
        self,
        identifiers: Sequence[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> trips_pb2.ListSegmentsResponse:
        # todo: handle INVALID_ARGUMENT
        request = trips_pb2.ListSegmentsRequest(
            page_token=cursor or "",
            ids=identifiers or [],
        )

        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._segments.ListSegments(request, timeout=self._timeout),
        )

    async def get(self, segment_id: str) -> models_pb2.SegmentReference:
        response = await errors.handle_grpc_errors(
            self._segments.GetSegment(
                trips_pb2.GetSegmentRequest(id=segment_id),
                timeout=self._timeout,
            ),
        )

        return response.segment
