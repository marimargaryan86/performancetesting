import lagom

from snowfall.project.junction.go.adapter import locations, places
from snowfall.project.junction.go.service.admin_api import includes
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    places_address: str


def create_dependencies(
    locations_client: locations.Client,
    places_client: places.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[locations.Client] = locations_client  # type: ignore[type-abstract]
    container[places.Client] = places_client  # type: ignore[type-abstract]

    includes.register_resolvers(locations_client)

    return container
