from snowfall.project.junction.rocket.service.api.air.models import (
    AirSearchRequestStorage,
    AirSearchResult,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class AirSearchRequestRepository(
    repository.PydanticRepository[AirSearchRequestStorage],
    mixins.InsertMixin[AirSearchRequestStorage],
    mixins.ExistsMixin[AirSearchRequestStorage],
    mixins.FindByIdMixin[AirSearchRequestStorage],
):
    _model = AirSearchRequestStorage

    async def find_by_search_id(
        self,
        identifier: str,
    ) -> AirSearchRequestStorage | None:
        return await self._execute(self._collection.find_one, {"search_id": identifier})


class AirSearchResultRepository(
    repository.PydanticRepository[AirSearchResult],
    mixins.InsertMixin[AirSearchResult],
    mixins.ExistsMixin[AirSearchResult],
    mixins.FindByIdMixin[AirSearchResult],
):
    _model = AirSearchResult

    async def find_results_by_search_id(
        self,
        search_id: str,
    ) -> resultset.ResultSet[AirSearchResult]:
        return await self._execute(
            query=self._collection.find,
            filter_pre_cursor={"search_id": search_id},
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
