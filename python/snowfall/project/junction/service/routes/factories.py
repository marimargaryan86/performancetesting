import zipfile

import aiofiles
import orjson
import pydantic

from snowfall.project.junction.service.routes import gtfs, nodes, repositories, stops
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory, mongo_factory


class ImportSettings(application.Settings):
    geodata_address: str
    mongo_dsn: pydantic.MongoDsn


class GtfsSettings(ImportSettings):
    gtfs_zip_path: pydantic.FilePath = pydantic.Field(
        json_schema_extra={"argument": True},
    )


async def import_nodes(app: application.Application[ImportSettings]) -> None:
    geocoding_service = geocoding_pb2_grpc.GeocodingServiceStub(
        await grpc_factory.make_insecure_channel(app, app.settings.geodata_address),
    )
    node_importer = nodes.NodeImporter(
        geodata=geocoding_service,
        repository=repositories.NodeRepository(
            (
                await mongo_factory.make_database(
                    app=app,
                    dsn=app.settings.mongo_dsn,
                )
            ).nodes,
        ),
    )
    async with aiofiles.open(
        filesystem.resource_path(__name__, "nodes.json"),
    ) as node_file:
        raw_nodes = orjson.loads(await node_file.read())

    await node_importer.import_nodes(raw_nodes)


async def import_stops(app: application.Application[GtfsSettings]) -> None:
    importer = stops.StopImporter(
        repository=repositories.StopRepository(
            (
                await mongo_factory.make_database(
                    app=app,
                    dsn=app.settings.mongo_dsn,
                )
            ).stops,
        ),
    )
    gtfs_zip_file = app.stack.enter_context(zipfile.ZipFile(app.settings.gtfs_zip_path))
    gtfs_file = gtfs.GtfsFile(gtfs_zip_file)
    await importer.import_stops(gtfs_file.get_stops())
