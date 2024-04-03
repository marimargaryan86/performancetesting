import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, TypeAlias

from starlette import requests, responses, routing, status

from snowfall.project.junction.extensions.service.mobile_api import repository
from snowfall.stdlib.integration.starlette import models

_ResourceFunction: TypeAlias = Callable[[], Awaitable[Mapping[str, Any]]]


class CacheAndListEnum:
    def __init__(
        self,
        resource_function: _ResourceFunction,
        cache_repo: repository.EnumsValuesRepository,
        path: str,
    ):
        self._path = path.lstrip("/")
        self._resource_function = resource_function
        self._cache_repo = cache_repo

    def to_route(self) -> routing.Route:
        return routing.Route(
            "/{0}".format(self._path),
            endpoint=self._route,
            methods=["GET"],
        )

    async def _route(
        self,
        request: requests.Request,
    ) -> responses.Response:
        cache_key = self._path.lstrip("/").rstrip("/").replace("/", "-")
        cached_response = await self._cache_repo.get(cache_key)
        if cached_response is None:
            response = await self._resource_function()
            await self._cache_repo.create(cache_key, json.dumps(response))
        else:
            response = json.loads(cached_response)

        return models.JsonApiResponse(
            models.Body(
                **response,
            ),
            status.HTTP_200_OK,
        )
