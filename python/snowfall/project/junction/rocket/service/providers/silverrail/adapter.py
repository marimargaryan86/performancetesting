from __future__ import annotations

import datetime
from collections.abc import AsyncIterator, Sequence

from iso4217 import Currency
from xsdata.models.datatype import (
    XmlDate,
    XmlTime,
)

from snowfall.project.junction.go.v1 import models_pb2 as go_models_pb2
from snowfall.project.junction.rocket.service.providers.silverrail import (
    constant,
    criteria,
    train_stations,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.time import date_to_age
from snowfall.stdlib.v1 import latlng_pb2, money_pb2
from snowfall.vendor.silverrail import client
from snowfall.vendor.silverrail.models.shopping import (
    DateTimeWindowType,
    FareCodeType,
    PointToPointPriceType,
    PointToPointShoppingQuery,
    PointToPointShoppingResponse,
    QueryTravelPointPairType,
    ServiceClassType,
    TicketableFareType,
    TotalPriceType,
    TravelPointType,
    TravelPointTypeEnumeration,
    TravelSegmentType,
)


class _SilverrailAdapter:
    def __init__(self, silverrail_client: client.SilverrailClient) -> None:
        self._client = silverrail_client


class SilverrailOffersAdapter(_SilverrailAdapter):
    def __init__(
        self,
        silverrail_client: client.SilverrailClient,
        train_station_repository: train_stations.TrainStationRepository,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(silverrail_client)
        self._train_stations = train_station_repository
        self._ttl = ttl
        self._logger = stdout.get_logger()

    async def gather_search_results(
        self,
        search_task: criteria.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        query = self._make_query(search_task)
        response = await self._client.shopping_point_to_point(query)
        search_results = self._convert_point_to_point_response(
            search_task.search_id,
            response,
        )
        for search_result in search_results:
            yield search_result

    def _make_query(
        self,
        search_task: criteria.Criteria,
    ) -> PointToPointShoppingQuery:
        travel_point_pairs = PointToPointShoppingQuery.TravelPointPairs(
            travel_point_pair=[
                QueryTravelPointPairType(
                    origin_travel_point=TravelPointType(
                        value=self._train_stations.get_by_id(search_task.origin).name,
                        type_value=TravelPointTypeEnumeration.STATION,
                    ),
                    destination_travel_point=TravelPointType(
                        value=self._train_stations.get_by_id(
                            search_task.destination,
                        ).name,
                        type_value=TravelPointTypeEnumeration.STATION,
                    ),
                    departure_date_time_window=DateTimeWindowType(
                        date=XmlDate.from_datetime(
                            search_task.outbound_departure_after,
                        ),
                        time=DateTimeWindowType.Time(
                            value=XmlTime.from_time(
                                search_task.outbound_departure_after.time(),
                            ),
                        ),
                    ),
                ),
            ],
        )
        passenger_specs = PointToPointShoppingQuery.PassengerSpecs(
            passenger_spec=[
                PointToPointShoppingQuery.PassengerSpecs.PassengerSpec(
                    passenger_spec_id="PAX_A{0}".format(idx + 1),
                    age=date_to_age(dob),
                )
                for idx, dob in enumerate(search_task.passenger_dobs)
            ],
        )
        return PointToPointShoppingQuery(
            travel_point_pairs=travel_point_pairs,
            passenger_specs=passenger_specs,
        )

    def _convert_point_to_point_response(
        self,
        search_id: str,
        response: PointToPointShoppingResponse,
    ) -> list[models_pb2.SearchResult]:
        self._raise_if_not_success(response)
        if response.results is None:
            raise client.SilverrailUnexpectedFormatError()

        if response.results.legs is None:
            raise client.SilverrailUnexpectedFormatError()

        search_results = self._convert_leg_solutions(search_id, response.results.legs)

        if response.results.fare_information is None:
            raise client.SilverrailUnexpectedFormatError()
        offers = self._convert_fare_information(response.results.fare_information)

        for leg_solution_id, search_result in search_results.items():
            search_result.offers.extend(offers[leg_solution_id])

        return list(search_results.values())

    def _raise_if_not_success(self, response: PointToPointShoppingResponse) -> None:
        if response.request_status is None:
            raise client.SilverrailUnexpectedFormatError()
        if response.request_status.success is None:
            raise client.SilverrailUnexpectedFormatError()

    # Returns one SearchResult per LegSolution. The offers for each SearchResult will
    # have to be filled later based on the rest of the response from Silverrail.
    def _convert_leg_solutions(  # noqa: WPS231
        self,
        search_id: str,
        legs: PointToPointShoppingResponse.Results.Legs,
    ) -> dict[str, models_pb2.SearchResult]:
        search_results: dict[str, models_pb2.SearchResult] = {}
        # The number of legs is always corresponding to the type of journey. For one-way, it's always one leg (no connection)
        # For round-trip, it's always two legs.
        for leg in legs.leg:
            # TODO(regis.blanc): Check that leg.origin_travel_point and leg.destination_travel_point
            # match our origin and destination, unless the Silverrail API can return more general search with intermediate
            # connections.

            if leg.leg_id is None or leg.leg_solutions is None:
                raise client.SilverrailUnexpectedFormatError()

            for leg_solution in leg.leg_solutions.leg_solution:
                if leg_solution.leg_solution_id is None:
                    raise client.SilverrailUnexpectedFormatError()
                travel_segments = leg_solution.travel_segments
                if travel_segments is None or travel_segments.travel_segment is None:
                    raise client.SilverrailUnexpectedFormatError()

                result_details = self._convert_travel_segments(
                    travel_segments.travel_segment,
                )
                search_results[leg_solution.leg_solution_id] = models_pb2.SearchResult(
                    id=string.uuid(),
                    search_id=search_id,
                    provider_id=str(constant.PROVIDER_ID),
                    result_details=result_details,
                )
        return search_results

    def _convert_travel_segments(  # noqa: WPS231
        self,
        travel_segments: Sequence[TravelSegmentType],
    ) -> list[models_pb2.ResultDetail]:
        result_details: list[models_pb2.ResultDetail] = []
        for idx, segment in enumerate(travel_segments):
            if segment.origin_travel_point is None:
                raise client.SilverrailUnexpectedFormatError()
            origin = self._train_stations.get_by_id(segment.origin_travel_point.value)

            if segment.destination_travel_point is None:
                raise client.SilverrailUnexpectedFormatError()
            destination = self._train_stations.get_by_id(
                segment.destination_travel_point.value,
            )

            if segment.departure_date_time is None or segment.arrival_date_time is None:
                raise client.SilverrailUnexpectedFormatError()

            # TODO(regis.blanc): Use the right timezone, check with Silverrail what timezone the results are in?
            departure_date = protobuf.datetime_to_protobuf_datetime(
                segment.departure_date_time.to_datetime().replace(tzinfo=datetime.UTC),
            )
            arrival_date = protobuf.datetime_to_protobuf_datetime(
                segment.arrival_date_time.to_datetime().replace(tzinfo=datetime.UTC),
            )
            result_details.append(
                models_pb2.ResultDetail(
                    rail=models_pb2.RailResultDetail(
                        origin=go_models_pb2.Point(
                            ref=origin.identifier,
                            name=origin.name,
                            coordinates=latlng_pb2.LatLng(
                                latitude=origin.latitude,
                                longitude=origin.longitude,
                            ),
                            time_zone=origin.timezone.key,
                        ),
                        destination=go_models_pb2.Point(
                            ref=destination.identifier,
                            name=destination.name,
                            coordinates=latlng_pb2.LatLng(
                                latitude=destination.latitude,
                                longitude=destination.longitude,
                            ),
                            time_zone=destination.timezone.key,
                        ),
                        segment_sequence=idx + 1,
                        departure_date=departure_date,
                        arrival_date=arrival_date,
                    ),
                ),
            )

        return result_details

    def _convert_fare_information(
        self,
        fare_information: PointToPointShoppingResponse.Results.FareInformation,
    ) -> dict[str, list[models_pb2.Offer]]:
        if fare_information.prices is None:
            raise client.SilverrailUnexpectedFormatError()
        if fare_information.prices.point_to_point_price is None:
            raise client.SilverrailUnexpectedFormatError()

        offers: dict[str, list[models_pb2.Offer]] = {}

        for point_to_point_price in fare_information.prices.point_to_point_price:
            # Identify the price in the format: PRICE_P_leg_price. Note that leg refers to the sequence of the leg in the
            # legs above, and not the particular leg_solution.
            leg_solution_id, offer = self._convert_point_to_point_price(
                point_to_point_price,
            )
            if leg_solution_id not in offers:
                offers[leg_solution_id] = []
            offers[leg_solution_id].append(offer)

        return offers

    # Convert the PointToPointPriceType to an Offer and return the corresponding leg
    # solution id.
    def _convert_point_to_point_price(
        self,
        ptp_price: PointToPointPriceType,
    ) -> tuple[str, models_pb2.Offer]:
        price_id = ptp_price.price_id
        total_price = ptp_price.total_price
        fares = ptp_price.ticketable_fares
        if price_id is None or total_price is None or fares is None:
            raise client.SilverrailUnexpectedFormatError()

        cabins = self._read_cabin_classes(fares)
        # TODO(regis.blanc): How to treat different cabin classes for different passengers?
        cabin_class = next(iter(cabins.values()))

        leg_ref = ptp_price.leg_references
        if leg_ref is None or leg_ref.leg_solution_idref is None:
            raise client.SilverrailUnexpectedFormatError()
        # TODO(regis.blanc): Assume this is a single leg solution ref. Check with
        # Silverrail if it's correct.
        leg_solution_ref: str = leg_ref.leg_solution_idref[0]

        offer = models_pb2.Offer(
            id=price_id,
            price=self._convert_total_price(total_price),
            rail=models_pb2.RailOffer(
                cabin_class=[
                    models_pb2.CabinDetails(
                        # TODO(regis.blanc): What is the result_id?
                        result_id="TODO",
                        cabin_class=cabin_class,
                    ),
                ],
            ),
        )
        return (leg_solution_ref, offer)

    def _convert_total_price(self, total_price: TotalPriceType) -> money_pb2.Money:
        if total_price.currency is None:
            raise client.SilverrailUnexpectedFormatError()
        if total_price.value is None:
            raise client.SilverrailUnexpectedFormatError()
        return money.from_string(
            str(total_price.value),
            Currency(total_price.currency),
        ).protobuf()

    # Map each passenger fare to the cabin class of the fare.
    def _read_cabin_classes(  # noqa: WPS231
        self,
        ticketable_fares: PointToPointPriceType.TicketableFares,
    ) -> dict[str, go_models_pb2.CabinClass]:
        res: dict[str, go_models_pb2.CabinClass] = {}

        for fare in ticketable_fares.ticketable_fare:
            refs = fare.passenger_references
            if refs is None or refs.passenger_reference is None:
                raise client.SilverrailUnexpectedFormatError()

            for pass_ref in refs.passenger_reference:
                pass_id = pass_ref.passenger_idref
                if pass_id is None:
                    raise client.SilverrailUnexpectedFormatError()
                cabin_class = self._convert_passenger_reference(pass_ref)
                res[pass_id] = cabin_class
        return res

    def _convert_passenger_reference(
        self,
        pass_ref: TicketableFareType.PassengerReferences.PassengerReference,
    ) -> go_models_pb2.CabinClass:
        fare_codes = pass_ref.fare_codes

        if fare_codes is None or fare_codes.fare_code is None:
            raise client.SilverrailUnexpectedFormatError()

        # TODO(regis.blanc): process pass_ref.fare_codes.fare_code list.
        fare_code = fare_codes.fare_code[0]
        return self._convert_fare_code(fare_code)

    def _convert_fare_code(self, fare_code: FareCodeType) -> go_models_pb2.CabinClass:
        if fare_code.service_class is None or fare_code.cabin_class is None:
            raise client.SilverrailUnexpectedFormatError()

        return go_models_pb2.CabinClass(
            type=self._convert_service_class(fare_code.service_class),
            marketing_name=fare_code.cabin_class,
        )

    def _convert_service_class(
        self,
        service_class: ServiceClassType,
    ) -> go_models_pb2.CabinClass.Type.ValueType:
        # These service classes are defined by Silverrail here: https://docs.silverrailtech.com/v1/docs/content-codes#Service_classes
        match service_class:
            case ServiceClassType.PREMIER:
                return go_models_pb2.CabinClass.TYPE_FIRST
            case ServiceClassType.FIRST:
                return go_models_pb2.CabinClass.TYPE_BUSINESS
            case ServiceClassType.SECOND | ServiceClassType.THIRD:
                return go_models_pb2.CabinClass.TYPE_ECONOMY
            case _:
                return go_models_pb2.CabinClass.TYPE_UNSPECIFIED
