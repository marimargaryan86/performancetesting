from collections.abc import Mapping
from typing import Any

from snowfall.stdlib.persistence.mongo import repository, resultset


class PlacesRepository(repository.DefaultRepository):
    async def find_places(
        self,
        destination: str | None,
    ) -> resultset.ResultSet[Mapping[str, Any]]:
        if destination:
            aggregate = [
                {"$match": {"destination": destination}},
                {"$group": {"_id": None, "places": {"$addToSet": "$origin"}}},
            ]
        else:  # Setup to search to hotels locations instead
            aggregate = [
                {"$group": {"_id": None, "places": {"$addToSet": "$destination"}}},
            ]
        return await self._execute(
            query=self._collection.aggregate,
            pipeline=aggregate,
        )
