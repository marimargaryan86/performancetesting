from collections.abc import Sequence

import pymongo

from snowfall.project.junction.rocket.service.api.flights.models import (
    FlightSearchRequestStorage,
    FlightSearchResult,
    RocketTrip,
)
from snowfall.project.junction.rocket.service.api.v1alpha import pricing_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class FlightSearchRequestRepository(
    repository.PydanticRepository[FlightSearchRequestStorage],
    mixins.InsertMixin[FlightSearchRequestStorage],
    mixins.ExistsMixin[FlightSearchRequestStorage],
    mixins.FindByIdMixin[FlightSearchRequestStorage],
):
    _model = FlightSearchRequestStorage
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find_by_search_id(
        self,
        identifier: str,
    ) -> FlightSearchRequestStorage | None:
        return await self._execute(self._collection.find_one, {"_id": identifier})


# TODO(jeremy): Add new repository for ResultDetails (https://git.snowfall.se/junction/junction/-/merge_requests/5178#note_252722)


class FlightSearchResultRepository(
    repository.PydanticRepository[FlightSearchResult],
    mixins.InsertMixin[FlightSearchResult],
    mixins.ExistsMixin[FlightSearchResult],
    mixins.FindByIdMixin[FlightSearchResult],
):
    _model = FlightSearchResult
    _indexes = (
        pymongo.IndexModel("offers._id", background=True),
        pymongo.IndexModel("result_details._id", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find_results_by_search_id(
        self,
        search_id: str,
    ) -> resultset.ResultSet[FlightSearchResult]:
        return await self._execute(
            query=self._collection.find,
            filter={"search_id": search_id},
        )

    async def find_any_result_by_search_id(
        self,
        identifier: str,
    ) -> bool:
        return (
            await self._execute(
                self._collection.find_one,
                {"search_id": identifier},
                projection={repository.mongo_id_key: 1},
            )
            is not None
        )

    async def find_result_by_offer_id(
        self,
        identifier: str,
    ) -> FlightSearchResult:
        return await self._execute(
            self._collection.find_one,
            {"offers._id": identifier},
        )

    async def find_results_by_offer_ids(
        self,
        identifiers: Sequence[str],
    ) -> resultset.ResultSet[FlightSearchResult]:
        return await self._execute(
            self._collection.find,
            {"offers._id": {"$in": identifiers}},
        )

    async def find_result_by_result_detail_id(
        self,
        identifier: str,
    ) -> FlightSearchResult:
        return await self._execute(
            self._collection.find_one,
            {"result_details._id": identifier},
        )

    async def find_results_by_result_detail_ids(
        self,
        identifiers: Sequence[str],
    ) -> resultset.ResultSet[FlightSearchResult]:
        return await self._execute(
            self._collection.find,
            {"result_details._id": {"$in": identifiers}},
        )


class RocketTripRepository(
    repository.PydanticRepository[RocketTrip],
    mixins.UpsertMixin[RocketTrip],
):
    _model = RocketTrip
    _indexes = (
        pymongo.IndexModel("offer_id", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def find_by_offer_id(self, offer_id: str) -> RocketTrip | None:
        return await self._execute(self._collection.find_one, {"offer_id": offer_id})


class QuoteRepository(
    repository.ProtoRepository[pricing_pb2.Quote],
    mixins.UpsertMixin[pricing_pb2.Quote],
    mixins.InsertMixin[pricing_pb2.Quote],
):
    _proto = pricing_pb2.Quote
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def update_status(
        self,
        identifier: str,
        status: pricing_pb2.Quote.Status.ValueType,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {"_id": identifier},
            {"$set": {"status": status}},
        )
