import datetime
import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.junction.offers import offers
from snowfall.junction.offers.amqp import OfferSearchProducer
from snowfall.junction.offers.grpc import OfferSearchService, OfferService
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp, grpc


class _GrpcSettings(pydantic.BaseSettings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    async with amqp.Connection(random.choice(settings.amqp_dsn)) as connection:  # nosec
        server = grpc.create_server(
            settings.grpc_address,
            settings.grpc_port,
            [
                OfferSearchService(
                    offers_searches=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        settings.default_ttl,
                    ),
                    publisher=OfferSearchProducer(
                        producer=await amqp.create_producer(
                            conn=connection,
                            exchange_name="offers",
                        ),
                    ),
                    default_page_size=settings.default_page_size,
                ),
                OfferService(default_page_size=settings.default_page_size),
            ],
        )

        await server.start()
        service.add_cleanup_task(server.stop(5))
        await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="offers",
        tasks=(Task(command="grpc", method=_serve),),
        # todo: add import task
    )

    _service.run()
