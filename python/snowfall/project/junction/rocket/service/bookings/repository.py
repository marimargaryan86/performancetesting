from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pymongo

from snowfall.project.junction.rocket.service.bookings.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


def _add_reseller_id_to_filter(
    reseller_id: str,
    filter_: Mapping[str, Any],
) -> dict[str, Any]:
    filter_ = dict(filter_)

    if reseller_id:
        filter_["$or"] = [
            {"reseller_id": reseller_id},
            {"owner_reseller_ids": {"$in": [reseller_id]}},
        ]

    return filter_


class BookingRepository(
    repository.ProtoRepository[models_pb2.Booking],
    mixins.FindByIdMixin[models_pb2.Booking],
    mixins.InsertMixin[models_pb2.Booking],
):
    _proto = models_pb2.Booking

    async def find(
        self,
        ids: Sequence[str] | None = None,
        cursor: str = "",
        reseller_id: str = "",
    ) -> resultset.ResultSet[models_pb2.Booking]:
        filter_ = {}
        if ids:
            filter_ = {
                "_id": {
                    "$in": ids,
                },
            }

        filter_ = _add_reseller_id_to_filter(reseller_id, filter_)

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def update(
        self,
        booking: models_pb2.Booking,
    ) -> models_pb2.Booking:
        replacement = self._coder.encode(booking)
        replacement.pop(repository.mongo_id_key)

        return await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: booking.id},
            replacement=replacement,
        )

    async def update_status(
        self,
        identifier: str,
        status: models_pb2.Booking.Status.ValueType,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "status": status,
                },
            },
        )


class BookingCancellationRepository(
    repository.ProtoRepository[models_pb2.BookingCancellation],
    mixins.FindByIdMixin[models_pb2.BookingCancellation],
    mixins.InsertMixin[models_pb2.BookingCancellation],
    mixins.UpsertMixin[models_pb2.BookingCancellation],
):
    _proto = models_pb2.BookingCancellation
    _indexes = (pymongo.IndexModel("booking_id", background=True),)

    async def find_by_booking_id(
        self,
        booking_id: str,
    ) -> models_pb2.BookingCancellation | None:
        return await self._execute(
            self._collection.find_one,
            {
                "booking_id": booking_id,
            },
        )

    async def update_ticket_id(self, identifier: str, ticket_id: str) -> None:
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "ticket_id": ticket_id,
                },
            },
        )

    async def mark_as_pending(self, identifier: str) -> None:
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "status": models_pb2.BookingCancellation.STATUS_PENDING,
                },
            },
        )

    async def update_status(
        self,
        identifier: str,
        status: models_pb2.BookingCancellation.Status.ValueType,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "status": status,
                },
            },
        )
