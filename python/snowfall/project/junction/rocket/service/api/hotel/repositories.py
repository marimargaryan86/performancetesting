import orjson

from snowfall.project.junction.rocket.service.api.hotel.models import HotelSearchResult
from snowfall.project.junction.rocket.service.api.hotel.types import (
    AbstractHotelSearchRepo,
)
from snowfall.stdlib.persistence.mongo import repository


class HotelSearchRepo(repository.DefaultRepository, AbstractHotelSearchRepo):
    async def insert(self, value: HotelSearchResult) -> None:
        # Using model_dump_json so UUIDs are converted to strs.
        json_str = value.model_dump_json(exclude_none=True)
        return await self._execute(
            self._collection.insert_one,
            orjson.loads(json_str),
        )
        # TODO(jeremy): raise if 'acknowledged' False

    async def exists_id(self, search_id: str) -> bool:
        document = await self._execute(
            self._collection.find_one,
            {"id": search_id},
        )
        return bool(document)

    async def find_by_id(self, id_: str) -> HotelSearchResult:
        result = await self._execute(
            self._collection.find_one,
            {"id": id_},
        )
        if not result:
            raise ValueError("No result for id:{0}".format(id_))
        return HotelSearchResult(**result)
