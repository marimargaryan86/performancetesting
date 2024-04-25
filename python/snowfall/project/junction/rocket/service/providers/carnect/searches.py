import datetime
import itertools
from collections.abc import AsyncIterator, Sequence
from typing import Any

import httpx
import timezonefinder
from dateutil import tz

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.providers.carnect import (
    cache,
    constants,
    criteria,
    errors,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import latlng_pb2
from snowfall.vendor.carnect import client, config
from snowfall.vendor.carnect.adapters import veh_avail_rate_adapter
from snowfall.vendor.carnect.builders import veh_avail_rate_builder
from snowfall.vendor.carnect.models import service, vehicle

CarnectVehAvail = service.VehicleVendorAvailabilityType.VehAvails.VehAvail
CoordinatesTuple = tuple[tuple[float, float], tuple[float, float]]

_TYPE_GEO_COORDINATES = "6"
_LOCATION_CODE_CONTEXT = "3"
_REQ_RESP_VERSION = "large"
_COVERAGE_TYPE_CANCELLATION_FEE = "CF"


_tz_finder = timezonefinder.TimezoneFinder()


def get_optional_value(obj: Any, accessor: str, default: Any) -> Any:
    parts = accessor.split(".")
    for part in parts:
        obj = getattr(obj, part)
        if obj is None:
            return default
    return obj


class SearchResultGenerator:
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: config.Config,
        search_result_cache: cache.SearchResultCache,
        ttl: datetime.timedelta,
        pay_company_id: str,
    ):
        self._client = carnect_client
        self._config = carnect_config
        self._search_result_cache = search_result_cache
        self._logger = stdout.get_logger()
        self._ttl = ttl
        self._pay_company_id = pay_company_id

    async def gather_search_results(
        self,
        search_task: criteria.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        try:
            async for search_result in self._gather_search_results(search_task):
                yield search_result
        except httpx.HTTPError:
            self._logger.exception("Offer search failed")

    async def _gather_search_results(
        self,
        search_task: criteria.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        response = await self._client.get_avail_rate(
            build_request(search_task, self._config),
        )
        rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(response)
        if not rs_adapter.is_success():
            self._logger.error(
                "VehAvailRate search failed",
                criteria=search_task,
                message=rs_adapter.get_error(),
            )
            return

        veh_avails = self._get_veh_avails(rs_adapter.available())
        rental_core = rs_adapter.rental_core()

        if not rental_core:
            raise ValueError("Rental core is missing")

        search_results = self._generate_search_results(
            search_task,
            veh_avails,
            rental_core,
        )

        async for search_result in search_results:
            offer = search_result.offers[0]
            details = search_result.result_details[0].car_rental
            await self._search_result_cache.store(
                cache.CarRentalResultDetail(
                    origin=cache.Coordinates(
                        latitude=details.origin.coordinates.latitude,
                        longitude=details.origin.coordinates.longitude,
                    ),
                    destination=cache.Coordinates(
                        latitude=details.destination.coordinates.latitude,
                        longitude=details.destination.coordinates.longitude,
                    ),
                    departure_at=search_task.pickup_datetime,
                    arrival_at=search_task.return_datetime,
                    driver_age=search_task.driver_age,
                    model=details.model,
                    seats_count=details.seats_count,
                    doors_count=details.doors_count,
                    transmission=details.transmission,
                    baggage_quantity=details.baggage_quantity,
                    vehicle_type=details.vehicle_type,
                    vendor_name=details.vendor_name,
                    vendor_code=details.vendor_code,
                ),
                expires_at=datetime.datetime.now(datetime.UTC) + self._ttl,
                key=offer.id,
            )
            yield search_result

    def _get_veh_avails(
        self,
        veh_avails_type: Sequence[service.VehicleVendorAvailabilityType],
    ) -> list[CarnectVehAvail]:
        veh_avails = [
            get_optional_value(
                availability_type,
                "veh_avails.veh_avail",
                [],
            )
            for availability_type in veh_avails_type
        ]

        return list(itertools.chain(*veh_avails))

    async def _generate_search_results(
        self,
        search_task: criteria.Criteria,
        veh_avails: Sequence[CarnectVehAvail],
        rental_core: service.VehicleRentalCoreType,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        pick_up_date_time: datetime.datetime | None = None
        return_date_time: datetime.datetime | None = None

        if rental_core.pick_up_date_time:
            pick_up_date_time = rental_core.pick_up_date_time.to_datetime()

        if rental_core.return_date_time:
            return_date_time = rental_core.return_date_time.to_datetime()

        if not pick_up_date_time or not return_date_time:
            raise ValueError("Pickup or return date time is missing")

        pickup_at = pick_up_date_time.astimezone(
            tz.gettz(
                _tz_finder.timezone_at(
                    lat=search_task.origin.coordinates.latitude,
                    lng=search_task.origin.coordinates.longitude,
                ),
            ),
        )
        return_at = return_date_time.astimezone(
            tz.gettz(
                _tz_finder.timezone_at(
                    lat=search_task.destination.coordinates.latitude,
                    lng=search_task.destination.coordinates.longitude,
                ),
            ),
        )

        for veh_avail in veh_avails:
            try:
                offer = parse_offer(veh_avail)
            except errors.FieldMissingError:
                self._logger.exception("Missing field while parsing offer")
                continue

            yield models_pb2.SearchResult(
                id=string.uuid(),
                search_id=search_task.search_id,
                provider_id=str(constants.PROVIDER_ID),
                pay_company_id=self._pay_company_id,
                expires_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(datetime.UTC) + self._ttl,
                ),
                offers=[offer],
                result_details=[
                    models_pb2.ResultDetail(
                        id=string.uuid(),
                        car_rental=get_car_rental_result_detail(
                            veh_avail=veh_avail,
                            pickup_at=pickup_at,
                            return_at=return_at,
                        ),
                    ),
                ],
            )


def _get_coordinates(  # noqa: WPS238
    veh_avail: CarnectVehAvail,
) -> CoordinatesTuple:
    try:
        origin = veh_avail.veh_avail_core.vendor_location.value  # type: ignore[union-attr]
    except AttributeError as error:
        raise errors.FieldMissingError() from error

    try:
        destination = veh_avail.veh_avail_core.drop_off_location.value  # type: ignore[union-attr]
    except AttributeError as exc:
        raise errors.FieldMissingError() from exc

    if not origin:
        raise errors.FieldMissingError("Origin field is missing")
    if not destination:
        raise errors.FieldMissingError("Destination field is missing")

    return _split_coordinates(origin), _split_coordinates(destination)


def _split_coordinates(coordinate_pair: str) -> tuple[float, float]:
    lat, lng = coordinate_pair.split(",")
    return float(lat), float(lng)


def parse_offer(
    veh_avail: CarnectVehAvail,
) -> models_pb2.Offer:
    offer_price = _get_offer_price(veh_avail)

    price_breakdown = [
        models_pb2.PriceBreakdown(
            price=offer_price.protobuf(),
            breakdown_type=models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
        ),
    ]

    return models_pb2.Offer(
        id=string.uuid(),
        price=offer_price.protobuf(),
        price_breakdown=price_breakdown,
        car_rental=models_pb2.CarRentalOffer(
            conditional_prices=_get_conditional_prices(veh_avail),
        ),
    )


def _get_offer_price(  # noqa: WPS238
    veh_avail: CarnectVehAvail,
) -> money.Money:
    try:
        amount = veh_avail.veh_avail_core.total_charge[0].estimated_total_amount  # type: ignore[union-attr]
    except (AttributeError, IndexError) as error:
        raise errors.FieldMissingError() from error

    try:
        currency_code = veh_avail.veh_avail_core.total_charge[0].currency_code  # type: ignore[union-attr]
    except (AttributeError, IndexError) as exc:
        raise errors.FieldMissingError() from exc

    if not amount:
        raise errors.FieldMissingError(
            "Price amount field is missing: {0}".format(amount),
        )
    if not currency_code:
        raise errors.FieldMissingError(
            "Price currency_code field is missing: {0}".format(currency_code),
        )

    return money.from_string(
        str(amount),
        currency=money.Currency(currency_code.upper()),
    )


def get_fare_rules(
    veh_avail: CarnectVehAvail,
) -> list[models_pb2.FareRule]:
    priced_coverages = get_optional_value(
        veh_avail,
        "veh_avail_info.priced_coverages.priced_coverage",
        [],
    )

    fare_rules = []

    for priced_coverage in priced_coverages:
        details = get_optional_value(priced_coverage, "coverage.details", [])
        coverage_code = get_optional_value(priced_coverage, "coverage.code", None)

        for detail in details:
            charge = detail.charge

            if (  # noqa: WPS337
                not charge
                or not charge.description
                or coverage_code != _COVERAGE_TYPE_CANCELLATION_FEE
            ):
                continue

            fare_rules.append(
                models_pb2.FareRule(
                    title="Cancellation conditions",
                    body=charge.description,
                ),
            )

    return fare_rules


def get_car_rental_result_detail(
    veh_avail: CarnectVehAvail,
    pickup_at: datetime.datetime,
    return_at: datetime.datetime,
) -> models_pb2.CarRentalResultDetail:
    origin, destination = _get_coordinates(veh_avail)
    image_url = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.picture_url",
        None,
    )
    model = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.veh_make_model.name",
        None,
    )
    seats_count = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.passenger_quantity",
        None,
    )
    doors_count = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.veh_type.door_count",
        None,
    )
    transmission = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.transmission_type.value",
        None,
    )
    baggage_quantity = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.baggage_quantity",
        None,
    )

    vendor_name = get_optional_value(veh_avail, "veh_avail_core.vendor.value", "")
    vendor_code = get_optional_value(veh_avail, "veh_avail_core.vendor.code", "")

    veh_category_id = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.veh_type.vehicle_category",
        "",
    )
    vehicle_type = vehicle.VEHICLE_CATEGORIES.get(veh_category_id)

    try:
        is_unlimited = (
            veh_avail.veh_avail_core.rental_rate[0].rate_distance[0].unlimited  # type: ignore[union-attr] # noqa: WPS219
        )
    except (IndexError, AttributeError):
        is_unlimited = False

    veh_avail_air_condition = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.air_condition_ind",
        default=False,
    )

    return models_pb2.CarRentalResultDetail(
        origin=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=origin[0],
                longitude=origin[1],
            ),
        ),
        destination=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=destination[0],
                longitude=destination[1],
            ),
        ),
        image_url=image_url,
        model=model,
        seats_count=_convert_to_integer(seats_count),
        doors_count=_convert_to_integer(doors_count),
        transmission=transmission,
        baggage_quantity=_convert_to_integer(baggage_quantity),
        vehicle_type=vehicle_type,
        vendor_name=vendor_name,
        vendor_code=vendor_code,
        unlimited_mileage=is_unlimited,
        air_conditioner=veh_avail_air_condition,
        pickup_at=protobuf.datetime_to_protobuf_datetime(pickup_at),
        return_at=protobuf.datetime_to_protobuf_datetime(return_at),
    )


