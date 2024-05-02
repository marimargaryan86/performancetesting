import datetime
from typing import TypeAlias

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.api.multi_modality import search
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class SuggestionSearchRepository(
    repository.ProtoRepository[multi_modal_pb2.SuggestionSearch],
    mixins.FindByIdMixin[multi_modal_pb2.SuggestionSearch],
    mixins.InsertMixin[multi_modal_pb2.SuggestionSearch],
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

    async def mark_as_completed(
        self,
        identifier: str,
    ) -> multi_modal_pb2.SuggestionSearch:
        return await self._set_status(
            identifier,
            multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED,
        )

    async def mark_as_failed(self, identifier: str) -> multi_modal_pb2.SuggestionSearch:
        return await self._set_status(
            identifier,
            multi_modal_pb2.SuggestionSearch.STATUS_FAILED,
        )

    async def mark_as_processing(
        self,
        identifier: str,
    ) -> multi_modal_pb2.SuggestionSearch:
        return await self._set_status(
            identifier,
            multi_modal_pb2.SuggestionSearch.STATUS_PROCESSING,
        )

    async def _set_status(
        self,
        identifier: str,
        status: multi_modal_pb2.SuggestionSearch.Status.ValueType,
    ) -> multi_modal_pb2.SuggestionSearch:
        return await self._execute(
            self._collection.find_one_and_update,
            {repository.mongo_id_key: identifier},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )


SuggestionType: TypeAlias = (
    search.Suggestion[search.Offer] | search.Suggestion[search.RoundtripOffer]
)


class SuggestionRepository(
    repository.ProtoRepository[multi_modal_pb2.Suggestion],
    mixins.FindByIdMixin[multi_modal_pb2.Suggestion],
    mixins.InsertMixin[multi_modal_pb2.Suggestion],
):
    _proto = multi_modal_pb2.Suggestion
    _indexes = (
        pymongo.IndexModel("suggestion_search_id", background=True),
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(collection)

        self._ttl = ttl

    async def create(
        self,
        suggestion_search_id: str,
        suggestion: SuggestionType,
    ) -> multi_modal_pb2.Suggestion:
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )
        new_suggestion = multi_modal_pb2.Suggestion(
            id=string.uuid(),
            suggestion_search_id=suggestion_search_id,
            expires_at=expires_at,
            offers=[
                multi_modal_pb2.Suggestion.Offer(
                    id=offer.id,
                    segment_type=offer.type,
                )
                for offer in suggestion.offers
            ],
        )

        return await self.insert(new_suggestion)

    async def find_by_suggestion_search_id(
        self,
        identifier: str,
        cursor: str | None = None,
    ) -> resultset.ResultSet[multi_modal_pb2.Suggestion]:
        filter_ = {
            "suggestion_search_id": {
                "$eq": identifier,
            },
        }

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )
