import contextlib
import datetime
from collections.abc import AsyncIterator, Iterable, Mapping, Sequence
from typing import ClassVar

import asyncstdlib
import more_itertools
from geopy import distance

from snowfall.project.junction.content.service.benerail import adapter, train_stations
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2, segment_type_pb2
from snowfall.stdlib import h3, money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.http import errors
from snowfall.stdlib.v1 import latlng_pb2, money_pb2
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models import place as models_place
from snowfall.vendor.benerail.models.enumeration import rcode
from snowfall.vendor.benerail.models.trip_offers import (
    link,
    summary,
)
from snowfall.vendor.benerail.models.trip_offers import (
    offer as trip_offers_offer,
)
from snowfall.vendor.benerail.models.trips import trips as models_trips


class RCodeLabelNotFoundError(Exception):
    """Raised when rcode retrieval fails."""


def _price_from_offer_info(
    offer_info: trip_offers_offer.Offer | summary.OfferSummary,
) -> money_pb2.Money:
    if isinstance(offer_info, trip_offers_offer.Offer):
        return money.from_string(
            string_amount=str(offer_info.price.amount),
            currency=money.Currency(
                offer_info.price.currency.upper(),
            ),
        ).protobuf()

    return money.from_string(
        string_amount=str(offer_info.price_with_optional_parts.amount),
        currency=money.Currency(
            offer_info.price_with_optional_parts.currency.upper(),
        ),
    ).protobuf()


