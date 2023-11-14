# WPS110
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from typing import Any, Generic, TypeVar

from pydantic import ConfigDict

from snowfall.stdlib.integration.pydantic import model


class DuffelBaseModel(model.DefaultingBaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


DATA = TypeVar("DATA")


class DuffelResponse(DuffelBaseModel, Generic[DATA]):
    data: DATA


class RemoteListMeta(DuffelBaseModel):
    limit: int | None = None
    before: str | None = None
    after: str | None = None


# list pagination request is slightly different then meta dict of a response
# but we we anly care about these 3 attributes which are the same
DuffelListRequest = RemoteListMeta


LISTELEM = TypeVar("LISTELEM")


class RemoteListPage(DuffelResponse[Sequence[LISTELEM]], Generic[LISTELEM]):
    meta: RemoteListMeta

    def empty(self) -> bool:
        return not bool(len(self.data))

    def __iter__(self) -> Any:
        return iter(self.data)


class RemoteList(Generic[LISTELEM]):
    def __init__(self, next_page: Callable[..., Awaitable[RemoteListPage[LISTELEM]]]):
        self._next_page = next_page

    def __aiter__(self) -> AsyncIterator[LISTELEM]:
        return self._generator()

    async def _generator(self) -> AsyncIterator[LISTELEM]:
        page = await self._next_page(None)
        while True:
            for element in page:
                yield element

            if not page.meta.after:
                break

            page = await self._next_page(page.meta.after)
