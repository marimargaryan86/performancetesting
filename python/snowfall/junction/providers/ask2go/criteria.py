import datetime
import itertools
import types
from collections.abc import Iterator
from typing import Sequence

import more_itertools

from snowfall.common.v1alpha import models_pb2 as common_models_pb2
from snowfall.junction.offers.v1alpha import amqp_pb2
from snowfall.junction.providers.ask2go import airports, h3, passengers
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2 as provider_amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import enums

_CABIN_CLASS_MAPPING = types.MappingProxyType(
    {
        common_models_pb2.CabinClass.TYPE_UNSPECIFIED: enums.AirCabinClassType.any_,
        common_models_pb2.CabinClass.TYPE_ECONOMY: enums.AirCabinClassType.economy,
        common_models_pb2.CabinClass.TYPE_PREMIUM: enums.AirCabinClassType.premium_economy,
        common_models_pb2.CabinClass.TYPE_BUSINESS: enums.AirCabinClassType.business,
        common_models_pb2.CabinClass.TYPE_FIRST: enums.AirCabinClassType.first,
    },
)


class CriteriaGenerator(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[airports.Airport]):
        self._mapping = h3_mapping

    def from_search_task(
        self,
        search_task: amqp_pb2.TripOfferSearchTask,
    ) -> Iterator[provider_amqp_pb2.SearchCriteriaTask]:
        passenger_types = passengers.get_num_of_passenger_types(
            passengers=search_task.search.passengers,
            date=_get_last_travel_date(search_task),
        )
        cabin_classes = get_cabin_classes(search_task.search.cabin_classes)

        for segment in search_task.search.segments:
            yield from self._from_segment(
                segment=segment,
                offer_search_id=search_task.offer_search_id,
                passenger_types=passenger_types,
                cabin_classes=cabin_classes,
            )

    def _from_segment(
        self,
        segment: common_models_pb2.Segment,
        offer_search_id: str,
        passenger_types: passengers.PassengerTypes,
        cabin_classes: Sequence[enums.AirCabinClassType],
    ) -> Iterator[provider_amqp_pb2.SearchCriteriaTask]:
        first_leg = more_itertools.first(segment.legs)

        if first_leg.type != common_models_pb2.Schedule.TYPE_AIR:
            return

        origins = self._mapping.find_mapped_values(
            coordinates=first_leg.origin.coordinates,
            neighbour_search_radius=1,
        )
        destinations = self._mapping.find_mapped_values(
            coordinates=more_itertools.last(segment.legs).destination.coordinates,
            neighbour_search_radius=1,
        )

        yield from (
            provider_amqp_pb2.SearchCriteriaTask(
                offer_search_id=offer_search_id,
                segments=[segment],
                criteria=provider_amqp_pb2.Criteria(
                    origin_iata=pair[0].iata,
                    destination_iata=pair[1].iata,
                    outbound=protobuf.datetime_to_protobuf_datetime(
                        protobuf.protobuf_to_datetime(
                            first_leg.departure_at,
                        ).astimezone(pair[0].timezone),
                    ),
                    cabin_class=cabin_class.value,
                    adults=passenger_types.adults,
                    children=passenger_types.children,
                    infants=passenger_types.infants,
                ),
            )
            for pair in itertools.product(origins, destinations)
            for cabin_class in cabin_classes
        )


def _get_last_travel_date(
    search_task: amqp_pb2.TripOfferSearchTask,
) -> datetime.date:
    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in search_task.search.segments
    )


def get_cabin_classes(
    cabin_classes: Sequence[common_models_pb2.CabinClass.Type.ValueType],
) -> list[enums.AirCabinClassType]:
    if not cabin_classes:
        return [enums.AirCabinClassType.any_]

    return [_CABIN_CLASS_MAPPING[cabin_class] for cabin_class in cabin_classes]
