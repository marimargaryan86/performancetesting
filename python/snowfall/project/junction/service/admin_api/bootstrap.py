from typing import Sequence

import lagom
from lagom.integrations import starlette

from snowfall.project.junction.adapter import locations, places
from snowfall.project.junction.service.admin_api import includes
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    places_address: Sequence[str]
    validate_responses_against_spec: bool = True


def create_dependencies(
    locations_client: locations.Client,
    places_client: places.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[locations.Client] = locations_client  # type: ignore[misc]
    container[places.Client] = places_client  # type: ignore[misc]

    includes.register_resolvers(locations_client)

    return starlette.StarletteIntegration(container)
