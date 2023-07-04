import dataclasses
import datetime
from collections import defaultdict
from collections.abc import AsyncIterator, Callable, Mapping, Sequence
from typing import Any

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.service.providers.duffel import cache
from snowfall.project.junction.service.providers.duffel.client_factory import (
    DuffelClientFactory,
)
from snowfall.project.junction.service.providers.duffel.search.parser import (
    OfferParser,
    dict_to_private_fares,
)
from snowfall.project.junction.service.providers.duffel.search.validator import (
    AirlineValidator,
    Validators,
)
from snowfall.project.junction.service.providers.duffel.v1 import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.vendor.duffel.builders.offer_request import (
    OfferRequestData,
    OfferRequestPassenger,
    OfferRequestSlice,
    OffersRequestBuilder,
)
from snowfall.vendor.duffel.models.offer import Offer, PrivateFare
from snowfall.vendor.duffel.models.offer_slice import OfferSliceSegment


def _fares_sort_key(
    elem: PrivateFare,
) -> tuple[str, str]:
    return elem.corporate_code or "", elem.tracking_reference or ""


def _generate_private_fares_keys(  # noqa: WPS210
    private_fares: Mapping[str, Sequence[PrivateFare]],
) -> Sequence[str]:
    private_fare_keys = []

    for name, fares in sorted(private_fares.items()):
        fare_keys = []
        for fare in sorted(fares, key=_fares_sort_key):
            fare_keys.append(
                b"\x00".decode().join(
                    [
                        "{0}-{1}".format(key, fare_value)
                        for key, fare_value in fare.dict().items()
                    ],
                ),
            )
        private_fare_keys.append(
            "{0}-{1}".format(name, b"\x00".decode().join(fare_keys)),
        )
    return private_fare_keys


class OfferGrouper(object):
    @classmethod
    def group_offers(
        cls,
        offers: Sequence[Offer],
        validator: Callable[[Offer], bool],
    ) -> Mapping[str, list[Offer]]:
        offer_groups = defaultdict[str, list[Offer]](list)

        for offer in offers or []:
            if validator(offer):
                offer_groups[cls._offer_key(offer)].append(offer)

        return offer_groups

    @classmethod
    def _segment_key(cls, segment: OfferSliceSegment) -> str:
        return "".join(
            [
                segment.arriving_at.isoformat(),
                segment.departing_at.isoformat(),
                segment.origin.iata_code or "",
                segment.destination.iata_code or "",
                segment.marketing_carrier.iata_code or "",
                segment.operating_carrier.iata_code or "",
                segment.marketing_carrier_flight_number,
            ],
        )

    @classmethod
    def _offer_key(cls, offer: Offer) -> str:
        return "|".join(
            cls._segment_key(segment)
            for offer_slice in offer.slices
            for segment in offer_slice.segments
        )


@dataclasses.dataclass(frozen=True)
class SearchCriteriaWrapper(object):
    search_criteria: OfferRequestData
    reseller_id: str


class DuffelSearchAdapter(object):
    def __init__(  # noqa: WPS211
        self,
        resellers_map: Mapping[str, Mapping[str, Any]],
        duffel_client_factory: DuffelClientFactory,
        offers_cache: cache.OfferCache,
        ttl: datetime.timedelta,
        enabled_airlines: frozenset[str] | None = None,
        disabled_airlines: frozenset[str] | None = None,
    ) -> None:
        self._offers_client_factory = duffel_client_factory
        self._offer_parser = OfferParser(default_ttl=ttl, offer_cache=offers_cache)
        self._logger = stdout.get_logger()
        self._airline_validator = AirlineValidator(
            enabled_airlines=enabled_airlines,
            disabled_airlines=disabled_airlines,
        )
        self._resellers_map = resellers_map

    def search_criteria_generator(  # noqa: WPS210
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> SearchCriteriaWrapper:
        offer_request_builder = OffersRequestBuilder()
        outbound_date = protobuf.protobuf_to_datetime(
            search_task.criteria.outbound_departure,
        )

        for passenger_age in search_task.criteria.passenger_ages:
            offer_request_builder.add_passenger(
                OfferRequestPassenger(age=passenger_age, pax_type=None),
            )

        offer_request_builder.add_slice(
            OfferRequestSlice(
                destination=search_task.criteria.destination_iata,
                origin=search_task.criteria.origin_iata,
                departure_date=outbound_date,
            ),
        )

        if search_task.criteria.HasField("inbound_departure"):
            inbound_date = protobuf.protobuf_to_datetime(
                search_task.criteria.inbound_departure,
            )
            offer_request_builder.add_slice(
                OfferRequestSlice(
                    destination=search_task.criteria.origin_iata,
                    origin=search_task.criteria.destination_iata,
                    departure_date=inbound_date,
                ),
            )
        account_config = self._resellers_map.get(search_task.criteria.reseller_id)
        offer_request_builder.private_fares = dict_to_private_fares(
            account_config.get("private_fares", {}) if account_config else {},
        )
        return SearchCriteriaWrapper(
            search_criteria=offer_request_builder.build(),
            reseller_id=search_task.criteria.reseller_id,
        )

    def generate_cache_key(self, search_criteria_wrapper: SearchCriteriaWrapper) -> str:
        private_fares_keys: Sequence[str] = []
        if search_criteria_wrapper.search_criteria.offer_data.private_fares:
            private_fares_keys = _generate_private_fares_keys(
                search_criteria_wrapper.search_criteria.offer_data.private_fares,
            )
        return string.to_uuid(
            b"\x00".decode().join(
                [
                    *[
                        str(passenger.age)
                        for passenger in search_criteria_wrapper.search_criteria.offer_data.passengers
                    ],
                    *[
                        "{origin}-{destination}-{departure_date}".format(
                            origin=offer_slice.origin,
                            destination=offer_slice.destination,
                            departure_date=offer_slice.departure_date,
                        )
                        for offer_slice in search_criteria_wrapper.search_criteria.offer_data.slices
                    ],
                    *private_fares_keys,
                ],
            ),
        )

    async def gather_search_results(  # noqa: WPS210
        self,
        search_criteria_wrapper: SearchCriteriaWrapper,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        duffel_client = self._offers_client_factory.for_reseller(
            search_criteria_wrapper.reseller_id,
        )
        res = await duffel_client.create_offer_request(
            search_criteria_wrapper.search_criteria,
            rate_limit_timeout=30,  # noqa: WPS432
        )

        if res.offers:
            validator = Validators(
                self._airline_validator,
            )
            grouped_offers = OfferGrouper.group_offers(res.offers, validator.matches)

            for offers in grouped_offers.values():
                offer_group = await self._offer_parser.parse_offer_group(
                    offers,
                )

                if offer_group:
                    yield offer_group
