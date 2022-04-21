import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.junction.passenger_name_records import passenger_name_records
from snowfall.junction.passenger_name_records.grpc import PassengerNameRecordService
from snowfall.stdlib import service
from snowfall.stdlib.transport import grpc


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50059
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    grpc_server = grpc.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PassengerNameRecordService(
                passenger_name_records=passenger_name_records.PassengerNameRecordRepository(
                    mongo.passenger_name_records.passenger_name_record,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as server:
        await server.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="passenger_name_records")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
