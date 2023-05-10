import datetime
import json
from typing import AsyncIterator

import structlog

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.direct_ferries import cache, port
from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import latlng_pb2, models_pb2
from snowfall.vendor.direct_ferries import client, errors
from snowfall.vendor.direct_ferries.models import leg, passenger, quote, request

_CURRENCY = "EUR"


class DFAdapterError(Exception):
    """Raised when there is an exception in the Direct Ferries adapter."""


class BookingError(DFAdapterError):
    """Raised when a booking error is encountered."""


class PassengerCountNotMatchingError(Exception):
    """Raised when the number of passengers changed during the booking."""


class DfAdapter(object):
    def __init__(
        self,
        df_client: client.DfHttpClient,
        ports: port.PortRepository,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ) -> None:
        self._client = df_client
        self._ports = ports
        self._offers_cache = offers_cache
        self._ttl = ttl
        self._logger = structlog.get_logger(__name__)

    def search_criteria_generator(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> request.QuoteRequest:
        passengers = [
            passenger.PassengerBase(
                age_range=passenger.AgeRange.parse_raw(
                    json.dumps(
                        {
                            "from": pax_age,
                            "to": pax_age,
                        },
                    ),
                ),
                is_wheelchair_user=False,
                is_lead_passenger=pax_num == 0,
            )
            for pax_num, pax_age in enumerate(
                search_task.criteria.passengers_ages,
            )
        ]

        legs: list[leg.LegBase] = [
            leg.LegBase(
                is_return_leg=False,
                route_id=search_task.criteria.outbound_route_id,
                departure_date_time=protobuf.protobuf_to_datetime(
                    search_task.criteria.outbound_departure_datetime,
                )
                .astimezone(datetime.timezone.utc)  # noqa: WPS348
                .replace(tzinfo=None),  # noqa: WPS348
                passengers=passengers,
            ),
        ]

        if search_task.criteria.HasField("inbound_departure_datetime"):
            legs.append(
                leg.LegBase(
                    is_return_leg=True,
                    route_id=search_task.criteria.inbound_route_id,
                    departure_date_time=protobuf.protobuf_to_datetime(
                        search_task.criteria.inbound_departure_datetime,
                    )
                    .astimezone(datetime.timezone.utc)  # noqa: WPS348
                    .replace(tzinfo=None),  # noqa: WPS348
                    passengers=passengers,
                ),
            )

        quote_base = quote.QuoteBase(
            selected_currency=_CURRENCY,
            is_different_outbound_return=True,
            return_alternative_routes=False,
            is_open_ticket=False,
            legs=legs,
        )

        return request.QuoteRequest(quote=quote_base)

    def generate_cache_key(self, search_criteria: request.QuoteRequest) -> str:
        return string.to_uuid(
            b"\x00".decode().join(
                [
                    str(search_criteria.quote.partner_code),
                    str(search_criteria.quote.is_different_outbound_return),
                    str(search_criteria.quote.return_alternative_routes),
                    str(search_criteria.quote.is_open_ticket),
                    *[
                        "{is_return_leg}-{route_id}-{departure_date_time}".format(
                            is_return_leg=leg.is_return_leg,
                            route_id=str(leg.route_id),
                            departure_date_time=str(leg.departure_date_time),
                        )
                        for leg in search_criteria.quote.legs
                    ],
                    *[
                        "{age_to}-{age_from}".format(
                            age_to=passenger.age_range.age_to,
                            age_from=passenger.age_range.age_from,
                        )
                        for leg in search_criteria.quote.legs
                        for passenger in leg.passengers
                    ],
                ],
            ),
        )

    async def gather_search_results(  # noqa: WPS210
        self,
        search_criteria: request.QuoteRequest,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        try:
            quotes = await self._client.quotes.get_quotes(
                request=search_criteria,
            )
        except errors.DFError:
            self._logger.exception("Failed to get quotes")

            return

        expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl

        for quote_obj in quotes:
            currency = money.Currency(quote_obj.selected_currency)

            segments: list[offer_models_pb2.OfferSegment] = []

            for leg_obj in quote_obj.legs:
                origin = self._ports.get_by_id(leg_obj.departure_port_code)
                destination = self._ports.get_by_id(leg_obj.arrival_port_code)

                segments.append(
                    offer_models_pb2.OfferSegment(
                        id=string.uuid(),
                        vendor=leg_obj.operator.name if leg_obj.operator else "",
                        type=models_pb2.Schedule.TYPE_FERRY,
                        legs=[
                            offer_models_pb2.OfferSegmentLeg(
                                id=string.uuid(),
                                origin=models_pb2.Point(
                                    ref=origin.identifier,
                                    name=str(origin.name or origin.identifier),
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=origin.latitude,
                                        longitude=origin.longitude,
                                    ),
                                    time_zone=origin.timezone.key,
                                ),
                                destination=models_pb2.Point(
                                    ref=destination.identifier,
                                    name=str(
                                        destination.name or destination.identifier,
                                    ),
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=destination.latitude,
                                        longitude=destination.longitude,
                                    ),
                                    time_zone=destination.timezone.key,
                                ),
                                departure_at=protobuf.datetime_to_protobuf(
                                    leg_obj.departure_date_time.replace(
                                        tzinfo=origin.timezone,
                                    ),
                                ),
                                arrival_at=protobuf.datetime_to_protobuf(
                                    leg_obj.arrival_date_time.replace(
                                        tzinfo=destination.timezone,
                                    ),
                                ),
                            ),
                        ],
                    ),
                )

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(expires_at),
                offers=[
                    offer_models_pb2.Offer(
                        id=await self._offers_cache.store(
                            cache.OfferDetails(
                                quote=quote_obj,
                            ),
                            expires_at=expires_at,
                        ),
                        segment_details=[
                            offer_models_pb2.OfferSegmentDetails(
                                id=string.uuid(),
                                offer_segment_id=segment.id,
                                cabin_class=models_pb2.CabinClass(
                                    type=models_pb2.CabinClass.TYPE_ECONOMY,
                                    marketing_name="Economy",
                                ),
                            )
                            for segment in segments
                        ],
                        price=money.from_string(
                            str(quote_obj.price.total_in_selected_currency),
                            currency,
                        ).protobuf(),
                    ),
                ],
                segments=segments,
            )
