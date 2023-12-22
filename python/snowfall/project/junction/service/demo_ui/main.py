import jinja2
from google.protobuf import json_format
from grpc import aio
from starlette import (
    exceptions,
    requests,
    responses,
    routing,
    staticfiles,
    status,
    templating,
)

from snowfall.project.junction.service.gateway.v1 import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import application, grpc_factory


class _Settings(starlette.Settings):
    gateway_address: str


class Routes(object):
    def __init__(
        self,
        *,
        templates: templating.Jinja2Templates,
        trips_stub: trips_pb2_grpc.TripServiceStub,
    ) -> None:
        self._logger = stdout.get_logger()
        self._templates = templates
        self._trips_stub = trips_stub

    async def get_index(self, request: requests.Request) -> responses.Response:
        return self._templates.TemplateResponse(request, "index.html.jinja")

    async def get_trips(self, request: requests.Request) -> responses.Response:
        try:
            response = await self._trips_stub.DrainTripSearchResults(
                request=trips_pb2.DrainTripSearchResultsRequest(
                    id=str(request.path_params["id"]),
                ),
                timeout=10,
            )
        except aio.AioRpcError as err:
            self._logger.exception()
            raise exceptions.HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from err

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                response,
                including_default_value_fields=True,
            ),
        )

    async def post_trips(self, request: requests.Request) -> responses.Response:
        body = await request.json()

        try:
            gw_request = json_format.ParseDict(
                body,
                trips_pb2.EnqueueTripSearchRequest(),
            )
        except json_format.ParseError as err:
            self._logger.exception()
            raise exceptions.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from err

        try:
            gw_response = await self._trips_stub.EnqueueTripSearch(
                gw_request,
                timeout=10,
            )
        except aio.AioRpcError as err2:
            self._logger.exception()
            raise exceptions.HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from err2

        return responses.JSONResponse(
            content=json_format.MessageToDict(
                gw_response,
                including_default_value_fields=True,
            ),
        )


async def _serve(
    app: application.Application[_Settings],
) -> None:
    loader = jinja2.PackageLoader(
        package_name="snowfall.project.junction.service.demo_ui.main",
    )
    environment = jinja2.Environment(loader=loader, autoescape=True)
    templates = templating.Jinja2Templates(env=environment)
    trips_stub = trips_pb2_grpc.TripServiceStub(
        channel=await grpc_factory.make_insecure_channel(
            app=app,
            target=app.settings.gateway_address,
        ),
    )
    routes = Routes(templates=templates, trips_stub=trips_stub)
    asgi_app = starlette.create_starlette_app(
        routes=[
            routing.Route("/", endpoint=routes.get_index, methods=["GET"]),
            routing.Mount(
                "/static",
                staticfiles.StaticFiles(
                    packages=[
                        ("snowfall.project.junction.service.demo_ui.main", "static"),
                    ],
                ),
            ),
            routing.Route(
                "/trips/{id:uuid}",
                endpoint=routes.get_trips,
                methods=["GET"],
            ),
            routing.Route("/trips", endpoint=routes.post_trips, methods=["POST"]),
        ],
        openapi_path=None,
        security_headers=False,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="demo-ui", cli_tool=True)

    entrypoint.enter_with_commands(
        application.Command(
            name="serve",
            callback=_serve,
            settings_class=_Settings,
        ),
    )
