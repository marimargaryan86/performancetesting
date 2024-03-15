from collections.abc import Mapping
from typing import Any

from snowfall.stdlib.persistence.mongo import repository


class PlacesRepository(repository.DefaultRepository):
    async def find_by_user_id(self, user_id: str) -> Mapping[str, Any] | None:
        return await self._execute(self._collection.find_one, {"user_id": user_id})
