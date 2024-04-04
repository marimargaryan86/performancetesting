from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, ClassVar, TypedDict, Unpack

from lagom.integrations.starlette import StarletteIntegration
from pydantic import BaseModel
from starlette import requests, responses, status
from starlette.routing import BaseRoute, Route
from starlette.schemas import BaseSchemaGenerator

_default_http_code = status.HTTP_200_OK

Handler = Callable[[Any, requests.Request], Awaitable[responses.Response]]


class SchemaArgs(TypedDict, total=False):
    request_body: type[BaseModel]
    response_body: type[BaseModel]
    query_parameters: type[BaseModel]
    path_parameters: type[BaseModel]
    status_code: int
    description: str
    summary: str


class SchemaGenerator(BaseSchemaGenerator):
    _endpoints: ClassVar[dict[Handler, Any]] = {}
    _routes: ClassVar[list[BaseRoute]] = []

    def __init__(self, base_schema: Mapping[str, Any]) -> None:
        self.base_schema = base_schema

    @classmethod
    def schema(
        cls,
        **kwargs: Unpack[SchemaArgs],
    ) -> Callable[[Handler], Handler]:
        def decorator(
            func: Handler,
        ) -> Handler:
            SchemaGenerator._endpoints[func] = {**kwargs}
            return func

        return decorator

    @classmethod
    def to_route(
        cls,
        integration: StarletteIntegration | None,
        *args: Any,
        **kwargs: Any,
    ) -> BaseRoute:
        cls._routes.append(Route(*args, **kwargs))
        if integration:
            return integration.route(*args, **kwargs)
        return Route(*args, **kwargs)

    def get_schema(  # noqa: WPS231, C901, PLR0912
        self,
        routes: list[BaseRoute],  # noqa: SF20
    ) -> dict[str, Any]:
        schema = dict(self.base_schema)
        schema.setdefault("paths", {})
        schema.setdefault("components", {})
        components: dict[str, Any] = {"schemas": {}, "parameters": {}}
        endpoints_info = self.get_endpoints(self._routes)
        for endpoint in endpoints_info:
            signature = SchemaGenerator._endpoints.get(endpoint.func, {})
            endpoint_schema = {}
            response = {}
            parameters: list[Any] = []
            if "query_parameters" in signature:
                query_params = signature.get(
                    "query_parameters",
                ).model_json_schema()
                extracted_params = extract_parameters(query_params, "query")
                for query_parameter in extracted_params:
                    components["parameters"][query_parameter["name"]] = query_parameter
                parameters.extend([
                    {"$ref": "#/components/parameters/{0}".format(param["name"])}
                    for param in extracted_params
                ])
            if "path_parameters" in signature:
                path_parameters = signature.get(
                    "path_parameters",
                ).model_json_schema()
                extracted_params = extract_parameters(path_parameters, "path")
                for path_parameter in extracted_params:
                    components["parameters"][path_parameter["name"]] = path_parameter
                parameters.extend([
                    {"$ref": "#/components/parameters/{0}".format(param["name"])}
                    for param in extracted_params
                ])
            if "description" in signature:
                endpoint_schema["description"] = signature.get("description")
            if "summary" in signature:
                endpoint_schema["summary"] = signature.get("summary")
            if "response_body" in signature:
                response = signature.get("response_body").model_json_schema(
                    ref_template="#/components/schemas/{model}",
                )
                if "$defs" in response:
                    for k, v in response.get("$defs", {}).items():  # noqa: WPS111
                        components["schemas"][k] = v  # noqa: WPS220
                    response.pop("$defs")
            elif signature.get("status_code") != status.HTTP_204_NO_CONTENT:
                raise RuntimeError("Response body cannot be empty")
            if "request_body" in signature:
                request = signature.get("request_body").model_json_schema(
                    ref_template="#/components/schemas/{model}",
                )
                if "$defs" in request:
                    for k2, v2 in request.get("$defs", {}).items():  # noqa: WPS111
                        components["schemas"][k2] = v2  # noqa: WPS220
                    request.pop("$defs")
                endpoint_schema["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": request,
                        },
                    },
                }

            endpoint_schema["responses"] = {
                signature.get("status_code", _default_http_code): {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "schema": response,
                        },
                    },
                },
            }
            if endpoint.path not in schema["paths"]:
                schema["paths"][endpoint.path] = {}
            endpoint_schema["parameters"] = parameters
            schema["paths"][endpoint.path][endpoint.http_method] = endpoint_schema
        schema["components"] = components
        return schema


def extract_parameters(
    schema: Mapping[str, Any],
    parameter_position: str,
) -> Sequence[Any]:
    properties = schema["properties"]
    fields = []
    for name, details in properties.items():
        field = {
            "name": name,
            "in": parameter_position,
            "schema": details,
            "description": details.get("description", ""),
        }
        if name in schema.get("required", []):
            field["required"] = True
        fields.append(field)
    return fields
