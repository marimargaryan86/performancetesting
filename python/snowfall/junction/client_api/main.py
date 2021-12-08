import uvicorn
from starlette import applications

from snowfall.junction.client_api import bootstrap, loaders, validation


def _factory() -> applications.Starlette:
    return bootstrap.create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
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
