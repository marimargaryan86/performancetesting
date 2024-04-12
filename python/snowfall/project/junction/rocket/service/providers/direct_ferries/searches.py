import dataclasses
import datetime
import json
from collections.abc import AsyncIterator, Sequence

from google.protobuf import message

from snowfall.project.junction.go.v1 import models_pb2 as legacy_go_pb2
from snowfall.project.junction.go.v1.models_pb2 import Point
from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    cache,
    helper_models,
    route,
)
from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    port as port_functions,
)
from snowfall.project.junction.rocket.service.providers.direct_ferries.constant import (
    PROVIDER_ID,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import datetime_pb2
from snowfall.stdlib.v1.latlng_pb2 import LatLng
from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.models import (
    leg,
    passenger,
    quote,
    request,
    vehicle,
)

_CURRENCY = "EUR"


class SearchError(Exception):
    """Raised when there is an exception in the Direct Ferries quote search."""


@dataclasses.dataclass(frozen=True)
class Criteria(message.Message):
    search_id: str
    origin: Point
    destination: Point
    passenger_dobs: list[datetime.date]
    outbound_departure_datetime: datetime.datetime
    vehicles: list[int]
    inbound_departure_datetime: datetime.datetime | None = None
    outbound_id: str | None = None


def cache_key(search: Criteria) -> str:
    return string.uuid()


class SearchResultGenerator:
    def __init__(
        self,
        df_client: client.DfHttpClient,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ):
        self._client = df_client
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = stdout.get_logger()

    async def generate(
        self,
        search_criteria: Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        quotes = await self._get_quotes(search_criteria)

        expires_at = datetime.datetime.now(tz=datetime.UTC) + self._ttl

        for quote_obj in quotes:
            price = money.from_string(
                str(quote_obj.quote.price.total_in_selected_currency),
                money.Currency(quote_obj.quote.selected_currency),
            ).protobuf()

            result_details = self._build_result_details(
                search_criteria=search_criteria,
                quote_obj=quote_obj,
            )

            yield models_pb2.SearchResult(
                id=string.uuid(),
                search_id=search_criteria.search_id,
                provider_id=str(PROVIDER_ID),
                expires_at=protobuf.datetime_to_protobuf(expires_at),
                offers=[
                    models_pb2.Offer(
                        id=quote_obj.redis_key
                        or await self._offers_cache.store(
                            cache.OfferDetails(
                                quote=quote_obj.quote,
                                round_trip_offer_cache_keys=(
                                    quote_obj.round_trip_offer_cache_keys
                                ),
                            ),
                            expires_at=expires_at,
                        ),
                        price_breakdown=[
                            models_pb2.PriceBreakdown(
                                breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
                                price=price,
                            ),
                        ],
                        price=price,
                        ferry=models_pb2.FerryOffer(
                            ferry_result_detail_id=result_details[-1].id,
                        ),
                    ),
                ],
                result_details=result_details,
            )

    async def _get_quotes(
        self,
        search_criteria: Criteria,
    ) -> list[helper_models.Quote]:
        if search_criteria.outbound_id:
            return await self._gather_return_trip_search_results(
                offer_id=search_criteria.outbound_id,
            )

        quotes_request_generator = QuoteRequestGenerator(search_criteria)

        vendor_quotes = await self._client.quotes.get_quotes(
            request=quotes_request_generator.create_quote_request(),
        )

        quotes = [
            helper_models.Quote(quote=vendor_quote) for vendor_quote in vendor_quotes
        ]

        if search_criteria.inbound_departure_datetime:
            quotes = await self._filter_round_trip_quotes(
                quotes=quotes,
                expires_at=datetime.datetime.now(tz=datetime.UTC) + self._ttl,
            )

        return quotes

    async def _gather_return_trip_search_results(
        self,
        offer_id: str,
    ) -> list[helper_models.Quote]:
        outbound_offer = await self._offers_cache.fetch(offer_id)

        if outbound_offer is None:
            raise SearchError("Outbound offer not found")

        redis_keys = outbound_offer.round_trip_offer_cache_keys
        if not redis_keys:
            raise SearchError("Inbound offer keys not found")

        inbound_offers = await self._offers_cache.mfetch(redis_keys)

        if not inbound_offers:
            raise SearchError("Inbound offers not found")

        quotes = [
            helper_models.Quote(quote=inbound_offer.quote)
            for inbound_offer in inbound_offers
            if inbound_offer is not None
        ]

        for quote_obj, redis_key in zip(quotes, redis_keys, strict=False):
            quote_obj.redis_key = redis_key

        return quotes

    async def _filter_round_trip_quotes(
        self,
        quotes: Sequence[helper_models.Quote],
        expires_at: datetime.datetime,
    ) -> list[helper_models.Quote]:
        filtered_quotes: list[helper_models.Quote] = []

        for quote_obj in quotes:
            round_trip_offer_cache_key = await self._offers_cache.store(
                cache.OfferDetails(
                    quote=quote_obj.quote,
                ),
                expires_at=expires_at,
            )

            append_to_filtered_quotes = True

            for filtered_quote in filtered_quotes:
                filtered_quote_dep_date = filtered_quote.quote.legs[
                    0
                ].departure_date_time
                quote_obj_dep_date = quote_obj.quote.legs[0].departure_date_time
                if filtered_quote_dep_date == quote_obj_dep_date:
                    filtered_quote.round_trip_offer_cache_keys = [
                        *filtered_quote.round_trip_offer_cache_keys,
                        round_trip_offer_cache_key,
                    ]

                    append_to_filtered_quotes = False
                    break

            if append_to_filtered_quotes:
                quote_obj.round_trip_offer_cache_keys = [
                    *quote_obj.round_trip_offer_cache_keys,
                    round_trip_offer_cache_key,
                ]
                filtered_quotes.append(quote_obj)

            quote_obj.quote.legs = [
                leg for leg in quote_obj.quote.legs if not leg.is_return_leg
            ]

        return filtered_quotes

    def _build_result_details(
        self,
        search_criteria: Criteria,
        quote_obj: helper_models.Quote,
    ) -> list[models_pb2.ResultDetail]:
        result_details: list[models_pb2.ResultDetail] = []

        outbound_details = self._create_result_details(
            origin=search_criteria.origin,
            destination=search_criteria.destination,
            legs=[leg for leg in quote_obj.quote.legs if not leg.is_return_leg],
        )

        result_details.append(outbound_details)

        if search_criteria.outbound_id:
            inbound_details = self._create_result_details(
                origin=search_criteria.destination,
                destination=search_criteria.origin,
                legs=[leg for leg in quote_obj.quote.legs if leg.is_return_leg],
            )
            result_details.append(inbound_details)

        return result_details

    def _create_result_details(
        self,
        origin: Point,
        destination: Point,
        legs: Sequence[leg.Leg],
    ) -> models_pb2.ResultDetail:
        first_leg = legs[0]
        last_leg = legs[-1]

        return models_pb2.ResultDetail(
            id=string.uuid(),
            ferry=models_pb2.FerryResultDetail(
                origin=legacy_go_pb2.Point(
                    ref=first_leg.departure_port_code,
                    name=first_leg.departure_port_name,
                    coordinates=origin.coordinates,
                    time_zone=origin.time_zone,
                ),
                destination=legacy_go_pb2.Point(
                    ref=last_leg.arrival_port_code,
                    name=last_leg.arrival_port_name,
                    coordinates=destination.coordinates,
                    time_zone=destination.time_zone,
                ),
                ferry_operator=models_pb2.FerryOperator(
                    id=first_leg.operator.identifier,
                    name=first_leg.operator.name,
                ),
                departure_date=datetime_pb2.DateTime(
                    year=int(first_leg.departure_date_time.year),
                    month=int(first_leg.departure_date_time.month),
                    day=int(first_leg.departure_date_time.day),
                    hours=int(first_leg.departure_date_time.hour),
                    minutes=int(first_leg.departure_date_time.minute),
                    seconds=int(first_leg.departure_date_time.second),
                    nanos=int(first_leg.departure_date_time.microsecond),
                    time_zone=datetime_pb2.TimeZone(id=origin.time_zone),
                ),
                arrival_date=datetime_pb2.DateTime(
                    year=int(last_leg.arrival_date_time.year),
                    month=int(last_leg.arrival_date_time.month),
                    day=int(last_leg.arrival_date_time.day),
                    hours=int(last_leg.arrival_date_time.hour),
                    minutes=int(last_leg.arrival_date_time.minute),
                    seconds=int(last_leg.arrival_date_time.second),
                    nanos=int(last_leg.arrival_date_time.microsecond),
                    time_zone=datetime_pb2.TimeZone(id=destination.time_zone),
                ),
                duration_in_minutes=sum(
                    leg.duration_minutes if leg.duration_minutes is not None else 0
                    for leg in legs
                ),
                outbound_segment=first_leg.is_return_leg is False,
                segment_sequence=2 if first_leg.is_return_leg else 1,
            ),
        )


class QuoteRequestGenerator:
    def __init__(self, search_criteria: Criteria):
        self._search_criteria = search_criteria

    def create_quote_request(self) -> request.QuoteRequest:
        quote_base = quote.QuoteBase(
            selected_currency=_CURRENCY,
            is_different_outbound_return=True,
            return_alternative_routes=False,
            is_open_ticket=False,
            legs=self._assemble_trip_legs(),
        )

        return request.QuoteRequest(quote=quote_base)

    def _assemble_trip_legs(self) -> list[leg.LegBase]:
        routes = route.RouteRepository()
        passengers = self._build_passenger_list_with_ages()
        vehicles = self._find_matching_vehicles()

        legs = [
            leg.LegBase(
                is_return_leg=False,
                route_id=routes.get_by_origin_destination(
                    origin=self._search_criteria.origin.ref,
                    destination=self._search_criteria.destination.ref,
                ).route_id,
                departure_date_time=self._search_criteria.outbound_departure_datetime,
                passengers=passengers,
                vehicles=vehicles,
            ),
        ]

        if self._search_criteria.inbound_departure_datetime:
            legs.append(
                leg.LegBase(
                    is_return_leg=True,
                    route_id=routes.get_by_origin_destination(
                        origin=self._search_criteria.destination.ref,
                        destination=self._search_criteria.origin.ref,
                    ).route_id,
                    departure_date_time=self._search_criteria.inbound_departure_datetime,
                    passengers=passengers,
                    vehicles=vehicles,
                ),
            )

        return legs

    def _build_passenger_list_with_ages(self) -> list[passenger.PassengerBase]:
        return [
            passenger.PassengerBase(
                age_range=passenger.AgeRange.parse_raw(
                    json.dumps(
                        {
                            "from": _calculate_age_at_departure(
                                departure_date=self._search_criteria.outbound_departure_datetime,
                                dob=dob,
                            ),
                            "to": _calculate_age_at_departure(
                                departure_date=self._search_criteria.outbound_departure_datetime,
                                dob=dob,
                            ),
                        },
                    ),
                ),
                is_wheelchair_user=False,
                is_lead_passenger=pax_num == 0,
            )
            for pax_num, dob in enumerate(
                self._search_criteria.passenger_dobs,
            )
        ]

    def _find_matching_vehicles(self) -> list[vehicle.Vehicle]:
        return [
            vehicle.Vehicle(
                type_id=vehicle_type_id,
            )
            for vehicle_type_id in self._search_criteria.vehicles
            if vehicle_type_id
        ]


class CriteriaGenerator:
    def __init__(self) -> None:
        self._ports = port_functions.load_ports()

    def criteria_task_generator(
        self,
        search: models_pb2.Search,
    ) -> list[Criteria]:
        port_functions.load_ports()

        origin = port_functions.get_closest_port(
            search.ferry.origin.coordinates,
            self._ports,
        )

        destination = port_functions.get_closest_port(
            search.ferry.destination.coordinates,
            self._ports,
        )

        return [
            Criteria(
                search_id=search.id,
                origin=Point(
                    ref=origin.identifier,
                    name=origin.name,
                    coordinates=LatLng(
                        latitude=origin.latitude,
                        longitude=origin.longitude,
                    ),
                    time_zone=str(origin.timezone),
                ),
                destination=Point(
                    ref=destination.identifier,
                    name=destination.name,
                    coordinates=LatLng(
                        latitude=destination.latitude,
                        longitude=destination.longitude,
                    ),
                    time_zone=str(destination.timezone),
                ),
                passenger_dobs=[
                    protobuf.protobuf_to_date(pax.date_of_birth)
                    for pax in search.ferry.passengers
                ],
                vehicles=[vehicle.type_id for vehicle in search.ferry.vehicles],
                outbound_departure_datetime=protobuf.protobuf_to_datetime(
                    search.ferry.departure_after,
                )
                .astimezone(origin.timezone)
                .replace(tzinfo=None),
                inbound_departure_datetime=(
                    protobuf.protobuf_to_datetime(
                        search.ferry.return_date,
                    )
                    .astimezone(destination.timezone)
                    .replace(tzinfo=None)
                    if search.ferry.HasField("return_date")
                    else None
                ),
                outbound_id=(
                    search.ferry.outbound_offer_id
                    if search.ferry.outbound_offer_id
                    else None
                ),
            ),
        ]


def _calculate_age_at_departure(
    departure_date: datetime.datetime,
    dob: datetime.date,
) -> int:
    year_diff = departure_date.year - dob.year
    is_before_birthday = (departure_date.month, departure_date.day) < (
        dob.month,
        dob.day,
    )
    return year_diff - int(is_before_birthday)
