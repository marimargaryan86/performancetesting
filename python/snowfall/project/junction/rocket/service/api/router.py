import lagom
from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.car_rental.endpoints import (
    searches as car_rental_search,
)


def get_routes(dependencies: lagom.Container) -> list[routing.BaseRoute]:
    integration = starlette.StarletteIntegration(dependencies)

    return [
        integration.route(
            "/car-rental/searches/{searchId}/results",
            car_rental_search.CarSearchResults,
            name="ListCarSearchResults",
        ),
    ]
