import lagom
from lagom.integrations.starlette import StarletteIntegration
from starlette import routing

from snowfall.project.fti.service.bigxtra_api.routes import examples, places
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


def get_routes(
    dependencies: lagom.Container,
) -> list[routing.BaseRoute]:
    integration = StarletteIntegration(dependencies)
    return [
        SchemaGenerator.to_route(integration, "/places", places.Places, name="Places"),
        SchemaGenerator.to_route(None, "/examples", examples.Examples),
        SchemaGenerator.to_route(None, "/examples/{exampleId}", examples.Example),
    ]
