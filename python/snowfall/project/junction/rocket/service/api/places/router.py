from lagom.integrations import starlette
from starlette import routing

from snowfall.project.junction.rocket.service.api.places import endpoints


def get_routes(integration: starlette.StarletteIntegration) -> list[routing.BaseRoute]:
    return [
        integration.route(
            "/places/{placeId:str}",
            endpoints.GetPlace,
            name="GetPlace",
        ),
    ]