class Transformer:
    _cabin_class_to_fare_type: ClassVar[
        dict[
            models_pb2.CabinClass.Type.ValueType,
            fare_type_pb2.FareType.ValueType,
        ]
    ] = {
        models_pb2.CabinClass.Type.TYPE_UNSPECIFIED: fare_type_pb2.FARE_TYPE_UNSPECIFIED,
        models_pb2.CabinClass.Type.TYPE_ECONOMY: fare_type_pb2.FARE_TYPE_ECONOMY,
        models_pb2.CabinClass.Type.TYPE_PREMIUM: fare_type_pb2.FARE_TYPE_FIRST,
        models_pb2.CabinClass.Type.TYPE_BUSINESS: fare_type_pb2.FARE_TYPE_BUSINESS,
        models_pb2.CabinClass.Type.TYPE_FIRST: fare_type_pb2.FARE_TYPE_FIRST,
    }

    def __init__(
        self,
        benerail_client: client.BenerailClient,
        provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
        train_station_repository: train_stations.TrainStationRepository,
    ):
        self._client = benerail_client
        self._cabin_mapping = provider_cabin_class_mapping
        self._train_station_repository = train_station_repository

    async def to_results(
        self,
        results: Sequence[adapter.TripWithOffers] | Sequence[adapter.TripWithTripOffer],
    ) -> Sequence[trips_pb2.Result]:
        trip_results: list[trips_pb2.Result] = []

        if not results:
            return trip_results

        passengers = (
            results[0].trip_offer.passengers
            if isinstance(results[0], adapter.TripWithTripOffer)
            else results[0].offers[0].passengers
        )
        for item in results:
            trip = item.trip

            offer_data_objects = (
                item.offers
                if isinstance(item, adapter.TripWithOffers)
                else item.trip_offer.offers
            )

            for offer_data in offer_data_objects:  # type: ignore[attr-defined]
                offer_info: trip_offers_offer.Offer | summary.OfferSummary = (
                    offer_data
                    if isinstance(offer_data, trip_offers_offer.Offer)
                    else offer_data.summary
                )

                amount = _price_from_offer_info(offer_info)
                trips = [await self._trip_to_proto(trip, offer_info, passengers)]
                trip_results.append(
                    trips_pb2.Result(
                        trips=trips,
                        base_amount=amount,
                        total_amount=amount,
                    ),
                )
        return trip_results

    async def _fare_to_proto(
        self,
        offer_info: trip_offers_offer.Offer | summary.OfferSummary,
    ) -> trips_pb2.Trip.Fare:
        if offer_info.comfort_class and offer_info.comfort_class.comfort_class_value:
            comfort_class_value = str(offer_info.comfort_class.comfort_class_value)
            try:
                comfort_class_name = await self._resolve_rcode_title(
                    comfort_class_value,
                )
            except RCodeLabelNotFoundError:
                comfort_class_name = comfort_class_value
        else:
            comfort_class_value = ""
            comfort_class_name = ""
        cabin_class_type = await self._cabin_mapping.resolve_cabin_class(
            comfort_class_value,
            "benerail",
        )
        return trips_pb2.Trip.Fare(
            type=self._cabin_class_to_fare_type[cabin_class_type],
            marketing_name=comfort_class_name,
        )

    async def _trip_to_proto(
        self,
        trip: models_trips.Trip,
        offer_info: trip_offers_offer.Offer | summary.OfferSummary,
        passengers: Sequence[link.PassengerResourceLink],
    ) -> trips_pb2.Trip:
        fare = await self._fare_to_proto(offer_info)
        segments = await self._segments_to_proto(trip, offer_info, passengers)
        return trips_pb2.Trip(
            segments=segments,
            fare=fare,
        )

    async def _segments_to_proto(
        self,
        trip: models_trips.Trip,
        offer_info: trip_offers_offer.Offer | summary.OfferSummary,
        passengers: Sequence[link.PassengerResourceLink],
    ) -> Sequence[trips_pb2.Segment]:
        timed_legs = [
            leg for leg in trip.trip_legs if isinstance(leg, models_trips.TimedLeg)
        ]
        return [
            await self._segment_to_proto(offer_info, leg, passengers)
            for leg in timed_legs
        ]

    async def _segment_to_proto(
        self,
        offer_info: trip_offers_offer.Offer | summary.OfferSummary,
        leg: models_trips.TimedLeg,
        passengers: Sequence[link.PassengerResourceLink],
    ) -> trips_pb2.Segment:
        fare = await self._fare_to_proto(offer_info)
        departure_at = protobuf.datetime_to_protobuf_datetime(
            datetime.datetime.fromisoformat(leg.departure_at),
        )
        arrival_at = protobuf.datetime_to_protobuf_datetime(
            datetime.datetime.fromisoformat(leg.arrival_at),
        )
        origin = self._place_to_proto(leg.origin)
        destination = self._place_to_proto(leg.destination)
        passenger_protos = [
            trips_pb2.Segment.Passenger(
                seating=trips_pb2.Segment.Passenger.Seating(
                    type=fare.type,
                    marketing_name=fare.marketing_name,
                ),
            )
            for _ in passengers
        ]
        vehicle = await self._vehicle_to_proto(leg)
        return trips_pb2.Segment(
            type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
            origin=origin,
            destination=destination,
            departure_at=departure_at,
            arrival_at=arrival_at,
            vehicle=vehicle,
            passengers=passenger_protos,
            marketed_by=trips_pb2.Segment.Company(),
            operated_by=trips_pb2.Segment.Company(),
        )

    def _place_to_proto(self, item: models_place.Place) -> trips_pb2.Location:
        station = self._train_station_repository.resolve_place_with_urn(
            item.place_value,
        )
        return trips_pb2.Location(
            ref=station.identifier,
            name=station.name or "",
            coordinates=latlng_pb2.LatLng(
                longitude=station.longitude,
                latitude=station.latitude,
            ),
        )

    async def _vehicle_to_proto(
        self,
        leg: models_trips.TimedLeg,
    ) -> trips_pb2.Segment.Vehicle:
        if leg.train_type and leg.train_type.train_type_value:
            train_type = leg.train_type.train_type_value

            try:
                code = await self._resolve_rcode_title(
                    train_type,
                )
            except RCodeLabelNotFoundError:
                code = train_type.rsplit(":", 1)[-1]
        else:
            code = ""

        name = ", ".join(leg.train_numbers) if leg.train_numbers else ""

        return trips_pb2.Segment.Vehicle(
            code=code,
            name=name,
        )

    @classmethod
    def _get_rcode_label(
        cls,
        labels: Mapping[str, rcode.RcoderesultLabels],
    ) -> rcode.RcoderesultLabels:
        try:
            return labels["en"]
        except KeyError:
            return labels["*"]

    @asyncstdlib.lru_cache()
    async def _resolve_rcode_title(self, rcode_value: str) -> str:
        try:
            urn_val = await self._client.rcode_client.get_urn_value(rcode_value)
        except errors.HttpError as http_error_ex:
            raise RCodeLabelNotFoundError from http_error_ex

        label_obj = None

        for rcode_obj in urn_val.response_result.rcodes:
            with contextlib.suppress(KeyError):
                label_obj = self._get_rcode_label(rcode_obj.labels)

            if label_obj:
                break

        if not label_obj:
            raise RCodeLabelNotFoundError

        label = label_obj.code_long or label_obj.code_short

        if not label:
            raise RCodeLabelNotFoundError

        return label


