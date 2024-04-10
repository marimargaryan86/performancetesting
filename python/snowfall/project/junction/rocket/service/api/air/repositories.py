from snowfall.project.junction.rocket.service.api.air.models import AirSearchResult
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class AirSearchResultRepository(
    repository.PydanticRepository[AirSearchResult],
    mixins.InsertMixin[AirSearchResult],
    mixins.ExistsMixin[AirSearchResult],
    mixins.FindByIdMixin[AirSearchResult],
):
    _model = AirSearchResult

    async def find_by_search_id(
        self,
        search_id: str,
    ) -> resultset.ResultSet[AirSearchResult]:
        return await self._execute(
            query=self._collection.find,
            filter_pre_cursor={"search_id": search_id},
        )
