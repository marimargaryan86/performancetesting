import datetime
import zoneinfo
from typing import AsyncIterator, Optional, Sequence

import more_itertools
import structlog

from snowfall.project.junction.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.distribusion import cache
from snowfall.project.junction.service.providers.distribusion.search import validator
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models import connections
from snowfall.vendor.distribusion.models.criterias import FindConnectionsCriteria

_DEFAULT_FARE_CLASS_NAME = "Economy"
_DEFAULT_LOCALE = "en"
_DEFAULT_CURRENCY = "EUR"


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                task.session_token,
                *[segment.id for segment in task.segments],
                *[str(age) for age in task.criteria.passengers_age],
                task.criteria.origin_id,
                task.criteria.destination_id,
            ],
        ),
    )


class MarketingCarrierAdapter(object):
    def __init__(
        self,
        marketing_carrier: connections.MarketingCarrier,
    ) -> None:
        self._marketing_carrier = marketing_carrier
        self._fare_classes: Optional[dict[str, connections.FareClass]] = None

    def get_code(self) -> str:
        return self._marketing_carrier.code or ""

    def get_fare_class(self, fare_class_code: str) -> Optional[connections.FareClass]:
        return self._get_fare_classes().get(fare_class_code)

    def get_fare_class_name(
        self,
        fare: Optional[connections.FaresRelFareClassPrice],
    ) -> str:
        if fare and fare.fare_class and fare.fare_class.code:
            fare_class = self.get_fare_class(fare.fare_class.code)

            if fare_class and fare_class.name:
                return fare_class.name

        return _DEFAULT_FARE_CLASS_NAME

    def _get_fare_classes(self) -> dict[str, connections.FareClass]:
        if self._fare_classes is None:
            self._fare_classes = {
                fare_class.code: fare_class
                for fare_class in self._marketing_carrier.fare_classes or []
                if fare_class.code is not None
            }

        return self._fare_classes


class MarketingCarrierAdapters(object):
    def __init__(self) -> None:
        self._adapters = dict[str, MarketingCarrierAdapter]()

    def get_adapter(
        self,
        marketing_carrier: connections.MarketingCarrier,
    ) -> MarketingCarrierAdapter:
        carrier_code = marketing_carrier.code or ""
        adapter = self._adapters.get(carrier_code)

        if not adapter:
            adapter = MarketingCarrierAdapter(marketing_carrier)
            self._adapters[carrier_code] = adapter

        return adapter


