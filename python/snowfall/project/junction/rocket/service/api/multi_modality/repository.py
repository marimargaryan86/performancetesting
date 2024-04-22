import datetime

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository


class SuggestionSearchRepository(
    repository.ProtoRepository[multi_modal_pb2.SuggestionSearch],
    mixins.FindByIdMixin[multi_modal_pb2.SuggestionSearch],
    mixins.InsertMixin[multi_modal_pb2.SuggestionSearch],
    mixins.StatusMixin[multi_modal_pb2.SuggestionSearch],
):
    _proto = multi_modal_pb2.SuggestionSearch
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(collection)

        self._ttl = ttl

    async def create_from_criteria(
        self,
        criteria: multi_modal_pb2.SuggestionSearch.Criteria,
    ) -> multi_modal_pb2.SuggestionSearch:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )
        new_search = multi_modal_pb2.SuggestionSearch(
            id=string.uuid(),
            criteria=criteria,
            status=multi_modal_pb2.SuggestionSearch.STATUS_PENDING,
            expires_at=expires_at,
        )

        return await self.insert(new_search)


class SuggestionRepository(
    repository.ProtoRepository[multi_modal_pb2.Suggestion],
    mixins.FindByIdMixin[multi_modal_pb2.Suggestion],
    mixins.InsertMixin[multi_modal_pb2.Suggestion],
):
    _proto = multi_modal_pb2.Suggestion
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(collection)

        self._ttl = ttl

    async def create(self) -> multi_modal_pb2.Suggestion:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )
        new_suggestion = multi_modal_pb2.Suggestion(
            id=string.uuid(),
            expires_at=expires_at,
        )

        return await self.insert(new_suggestion)
