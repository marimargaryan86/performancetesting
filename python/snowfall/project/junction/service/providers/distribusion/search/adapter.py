import datetime
import zoneinfo
from typing import AsyncIterator, Collection, Sequence

import structlog

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.distribusion import cache
from snowfall.project.junction.service.providers.distribusion.search import amenities
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
_FARE_RULE_CODES = (
    "BLUG",  # Bulky luggage
    "AAFR",  # Accessible area for bicycles
    "REFU",  # Fully refundable
    "PALL",  # Pet allowance
    "NREF",  # Non-refundable
    "NAME",  # Non-amendable
    "AMEN",  # Amendable
    "PREF",  # Partially refundable
    "STVA",  # Ticket Validity OW
    "RTVA",  # Ticket Validity RT
    "CBYE",  # Child below 15 years travels for free
)


def offer_group_cache_key(task: amqp_pb2.SearchCriteriaTask) -> str:
    return string.to_uuid(
        b"\x00".decode().join(
            [
                *[segment.id for segment in task.segments],
                *[str(age) for age in task.criteria.passengers_age],
                *task.criteria.origin_ids,
                *task.criteria.destination_ids,
            ],
        ),
    )


class MarketingCarrierAdapter(object):  # noqa: WPS214
    def __init__(
        self,
        marketing_carrier: connections.MarketingCarrier,
    ) -> None:
        self._marketing_carrier = marketing_carrier
        self._fare_classes: dict[str, connections.FareClass] | None = None
        self._passenger_types: list[cache.PassengerType] | None = None

    def get_code(self) -> str:
        return self._marketing_carrier.code or ""

    def get_fare_class(self, fare_class_code: str) -> connections.FareClass | None:
        return self._get_fare_classes().get(fare_class_code)

    def get_fare_feature_codes(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> set[str] | None:
        fare_features = self._get_fare_features(fare)

        if fare_features:
            return {feature.code for feature in fare_features if feature.code}

        return None

    def get_fare_class_name(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> str:
        if fare and fare.fare_class and fare.fare_class.code:
            fare_class = self.get_fare_class(fare.fare_class.code)

            if fare_class and fare_class.name:
                return fare_class.name

        return _DEFAULT_FARE_CLASS_NAME

    def passenger_types(self) -> list[cache.PassengerType]:
        if self._passenger_types:
            return self._passenger_types

        self._passenger_types = []

        for pax_type in self._marketing_carrier.passenger_types or []:
            if pax_type.code and pax_type.min_age >= 0 and pax_type.max_age:
                self._passenger_types.append(
                    cache.PassengerType(
                        type_name=pax_type.name,
                        type_code=pax_type.code,
                        min_age=pax_type.min_age,
                        max_age=pax_type.max_age,
                    ),
                )

        return self._passenger_types

    def is_fully_refundable(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> bool:
        return self.has_any_fare_feature(fare, ["REFU", "PREF"])

    def is_non_refundable(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> bool:
        return self.has_any_fare_feature(fare, ["NREF"])

    def is_changeable(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> bool:
        return self.has_any_fare_feature(fare, ["AMEN"])

    def has_exchange_conditions(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> bool:
        return self._has_any_fare_description(fare, ["AMEN"])

    def has_any_fare_feature(
        self,
        fare: connections.FaresRelFareClassPrice | None,
        codes: Collection[str],
    ) -> bool:
        fare_codes = self.get_fare_feature_codes(fare)
        return fare_codes is not None and bool(fare_codes.intersection(codes))

    def get_fare_rules(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> list[cache.FareRule] | None:
        fare_features = self._get_fare_features(fare)

        if fare_features:
            return [
                cache.FareRule(name=feature.name, description=feature.description)
                for feature in fare_features
                if feature.code
                and feature.code in _FARE_RULE_CODES
                and feature.name
                and feature.description
            ]

        return None

    def _has_any_fare_description(
        self,
        fare: connections.FaresRelFareClassPrice | None,
        codes: Collection[str],
    ) -> bool:
        fare_features = self._get_fare_features(fare)

        if fare_features and codes:
            for feature in fare_features:
                if feature.code and feature.code in codes and feature.description:
                    return True

        return False

    def _get_fare_features(
        self,
        fare: connections.FaresRelFareClassPrice | None,
    ) -> Sequence[connections.FareFeature] | None:
        if fare and fare.fare_class and fare.fare_class.code:
            fare_class = self.get_fare_class(fare.fare_class.code)
            return fare_class.fare_features if fare_class else None

        return None

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
        ttl: datetime.timedelta,
    ) -> None:
        self._client = distribusion_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = structlog.get_logger(__name__)

    def search_criteria_generator(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> FindConnectionsCriteria:
        return FindConnectionsCriteria(
            locale=search_task.criteria.locale or _DEFAULT_LOCALE,
            departure_stations=list(search_task.criteria.origin_ids),
            arrival_stations=list(search_task.criteria.destination_ids),
            departure_date=protobuf.protobuf_to_date(
                search_task.criteria.outbound_departure,
            ),
            return_date=(
                protobuf.protobuf_to_date(
                    search_task.criteria.inbound_departure,
                )
                if search_task.criteria.HasField("inbound_departure")
                else None
            ),
            pax_ages=list(search_task.criteria.passengers_age),
            pax=len(search_task.criteria.passengers_age),
            currency=search_task.criteria.currency or _DEFAULT_CURRENCY,
        )

    def generate_cache_key(self, search_criteria: FindConnectionsCriteria) -> str:
        return string.to_uuid(
            b"\x00".decode().join(
                [
                    str(search_criteria.pax),
                    str(search_criteria.currency),
                    str(search_criteria.locale),
                    *search_criteria.departure_stations,
                    *search_criteria.arrival_stations,
                    str(search_criteria.departure_date),
                    str(search_criteria.return_date),
                ],
            ),
        )

    async def gather_search_results(
        self,
        search_criteria: FindConnectionsCriteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        connection_list = await self._client.find_connections(search_criteria)
        fare_groups = self._parse_connections(
            search_criteria,
            connection_list,
        )
        async for fare_group in fare_groups:
            yield fare_group

    async def _parse_connections(
        self,
        search_criteria: FindConnectionsCriteria,
        connection_list: Sequence[connections.Connection],
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl
        carriers = MarketingCarrierAdapters()

        self._logger.info(
            "Connections",
            origins=search_criteria.departure_stations,
            destinations=search_criteria.arrival_stations,
            count=len(connection_list),
        )

        for connection in connection_list:
            self._logger.info(
                "Connection",
                departure_time=connection.departure_time,
                arrival_time=connection.arrival_time,
            )
            if not connection.booked_out and connection.marketing_carrier is not None:
                offer_group = await self._parse_connection(
                    search_criteria,
                    connection,
                    carriers.get_adapter(connection.marketing_carrier),
                    expires_at,
                )

                yield offer_group

    async def _parse_connection(
        self,
        search_criteria: FindConnectionsCriteria,
        connection: connections.Connection,
        carrier: MarketingCarrierAdapter,
        expires_at: datetime.datetime,
    ) -> offer_models_pb2.OfferGroup:
        offers = list[offer_models_pb2.Offer]()
        segments = self._parse_segments(connection, carrier)
        passenger_types = carrier.passenger_types()

        for fare in connection.fares or []:
            if not fare.price:
                continue

            offer_segment_details = [
                offer_models_pb2.OfferSegmentDetails(
                    id=string.uuid(),
                    offer_segment_id=segment.id,
                    amenities=self._parse_amenities(carrier, fare),
                )
                for segment in segments
            ]

            offers.append(
                offer_models_pb2.Offer(
                    id=await self._offers_cache.store(
                        cache.OfferDetails(
                            expires_at=expires_at,
                            departure_station=connection.departure_station.code,
                            arrival_station=connection.arrival_station.code,
                            departure_time=datetime.datetime.fromisoformat(
                                connection.departure_time,
                            ),
                            arrival_time=datetime.datetime.fromisoformat(
                                connection.arrival_time,
                            ),
                            marketing_carrier=carrier.get_code(),
                            passengers_age=search_criteria.pax_ages,
                            price=fare.price,
                            currency=connection.currency,
                            fare_class=(
                                fare.fare_class.code
                                if fare.fare_class and fare.fare_class.code
                                else ""
                            ),
                            passenger_types=passenger_types,
                            fully_refundable=carrier.is_fully_refundable(fare),
                            non_refundable=carrier.is_non_refundable(fare),
                            changeable=carrier.is_changeable(fare),
                            has_exchange_conditions=carrier.has_exchange_conditions(
                                fare,
                            ),
                            fare_rules=carrier.get_fare_rules(fare),
                        ),
                        expires_at=expires_at,
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
        carrier: MarketingCarrierAdapter,
    ) -> Sequence[offer_models_pb2.OfferSegment]:
        segments = list[offer_models_pb2.OfferSegment]()

        for offer_segment in connection.segments:
            leg = self._parse_leg(
                offer_segment,
            )
            operator = (
                offer_segment.operating_carrier.code
                if offer_segment.operating_carrier
                else None
            )
            segments.append(
                offer_models_pb2.OfferSegment(
                    id=string.uuid(),
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
    ) -> offer_models_pb2.Vehicle | None:
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
    ) -> offer_models_pb2.OfferSegmentLeg:
        origin = offer_segment.departure_station
        destination = offer_segment.arrival_station
        departure_time = offer_segment.departure_time or ""
        arrival_time = offer_segment.arrival_time or ""

        return offer_models_pb2.OfferSegmentLeg(
            id=string.uuid(),
            origin=self._parse_point(origin),
            destination=self._parse_point(destination),
            departure_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(departure_time).replace(
                    tzinfo=zoneinfo.ZoneInfo(origin.time_zone),
                ),
            ),
            arrival_at=protobuf.datetime_to_protobuf(
                datetime.datetime.fromisoformat(arrival_time).replace(
                    tzinfo=zoneinfo.ZoneInfo(destination.time_zone),
                ),
            ),
        )

    def _parse_point(
        self,
        station: connections.Station,
    ) -> models_pb2.Point:
        return models_pb2.Point(
            ref=station.code,
            name=station.name or "",
            coordinates=models_pb2.Coordinates(
                latitude=station.latitude,
                longitude=station.longitude,
            ),
            time_zone=station.time_zone,
        )

    def _parse_amenities(
        self,
        carrier: MarketingCarrierAdapter,
        fare: connections.FaresRelFareClassPrice,
    ) -> offer_models_pb2.SegmentAmenities | None:
        fare_feature_codes = carrier.get_fare_feature_codes(fare)

        if fare_feature_codes:
            return amenities.parse_amenities(fare_feature_codes)

        return None