class DistribusionSearchAdapter(object):  # noqa: WPS214
    def __init__(
        self,
        distribusion_client: client.DistribusionClient,
        offers_cache: cache.OffersCache,
        connection_validator: validator.ConnectionValidator,
        ttl: datetime.timedelta,
    ) -> None:
        self._client = distribusion_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._validator = connection_validator
        self._logger = structlog.get_logger(__name__)

    async def gather_search_results(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        criteria = FindConnectionsCriteria(
            locale=search_task.criteria.locale or _DEFAULT_LOCALE,
            departure_stations=[search_task.criteria.origin_id],
            arrival_stations=[search_task.criteria.destination_id],
            departure_date=protobuf.protobuf_to_date(
                search_task.criteria.outbound_departure,
            ),
            return_date=protobuf.protobuf_to_date(
                search_task.criteria.inbound_departure,
            )
            if search_task.criteria.HasField("inbound_departure")
            else None,
            pax=len(search_task.criteria.passengers_age),
            currency=search_task.criteria.currency or _DEFAULT_CURRENCY,
        )
        connection_list = await self._client.find_connections(criteria)
        async for fare_group in self._parse_connections(search_task, connection_list):
            yield fare_group

    async def _parse_connections(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
        connection_list: Sequence[connections.Connection],
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        requirements = validator.requirements_from_segments(search_task.segments)
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl
        carriers = MarketingCarrierAdapters()

        self._logger.info(
            "Connections",
            origin=search_task.criteria.origin_id,
            destination=search_task.criteria.destination_id,
            count=len(connection_list),
        )

        for connection in connection_list:
            self._logger.info(
                "Connection",
                departure_time=connection.departure_time,
                arrival_time=connection.arrival_time,
            )
            if (  # noqa: WPS337
                self._validator.matches(connection, requirements)
                and not connection.booked_out
                and connection.marketing_carrier is not None
            ):
                offer_group = await self._parse_connection(
                    connection,
                    search_task.segments,
                    carriers.get_adapter(connection.marketing_carrier),
                    expires_at,
                )

                yield offer_group

    async def _parse_connection(
        self,
        connection: connections.Connection,
        search_segments: Sequence[models_pb2.Segment],
        carrier: MarketingCarrierAdapter,
        expires_at: datetime.datetime,
    ) -> offer_models_pb2.OfferGroup:
        offers = list[offer_models_pb2.Offer]()
        segments = self._parse_segments(connection, search_segments, carrier)

        for fare in connection.fares or []:
            if not fare.price:
                continue

            offer_segment_details = [
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=segment.id,
                )
                for segment in segments
            ]

            offers.append(
                offer_models_pb2.Offer(
                    id=await self._offers_cache.store(
                        cache.OfferDetails(
                            fare_class=fare.fare_class.code
                            if fare.fare_class and fare.fare_class.code
                            else "",
                        ),
                    ),
                    price=money.Money(
                        amount=fare.price,
                        currency=money.Currency(connection.currency),
                    ).protobuf(),
                    brand_name=carrier.get_fare_class_name(fare),
                    segment_details=offer_segment_details,
                ),
            )

        return offer_models_pb2.OfferGroup(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offers=offers,
            segments=segments,
        )

    def _parse_segments(
        self,
        connection: connections.Connection,
        search_segments: Sequence[models_pb2.Segment],
        carrier: MarketingCarrierAdapter,
    ) -> Sequence[offer_models_pb2.OfferSegment]:
        segments = list[offer_models_pb2.OfferSegment]()

        for offer_segment, search_segment in zip(connection.segments, search_segments):
            leg = self._parse_leg(
                offer_segment,
                more_itertools.first(search_segment.legs),
            )
            operator = (
                offer_segment.operating_carrier.code
                if offer_segment.operating_carrier
                else None
            )
            segments.append(
                offer_models_pb2.OfferSegment(
                    id=string.uuid(),
                    segment_id=search_segment.id,
                    legs=[leg],
                    vehicle=self._parse_vehicle(offer_segment),
                    operator=operator or carrier.get_code(),
                    vendor=carrier.get_code(),
                    type=models_pb2.Schedule.TYPE_BUS,
                ),
            )
        return segments

    def _parse_vehicle(
        self,
        offer_segment: connections.Segment,
    ) -> Optional[offer_models_pb2.Vehicle]:
        if not offer_segment.vehicle:
            return None

        if not offer_segment.vehicle.vehicle_type:
            return None

        if not offer_segment.vehicle.vehicle_type.code:
            return None

        return offer_models_pb2.Vehicle(
            equipment=offer_segment.vehicle.vehicle_type.code,
        )

    def _parse_leg(
        self,
        offer_segment: connections.Segment,
        search_leg: models_pb2.Leg,
    ) -> offer_models_pb2.OfferSegmentLeg:
        origin = offer_segment.departure_station
        destination = offer_segment.arrival_station
        departure_time = offer_segment.departure_time or ""
        arrival_time = offer_segment.arrival_time or ""

        return offer_models_pb2.OfferSegmentLeg(
            id=search_leg.id,
            origin=self._parse_point(origin, search_leg.origin),
            destination=self._parse_point(destination, search_leg.destination),
            departure_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(departure_time).replace(
                    tzinfo=zoneinfo.ZoneInfo(
                        origin.time_zone
                        if origin and origin.time_zone
                        else search_leg.origin.time_zone,
                    ),
                ),
            ),
            arrival_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(arrival_time).replace(
                    tzinfo=zoneinfo.ZoneInfo(
                        destination.time_zone
                        if destination and destination.time_zone
                        else search_leg.destination.time_zone,
                    ),
                ),
            ),
        )

    def _parse_point(
        self,
        station: connections.Station,
        search_point: models_pb2.Point,
    ) -> models_pb2.Point:
        return models_pb2.Point(
            ref=station.code,
            name=station.name or "",
            coordinates=models_pb2.Coordinates(
                latitude=station.latitude or search_point.coordinates.latitude,
                longitude=station.longitude or search_point.coordinates.longitude,
            ),
            time_zone=station.time_zone or search_point.time_zone,
        )
