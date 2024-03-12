from starlette import routing

from snowfall.project.fti.service.bigxtra_api.routes import examples


def get_routes() -> list[routing.BaseRoute]:
    return [
        routing.Route("/examples", examples.Examples),
        routing.Route("/examples/{exampleId}", examples.Example),
    ]
