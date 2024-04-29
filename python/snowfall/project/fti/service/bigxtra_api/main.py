import json
import random

import aiofiles
import lagom
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from snowfall.project.fti.service.bigxtra_api import bootstrap, repository
from snowfall.project.fti.service.bigxtra_api.routes import router
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application

_schema_path = filesystem.resource_path(
    "snowfall.project.fti.openapi",
    "openapi.json",
)


async def _http(app: application.Application[bootstrap.Settings]) -> None:
    engine = create_async_engine(
        "{0}/{1}".format(
            random.choice(app.settings.postgresql_dsn),  # noqa: S311
            app.settings.db_name,
        ),
    )
    session = async_sessionmaker(engine, expire_on_commit=False)
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                fti_repository=repository.Repository(session),
            ),
        ),
        openapi_path=_schema_path,
    )
    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


async def _schema(app: application.Application[starlette.Settings]) -> None:
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
    )
    sch = schemas.get_schema(
        routes=router.get_routes(lagom.Container()),
    )
    async with aiofiles.open(_schema_path, "w", encoding="locale") as file:
        await file.write(json.dumps(sch, ensure_ascii=False, indent=4))
        await file.write("\n")


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="fti-bigxtra-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
        application.Command(
            name="schema",
            callback=_schema,
            settings_class=starlette.Settings,
        ),
    )
