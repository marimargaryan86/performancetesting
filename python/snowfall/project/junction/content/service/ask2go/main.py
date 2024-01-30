import random
import uuid
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.content.service.ask2go import trips
from snowfall.project.junction.provider import airports, cabin_classes
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory, httpx_factory
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.adapter import Adapter
from snowfall.vendor.rate_limiter import client as rate_limiter
from snowfall.vendor.rate_limiter import config, gubernator_pb2_grpc

_PROVIDER_ID = uuid.UUID("f10132d5-9e58-4f35-8593-c0e259429f94")
_PROVIDER_NAME = "Ask2Go"


class _Settings(bootstrap.Settings):
    api_base_url: pydantic.AnyUrl
    api_booking_base_url: pydantic.AnyUrl
    http_timeout: int = 30
    mongo_dsn: Sequence[pydantic.AnyUrl]
    rate_limiter_grpc_host: str
    rate_limiter_service_configs: dict[str, config.RateLimitConfig]
    poll_retries_limit: int = 10
    wait_time_between_polling: float = 1


async def _factory(
    app: application.Application[_Settings],
) -> bootstrap.ProviderConfiguration:
    httpx_client = await httpx_factory.make_client(app)
    rate_limit_client = rate_limiter.Client(
        gubernator_pb2_grpc.V1Stub(
            await grpc_factory.make_insecure_channel(
                app,
                app.settings.rate_limiter_grpc_host,
            ),
        ),
        app.settings.rate_limiter_service_configs["ask2go"],
    )

    search_client = client.Ask2GoClient(
        http_client=httpx_client,
        api_base_url=str(app.settings.api_base_url),
        api_booking_base_url=str(app.settings.api_booking_base_url),
        rate_limit_client=rate_limit_client,
    )

    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    airport_repo = airports.AirportRepository(
        filesystem.PkgLoader("snowfall.data").load("airports.json"),
    )
    cabin_mapping_repo = cabin_classes.CabinMappingRepository(
        mongo.ask2go.provider_cabin_mapping,
    )
    trip_searcher = trips.Trips(
        adapter=Adapter(
            ask2go_client=search_client,
            poll_retries_limit=app.settings.poll_retries_limit,
            wait_time_between_polling=app.settings.wait_time_between_polling,
        ),
        transformer=trips.Transformer(airport_repo, cabin_mapping_repo),
    )

    return bootstrap.ProviderConfiguration(
        provider_id=_PROVIDER_ID,
        provider_name=_PROVIDER_NAME,
        trip_search_implementation=bootstrap.TripSearchImplementation(
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            one_way=trip_searcher.find_one_way,
        ),
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="ask2go",
        implementation_factory=_factory,
        settings_class=_Settings,
    )
    entrypoint.enter()
