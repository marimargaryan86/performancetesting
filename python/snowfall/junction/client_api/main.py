import uvicorn
from starlette import applications

from snowfall.junction.client_api import (
    bootstrap,
    journeys,
    loaders,
    patch,
    places,
    validation,
)


def _factory() -> applications.Starlette:
    patch.patch_open_api()
    places_db = [
        {"id": "f236a92c-4cfa-468e-85ef-431d25dcd925"},
        {"id": "488a836d-ec22-439b-a9d8-3c4c386a731e"},
    ]

    return bootstrap.create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
        dependencies=bootstrap.create_dependencies(
            place_repository=places.PlaceRepository(places_db),
            journey_search_repository=journeys.JourneySearchRepository(),
        ),
    )


if __name__ == "__main__":
    settings = bootstrap.Settings()

    uvicorn.run(
        app="snowfall.junction.client_api.main:_factory",
        factory=True,
        host=settings.http_address,
        port=settings.http_port,
        access_log=False,
        reload=settings.reload,
    )
