from __future__ import annotations

import abc
from typing import Sequence

import grpc

from snowfall.project.junction.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.v1alpha import models_pb2


class NotFoundError(Exception):
    """Raised when a segment is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.SegmentReference:
        """Fetch a segment resource."""


class DictClient(Client):
    def __init__(self, segments: Sequence[models_pb2.SegmentReference]) -> None:
        self._segments = {segment.id: segment for segment in segments}

    async def get(self, segment_id: str) -> models_pb2.SegmentReference:
        if segment_id not in self._segments:
            raise NotFoundError()

        return self._segments[segment_id]


class GrpcClient(Client):
    def __init__(self, segments: trips_pb2_grpc.TripServiceStub, timeout: int = 10):
        self._segments = segments
        self._timeout = timeout

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
