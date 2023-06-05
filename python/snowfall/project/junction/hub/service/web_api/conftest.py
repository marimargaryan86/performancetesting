import pytest
from starlette import applications

from snowfall.project.junction.hub.service.web_api import bootstrap, router
from snowfall.stdlib.integration.starlette import application


def _create_app() -> applications.Starlette:
    return application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(),
        ),
        openapi_path=None,
        security_headers=False,
    )


@pytest.fixture()
def app() -> applications.Starlette:
    return _create_app()