def _get_conditional_prices(
    veh_avail: CarnectVehAvail,
) -> list[models_pb2.ConditionalPrice]:
    priced_coverages = get_optional_value(
        veh_avail,
        "veh_avail_info.priced_coverages.priced_coverage",
        [],
    )

    conditional_prices = []

    for priced_coverage in priced_coverages:
        details = get_optional_value(priced_coverage, "coverage.details", [])
        coverage_code = get_optional_value(priced_coverage, "coverage.code", None)

        for detail in details:
            charge = detail.charge

            if (  # noqa: WPS337
                not charge
                or not charge.amount
                or not charge.currency_code
                or coverage_code == _COVERAGE_TYPE_CANCELLATION_FEE
            ):
                continue

            conditional_prices.append(
                models_pb2.ConditionalPrice(
                    price=money.from_string(
                        string_amount=str(charge.amount),
                        currency=money.Currency(charge.currency_code),
                    ).protobuf(),
                    description=charge.description,
                    included_in_total=charge.included_in_est_total_ind,
                ),
            )

    return conditional_prices


def _convert_to_integer(value: str | None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def build_request(
    search_task: criteria.Criteria,
    carnect_config: config.Config,
    vendor_code: str | None = None,
) -> service.VehAvailRateRq:
    request = veh_avail_rate_builder.VehAvailRateRqBuilder(carnect_config)

    request.version(_REQ_RESP_VERSION)
    request.rate_query_type(service.RateQueryType.LIVE)
    request.rate_query_parameter_type(_TYPE_GEO_COORDINATES)
    request.add_driver_age(search_task.driver_age)

    if vendor_code:
        request.add_pref_vendor(vendor_code)
    rental_core = request.get_rental_core()

    rental_core.pick_up_date(search_task.pickup_datetime)
    rental_core.return_date(search_task.return_datetime)

    origin = "{lat},{lon}".format(
        lat=search_task.origin.coordinates.latitude,
        lon=search_task.origin.coordinates.longitude,
    )
    destination = "{lat},{lon}".format(
        lat=search_task.destination.coordinates.latitude,
        lon=search_task.destination.coordinates.longitude,
    )
    rental_core.add_pick_up_location(origin, _LOCATION_CODE_CONTEXT)
    rental_core.return_location(destination, _LOCATION_CODE_CONTEXT)

    return request.build()
