import asyncio
import json
import pkgutil
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.rocket.service.places import constants
from snowfall.project.junction.rocket.service.places.typing import ProviderTypedDict
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import application, grpc_factory

_logger = stdout.get_logger()


class _GeneratePlacesSettings(application.Settings):
    geodata_address: str
    mongo_dsn: Sequence[AnyUrl]


async def _generate_places(
    app: application.Application[_GeneratePlacesSettings],
) -> None:
    asyncio.get_running_loop().slow_callback_duration = 1

    mongo = motor_asyncio.AsyncIOMotorClient(  # noqa: F841
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(  # noqa: F841
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
    )

    nodes_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "nodes.json",
    )

    if nodes_json is None:
        raise RuntimeError("No nodes.json file present")
    nodes = json.loads(nodes_json.decode("utf-8"))  # noqa: F841

    benerail_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "benerail_stations.json",
    )

    df_json = pkgutil.get_data(
        "snowfall.project.junction.rocket.service.places.main",
        "ports.json",
    )

    provider_json: ProviderTypedDict = {  # noqa: F841
        models_pb2.TYPE_RAILWAY_STATION: {
            constants.BENERAIL_ID: (
                json.loads(
                    benerail_json.decode("utf-8"),
                )
                if benerail_json
                else []
            ),
        },
        models_pb2.TYPE_FERRY_PORT: {
            constants.DF_ID: json.loads(df_json.decode("utf-8")) if df_json else [],
        },
    }


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        application.Command(
            name="generate-places",
            callback=_generate_places,
            settings_class=_GeneratePlacesSettings,
        ),
    )