class Trips:
    def __init__(
        self,
        benerail_adapter: adapter.BenerailAdapter,
        station_mapping: h3.H3MappingRepository[train_stations.TrainStation],
        train_station_repository: train_stations.TrainStationRepository,
        transformer: Transformer,
        *,
        should_retrieve_offers: bool,
    ):
        self._adapter = benerail_adapter
        self._mapping = station_mapping
        self._train_station_repository = train_station_repository
        self._transformer = transformer
        self._should_retrieve_offers = should_retrieve_offers

    async def find_one_way(
        self,
        trip_request: trips_pb2.SearchTripsRequest.OneWay,
        passengers: Iterable[trips_pb2.SearchTripsRequest.Passenger],
    ) -> trips_pb2.SearchTripsResponse:
        criterion = trip_request.criterion
        origins = self._mapping.find_mapped_values(
            coordinates=criterion.origin_coordinates,
            neighbour_search_radius=1,
        )
        destinations = self._mapping.find_mapped_values(
            coordinates=criterion.destination_coordinates,
            neighbour_search_radius=1,
        )

        if not all((origins, destinations)):
            return trips_pb2.SearchTripsResponse(results=[])

        origin = _find_nearest_provider_place(
            frozenset(origins),
            criterion.origin_coordinates,
        )
        destination = _find_nearest_provider_place(
            frozenset(destinations),
            criterion.destination_coordinates,
        )
        departure_datetime = datetime.datetime.combine(
            protobuf.protobuf_to_date(
                criterion.departure_date,
            ),
            datetime.time(
                hour=12,  # noqa: WPS432
                tzinfo=more_itertools.first(origins).timezone,
            ),
        )

        if self._should_retrieve_offers:
            trip_with_offer_iterator: AsyncIterator[adapter.TripWithOffers] = (
                self._adapter.search_with_offers(
                    origin=origin,
                    destination=destination,
                    departure_datetime=departure_datetime,
                    passenger_dobs=[
                        protobuf.protobuf_to_date(
                            passenger.date_of_birth,
                        )
                        for passenger in passengers
                    ],
                    session_token=string.uuid(),
                )
            )

            trip_with_offer_objects = [
                result async for result in trip_with_offer_iterator
            ]

            return trips_pb2.SearchTripsResponse(
                results=await self._transformer.to_results(trip_with_offer_objects),
            )

        trip_with_trip_offer_iterator: AsyncIterator[adapter.TripWithTripOffer] = (
            self._adapter.search_with_trip_offers(
                origin=origin,
                destination=destination,
                departure_datetime=departure_datetime,
                passenger_dobs=[
                    protobuf.protobuf_to_date(
                        passenger.date_of_birth,
                    )
                    for passenger in passengers
                ],
                session_token=string.uuid(),
            )
        )

        trip_with_trip_offer_objects = [
            result async for result in trip_with_trip_offer_iterator
        ]

        return trips_pb2.SearchTripsResponse(
            results=await self._transformer.to_results(
                trip_with_trip_offer_objects,
            ),
        )


def _find_nearest_provider_place(
    stations: frozenset[train_stations.TrainStation],
    coordinates: latlng_pb2.LatLng,
) -> str:
    coords = coordinates.latitude, coordinates.longitude
    return min(
        stations,
        key=lambda station: distance.distance(
            coords,
            (station.latitude, station.longitude),
        ),
    ).identifier
