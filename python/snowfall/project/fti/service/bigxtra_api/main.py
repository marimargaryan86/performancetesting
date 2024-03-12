import json

import aiofiles

from snowfall.project.fti.service.bigxtra_api.routes import router
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application

_schema_path = filesystem.resource_path(
    "snowfall.project.fti.openapi",
    "openapi.json",
)


async def _http(app: application.Application[starlette.Settings]) -> None:
    asgi_app = starlette.create_starlette_app(
        routes=router.get_routes(),
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
        routes=router.get_routes(),
    )
    async with aiofiles.open(_schema_path, "w", encoding="locale") as file:
        await file.write(json.dumps(sch, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="bigxtra-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=starlette.Settings,
        ),
        application.Command(
            name="schema",
            callback=_schema,
            settings_class=starlette.Settings,
        ),
    )
