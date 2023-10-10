import aiofiles
import orjson
import pydantic

from snowfall.project.junction.service.routes import nodes, repositories
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory, mongo_factory


class ImportSettings(application.Settings):
    geodata_address: str
    mongo_dsn: pydantic.MongoDsn


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
