from __future__ import annotations

import functools
import json
import re
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from starlette import (
    datastructures,
    endpoints,
    exceptions,
    requests,
    responses,
    routing,
    status,
)

from snowfall.stdlib import sequence, string, types
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)

if TYPE_CHECKING:
    from google.protobuf.internal import enum_type_wrapper


async def _parse_request_body(
    request: requests.Request,
) -> types.PrimitiveMapping:
    if request.method not in {"POST", "PATCH"}:
        return {}

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return {}

    if "data" not in body:
        return body

    return request_helpers.flatten_request_body(body)


def to_route(
    path: str,
    endpoint: Callable[[messages.Request], Awaitable[responses.Response]],
    methods: Sequence[str] | None = None,
    name: str | None = None,
) -> routing.Route:
    @functools.wraps(endpoint)
    async def wrapper(request: requests.Request) -> responses.Response:
        return await endpoint(
            messages.Request(
                body=await _parse_request_body(request),
                pagination=pagination_helpers.get_pagination(request),
                path_params=request.path_params,
                query_params=request.scope.get(
                    "parsed_query_string",
                    request.query_params,
                ),
                starlette_request=request,
            ),
        )

    return routing.Route(
        path=path,
        endpoint=wrapper,
        methods=list(methods) if methods else None,
        name=name,
    )


class Proxy(object):
    def __init__(
        self,
        client: httpx.AsyncClient,
        prefix: str = "",
        allow: Sequence[tuple[str, re.Pattern[str]]] | None = None,
        deny: Sequence[tuple[str, re.Pattern[str]]] | None = None,
        pop_headers: Sequence[str] | None = None,
    ) -> None:
        if not str(client.base_url):
            raise RuntimeError("A base URL must be set to use the proxy route")

        if allow and deny:
            raise RuntimeError("allow and deny can't both be specified")

        self._allow = allow
        self._client = client
        self._deny = deny
        self._prefix = "/{0}".format(prefix.lstrip("/"))
        self._pop_headers = [
            "host",
            *self._client.headers.keys(),
            *(pop_headers or []),
        ]

    def to_route(self) -> routing.Route:
        return routing.Route(
            "/".join((self._prefix.rstrip("/"), "{path:path}")),
            endpoint=self._route,
            methods=["POST", "GET", "PATCH", "DELETE"],
        )

    def _clean_headers(self, request: requests.Request) -> dict[str, Any]:
        headers = dict(request.headers)
        for header in self._pop_headers:
            headers.pop(header, None)
        return headers

    async def _route(
        self,
        request: requests.Request,
    ) -> responses.Response:
        response = await self._client.request(
            method=request.method,
            url="{0}?{1}".format(
                request.path_params["path"],
                request.url.query,
            ).rstrip("?"),
            content=await request.body(),
            headers=self._clean_headers(request),
        )

        their_base_url = str(self._client.base_url).encode()
        our_base_url = str(
            self._client.base_url.copy_with(
                scheme="https" if request.url.is_secure else "http",
                host=request.url.hostname,
                port=request.url.port,
                path=self._prefix,
            ),
        ).encode()

        return responses.Response(
            content=response.content.replace(their_base_url, our_base_url),
            status_code=response.status_code,
            media_type=response.headers["Content-Type"],
            headers={
                h_key: h_value
                for h_key, h_value in response.headers.items()
                if h_key.startswith("x")
            },
        )


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(
            models.Body(
                meta={"status": "pass"},
                links={"self": str(request.url_for("Health"))},
            ),
        )


_EnumValue = TypeVar("_EnumValue", bound=int)


class ListAndViewEnum(object):
    def __init__(
        self,
        enum: enum_type_wrapper._EnumTypeWrapper[_EnumValue],
        resource_factory: Callable[[Any, datastructures.URL], models.Resource],
        path: str,
    ) -> None:
        self._enum = enum
        self._path = path.lstrip("/").rstrip("/")
        self._resource_factory = resource_factory
        self._list_route_name = string.to_upper_camel(
            "list-{0}".format(self._path).replace("/", " "),
        )
        self._view_route_name = string.to_upper_camel(
            "view-{0}".format(self._path).replace("/", " "),
        )

    def to_routes(self) -> tuple[routing.Route, routing.Route]:
        return (
            routing.Route(
                path="/{0}".format(self._path),
                endpoint=self._list,
                methods=["GET"],
                name=self._list_route_name,
            ),
            routing.Route(
                path="/{0}/{{enumId}}".format(self._path),
                endpoint=self._view,
                methods=["GET"],
                name=self._view_route_name,
            ),
        )

    def _to_id(self, leg_type: int) -> str:
        return protobuf.enum_value_to_slug(
            enum_descriptor=self._enum.DESCRIPTOR,
            enum_value=leg_type,
        )

    async def _list(
        self,
        request: requests.Request,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=sorted(
                (
                    enum_value.number
                    for enum_value in self._enum.DESCRIPTOR.values  # noqa: PD011
                ),
                key=self._to_id,
            ),
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    self._resource_factory(
                        enum_value,
                        request.url_for(
                            self._view_route_name,
                            enumId=self._to_id(enum_value),
                        ),
                    )
                    for enum_value in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(self._list_route_name),
                    sequence_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )

    async def _view(
        self,
        request: requests.Request,
    ) -> responses.Response:
        try:
            enum_value = protobuf.slug_to_enum_value(
                self._enum,
                request.path_params["enumId"],
            )
        except ValueError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return await messages.create_response(
            body=models.Body(
                data=self._resource_factory(
                    enum_value,
                    request.url_for(
                        self._view_route_name,
                        enumId=request.path_params["enumId"],
                    ),
                ),
            ),
            request=request,
        )
