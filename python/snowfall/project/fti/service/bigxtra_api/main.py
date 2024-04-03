import json
import random

import aiofiles
import lagom
from motor import motor_asyncio

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
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )[app.settings.mongo_db]
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                places_repository=repository.PlacesRepository(mongo["flights"]),
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
    entrypoint = application.Entrypoint(name="bigxtra-api")

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
