import base64
import functools
import hashlib
from collections.abc import Mapping

import httpx
from starlette import responses, status, templating

from snowfall.project.junction.go.service.dogfood_ui import locations
from snowfall.stdlib import h3, string
from snowfall.stdlib.integration.starlette import messages
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import latlng_pb2

_SESSION_TOKEN_LENGTH = 32


@functools.cache
def _hash_static_resources() -> dict[str, str]:
    hashes = {}
    static_path = filesystem.package_path(
        "snowfall.project.junction.go.service.dogfood_ui.static",
    )

    for static_file_path in static_path.glob("*"):
        if static_file_path.is_dir():
            continue

        with static_file_path.open("rb", buffering=0) as static_file:
            hashes[static_file_path.name] = base64.urlsafe_b64encode(
                hashlib.file_digest(
                    static_file,  # type: ignore[arg-type]
                    "sha512",
                ).digest(),
            ).decode()

    return hashes


_ProvidersReturn = Mapping[
    str,
    tuple[h3.H3MappingRepository[h3.CoordinatesItem], int],
]


async def _providers() -> _ProvidersReturn:
    return {
        "airports": (await locations.load_airports(), 1),
        "benerail": (await locations.load_benerail(), 1),
        "direct_ferries": (await locations.load_direct_ferries(), 1),
        "distribusion": (await locations.load_distribusion(), 1),
        "save_a_train": (await locations.load_save_a_train(), 1),
    }


def _is_city(place_response: httpx.Response) -> bool:
    type_ids = {
        type_["id"]
        for type_ in place_response.json()["data"]["relationships"]["types"]["data"]
    }

    return "city" in type_ids


class Locations:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get(
        self,
        request: messages.Request,
    ) -> responses.Response:
        place_response = await self._client.get(
            "/places/{0}".format(request.query_params.get("id")),
        )

        place_response.raise_for_status()

        if _is_city(place_response):
            return responses.Response(status_code=status.HTTP_400_BAD_REQUEST)

        mapping_results = {}

        for provider, repository_neighbour_tuple in (await _providers()).items():
            mapping_results[provider] = [
                mapping_result.identifier
                for mapping_result in repository_neighbour_tuple[0].find_mapped_values(
                    latlng_pb2.LatLng(
                        latitude=place_response.json()["data"]["attributes"][
                            "latitude"
                        ],
                        longitude=place_response.json()["data"]["attributes"][
                            "longitude"
                        ],
                    ),
                    repository_neighbour_tuple[1],
                )
            ]

        return responses.JSONResponse(content=mapping_results)


class UI:
    def __init__(self, template: templating.Jinja2Templates) -> None:
        self._template = template

    async def get(
        self,
        request: messages.Request,
    ) -> responses.Response:
        return self._template.TemplateResponse(
            "layout.html",
            {
                "request": request.starlette_request,
                "session_token": string.random(_SESSION_TOKEN_LENGTH),
                "hashes": _hash_static_resources(),
            },
        )
