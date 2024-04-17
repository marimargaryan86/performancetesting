import pathlib
import random

from motor import motor_asyncio

from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.content.service.benerail import (
    adapter,
    config,
    train_stations,
    trips,
)
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging
from snowfall.stdlib.service import httpx_factory
from snowfall.vendor.benerail import client


async def _factory(
    app: bootstrap.Application[config.Settings],
) -> bootstrap.ProviderConfiguration:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    http_client = await httpx_factory.make_client(
        app=app,
        timeout=app.settings.api_timeout,
        cert=httpx_factory.Certificate(
            certificate_file=pathlib.Path(app.settings.cert_path),
        ),
    )
    logging.register(http_client)
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )
    stations = train_stations.load_train_stations()
    h3_mapping = h3.H3MappingRepository[train_stations.TrainStation](
        mapping=stations,
        resolution=8,
    )
    train_station_repo = train_stations.TrainStationRepository(
        stations=stations,
    )
    benerail_adapter = adapter.BenerailAdapter(
        benerail_client=benerail_client,
    )
    transformer = trips.Transformer(
        benerail_client=benerail_client,
        provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
            mongo.benerail.provider_cabin_mapping,
        ),
        train_station_repository=train_station_repo,
    )
    trip_searcher = trips.Trips(
        benerail_adapter=benerail_adapter,
        station_mapping=h3_mapping,
        train_station_repository=train_station_repo,
        transformer=transformer,
        should_retrieve_offers=app.settings.should_retrieve_offers,
    )

    return bootstrap.ProviderConfiguration(
        provider_id=config.PROVIDER_ID,
        provider_name=config.PROVIDER_NAME,
        trip_search_implementation=bootstrap.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_COORDINATES,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_TRAIN],
            one_way=trip_searcher.find_one_way,
        ),
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="junction-content-benerail",
        implementation_factory=_factory,
        settings_class=config.Settings,
    )
    entrypoint.enter()
