import pathlib
from typing import AsyncIterator, Mapping, Optional, Sequence

import currencycloud
import httpx
import pytest
from motor import motor_asyncio
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.adapter import authentication
from snowfall.project.junction.adapter import currencies, errors
from snowfall.project.junction.service.pay_api import bootstrap
from snowfall.project.junction.service.pay_api.repositories import CompanyRepository
from snowfall.project.junction.service.pay_api.routes import router
from snowfall.project.pay.service.quotations import quotations
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import filesystem


def _create_app(  # noqa: WPS211
    cc_client: currencycloud.Client,
    currencies_client: currencies.Client,
    authentication_client: authentication.Client,
    quotations_repository: quotations.QuotationsRepository,
    companies_repository: CompanyRepository,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_routes(
            bootstrap.create_dependencies(
                cc_client,
                currencies_client,
                authentication_client,
                quotations_repository,
                companies_repository,
            ),
        ),
    )
    app.add_exception_handler(errors.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


@pytest.fixture()
def cc_login() -> str:
    return "cc_login"


@pytest.fixture()
def cc_api_key() -> str:
    return "random_key"


@pytest.fixture()
def cc_env() -> str:
    return "demo"


@pytest.fixture()
def quotations_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> quotations.QuotationsRepository:
    return quotations.QuotationsRepository(
        collection=mongo_client.test.quotations,
    )


@pytest.fixture()
def cc_client(cc_login: str, cc_api_key: str, cc_env: str) -> currencycloud.Client:
    return currencycloud.Client(
        cc_login,
        cc_api_key,
        cc_env,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
    }


@pytest.fixture()
def app(
    cc_client: currencycloud.Client,
    currencies_client: currencies.Client,
    authentication_client: authentication.Client,
    quotations_repository: quotations.QuotationsRepository,
    companies_repository: CompanyRepository,
) -> applications.Starlette:
    return _create_app(
        cc_client=cc_client,
        currencies_client=currencies_client,
        authentication_client=authentication_client,
        quotations_repository=quotations_repository,
        companies_repository=companies_repository,
        openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
    )


@pytest.fixture()
async def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))

        yield client
