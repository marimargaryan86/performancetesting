from __future__ import annotations

import contextlib
import datetime
import functools
import math
import random
from collections.abc import Collection, Iterable

import httpx
from aio_pika import abc
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import cabin_classes, simple_offers
from snowfall.project.junction.service.providers.benerail import (
    adapter,
    cache,
    config,
    criteria,
    train_stations,
)
from snowfall.project.junction.service.providers.benerail.helper_functions import (
    normalize_datetime,
)
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.benerail import client

_Impl = simple_offers.SimpleOfferSearchImplementation[criteria.SearchCriteria,]
_radius_of_earth_in_metres = 6371000


async def simple_search_app(
    app: application.Application[config.Settings],
    amqp_conn: abc.AbstractConnection,
    redis_conn: aioredis.Redis[bytes],
    stack: contextlib.AsyncExitStack,
) -> _Impl:
    stations = await train_stations.load_train_stations()
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    http_client = await stack.enter_async_context(
        httpx.AsyncClient(
            http2=True,
            timeout=app.settings.api_timeout.seconds,
            cert=config.cert_tmp_path(app.settings.cert_base64),
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    benerail_client = client.BenerailClient(
        subscription_key=app.settings.subscription_key,
        base_url=str(app.settings.api_base_url),
        http_client=http_client,
    )

    benerail_adapter = adapter.BenerailOffersAdapter(
        benerail_client=benerail_client,
        train_station_repository=train_stations.TrainStationRepository(
            train_stations=stations,
        ),
        provider_cabin_class_mapping=cabin_classes.CabinMappingRepository(
            mongo.benerail.provider_cabin_mapping,
        ),
        offers_cache=cache.OffersCache(
            client=redis.Client(redis_conn, prefix=app.name),
        ),
        ttl=app.settings.ttl,
    )

    return simple_offers.SimpleOfferSearchImplementation(
        search_criteria_task_generator=CriteriaGenerator(
            h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                mapping=stations,
                resolution=8,
            ),
        ).criteria_task_generator,
        search_criteria_generator=criteria_generator,
        offer_group_cache_key_generator=cache.generate_cache_key,
        offer_group_generator=benerail_adapter.gather_search_results,
    )


def _calculate_distance(
    p1: tuple[float, float],
    p2: train_stations.TrainStation,
) -> float:
    """Return the great circle distance in meters between two points."""
    station = p2.latitude, p2.longitude
    lon1, lat1, lon2, lat2 = map(math.radians, (*p1, *station))

    dlon = math.sin((lon2 - lon1) / 2) ** 2
    dlat = math.sin((lat2 - lat1) / 2) ** 2
    hav = dlat + math.cos(lat1) * math.cos(lat2) * dlon
    distance = 2 * math.asin(math.sqrt(hav))
    return distance * _radius_of_earth_in_metres


def _find_nearest_provider_place(
    stations: Iterable[train_stations.TrainStation],
    coordinates: latlng_pb2.LatLng,
) -> str:
    coords = coordinates.latitude, coordinates.longitude
    return min(
        stations,
        key=functools.partial(_calculate_distance, coords),
    ).identifier


def criteria_generator(
    search: criteria.SearchCriteria,
) -> criteria.SearchCriteria:
    return search


class CriteriaGenerator(object):
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[train_stations.TrainStation],
    ):
        self._mapping = h3_mapping

    def criteria_task_generator(
        self,
        search: offers_pb2.SimpleTripOfferSearch,
    ) -> list[criteria.SearchCriteria]:
        allowed_segment_types = search.allowed_segment_types
        if models_pb2.Schedule.TYPE_RAIL in allowed_segment_types:
            origins = self._mapping.find_mapped_values(
                coordinates=search.origin.coordinates,
                neighbour_search_radius=1,
            )
            destinations = self._mapping.find_mapped_values(
                coordinates=search.destination.coordinates,
                neighbour_search_radius=1,
            )

            if not origins or not destinations:
                return []

            return create_criteria_time_windows(
                frozenset(origins),
                frozenset(destinations),
                search,
            )
        return []


def create_criteria_time_windows(
    origins: Collection[train_stations.TrainStation],
    destinations: Collection[train_stations.TrainStation],
    search: offers_pb2.SimpleTripOfferSearch,
) -> list[criteria.SearchCriteria]:
    timestamps = []
    departure_at = normalize_datetime(
        protobuf.protobuf_to_datetime(search.departure_at),
    ).replace(hour=0)

    if search.HasField("departure_before"):
        departure_before = protobuf.protobuf_to_datetime(search.departure_before)
    else:
        departure_before = departure_at + datetime.timedelta(days=1)

    while departure_at < departure_before:
        timestamps.append(departure_at)
        departure_at += datetime.timedelta(hours=2)

    return [
        criteria.SearchCriteria(
            origin=_find_nearest_provider_place(
                origins,
                search.origin.coordinates,
            ),
            destination=_find_nearest_provider_place(
                destinations,
                search.destination.coordinates,
            ),
            passenger_dobs=[
                protobuf.protobuf_to_date(passenger.date_of_birth)
                for passenger in search.passengers
            ],
            outbound_departure_datetime=timestamp,
            session_token=search.session_token,
        )
        for timestamp in timestamps
    ]
