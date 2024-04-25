from collections.abc import Sequence

import pymongo

from snowfall.project.junction.rocket.service.api.flights.models import (
    FlightSearchRequestStorage,
    FlightSearchResult,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class FlightSearchRequestRepository(
    repository.PydanticRepository[FlightSearchRequestStorage],
    mixins.InsertMixin[FlightSearchRequestStorage],
    mixins.ExistsMixin[FlightSearchRequestStorage],
    mixins.FindByIdMixin[FlightSearchRequestStorage],
):
    _model = FlightSearchRequestStorage

    async def find_by_search_id(
        self,
        identifier: str,
    ) -> FlightSearchRequestStorage | None:
        return await self._execute(self._collection.find_one, {"search_id": identifier})


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
