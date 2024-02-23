import datetime
import zoneinfo
from collections import defaultdict
from collections.abc import AsyncIterator
from types import MappingProxyType
from typing import Any

import httpx
import timezonefinder

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.service.providers.carnect import (
    cache,
    constants,
)
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
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
_tz_finder = timezonefinder.TimezoneFinder()

_CABIN_MAPPING = MappingProxyType({
    "1": models_pb2.CabinClass.TYPE_ECONOMY,
    "2": models_pb2.CabinClass.TYPE_ECONOMY,
    "3": models_pb2.CabinClass.TYPE_ECONOMY,
    "4": models_pb2.CabinClass.TYPE_ECONOMY,
    "5": models_pb2.CabinClass.TYPE_ECONOMY,
    "6": models_pb2.CabinClass.TYPE_ECONOMY,
    "7": models_pb2.CabinClass.TYPE_ECONOMY,
    "8": models_pb2.CabinClass.TYPE_PREMIUM,
    "9": models_pb2.CabinClass.TYPE_FIRST,
    "10": models_pb2.CabinClass.TYPE_PREMIUM,
    "11": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "12": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "13": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "14": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "15": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "16": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "17": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "18": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "19": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "20": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "21": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "22": models_pb2.CabinClass.TYPE_ECONOMY,
    "23": models_pb2.CabinClass.TYPE_FIRST,
    "24": models_pb2.CabinClass.TYPE_FIRST,
    "25": models_pb2.CabinClass.TYPE_UNSPECIFIED,
    "26": models_pb2.CabinClass.TYPE_UNSPECIFIED,
})
_TYPE_GEO_COORDINATES = "6"
_LOCATION_CODE_CONTEXT = "3"
_REQ_RESP_VERSION = "large"
_COVERAGE_TYPE_CANCELLATION_FEE = "CF"


class FieldMissingError(Exception):
    """When required field is missing."""


def get_zone_for_coordinate(coordinate: latlng_pb2.LatLng) -> zoneinfo.ZoneInfo:
    return zoneinfo.ZoneInfo(
        _tz_finder.timezone_at(
            lat=coordinate.latitude,
            lng=coordinate.longitude,
        )
        or "",
    )


def split_coordinates(coordinate_pair: str) -> tuple[float, float]:
    lat, lng = coordinate_pair.split(",")
    return float(lat), float(lng)


def get_optional_value(obj: Any, accessor: str, default: Any) -> Any:
    parts = accessor.split(".")
    for part in parts:
        obj = getattr(obj, part)
        if obj is None:
            return default
    return obj


def _get_coordinates(  # noqa: WPS238
    veh_avail: CarnectVehAvail,
) -> CoordinatesTuple:
    try:
        origin = veh_avail.veh_avail_core.vendor_location.value  # type: ignore[union-attr]
    except AttributeError as error:
        raise FieldMissingError() from error

    try:
        destination = veh_avail.veh_avail_core.drop_off_location.value  # type: ignore[union-attr]
    except AttributeError as exc:
        raise FieldMissingError() from exc

    if not origin:
        raise FieldMissingError("Origin field is missing")
    if not destination:
        raise FieldMissingError("Destination field is missing")
    return split_coordinates(origin), split_coordinates(destination)


def _get_equipment(
    veh_avail: CarnectVehAvail,
) -> str:
    veh_size_id = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.veh_class.size",
        "",
    )
    veh_category_id = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.veh_type.vehicle_category",
        "",
    )
    veh_size = vehicle.VEHICLE_SIZES.get(veh_size_id)
    veh_category = vehicle.VEHICLE_CATEGORIES.get(veh_category_id)
    equipment_parts = []

    if veh_size:
        equipment_parts.append(veh_size)
    if veh_category:
        equipment_parts.append(veh_category)

    return ",".join(equipment_parts)


def get_offer_price(  # noqa: WPS238
    veh_avail: CarnectVehAvail,
) -> money.Money:
    try:
        amount = veh_avail.veh_avail_core.total_charge[0].estimated_total_amount  # type: ignore[union-attr]
    except (AttributeError, IndexError) as error:
        raise FieldMissingError() from error

    try:
        currency_code = veh_avail.veh_avail_core.total_charge[0].currency_code  # type: ignore[union-attr]
    except (AttributeError, IndexError) as exc:
        raise FieldMissingError() from exc

    if not amount:
        raise FieldMissingError("Price amount field is missing: {0}".format(amount))
    if not currency_code:
        raise FieldMissingError(
            "Price currency_code field is missing: {0}".format(currency_code),
        )

    return money.from_string(
        str(amount),
        currency=money.Currency(currency_code.upper()),
    )


def get_conditional_prices(
    veh_avail: CarnectVehAvail,
) -> list[offer_models_pb2.ConditionalPrice]:
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
                offer_models_pb2.ConditionalPrice(
                    price=money.from_string(
                        string_amount=str(charge.amount),
                        currency=money.Currency(charge.currency_code),
                    ).protobuf(),
                    description=charge.description,
                    included_in_total=charge.included_in_est_total_ind,
                ),
            )

    return conditional_prices


def get_fare_rules(
    veh_avail: CarnectVehAvail,
) -> list[offer_models_pb2.FareRule]:
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
                offer_models_pb2.FareRule(
                    title="Cancellation conditions",
                    body=charge.description,
                ),
            )

    return fare_rules


def _get_cabin_class_type(
    veh_avail: CarnectVehAvail,
) -> models_pb2.CabinClass.Type.ValueType:
    return _CABIN_MAPPING.get(
        get_optional_value(
            veh_avail,
            "veh_avail_core.vehicle.veh_class.size",
            "",
        ),
        models_pb2.CabinClass.TYPE_UNSPECIFIED,
    )


def _is_baggage_free(veh_avail: CarnectVehAvail) -> bool:
    return bool(
        get_optional_value(
            veh_avail,
            accessor="veh_avail_core.vehicle.baggage_quantity",
            default=False,
        ),
    )


def _parse_offer(
    veh_avail: CarnectVehAvail,
    segment: offer_models_pb2.OfferSegment,
) -> offer_models_pb2.Offer:
    offer_price = get_offer_price(veh_avail)

    price_breakdown = [
        offer_models_pb2.PriceBreakdown(
            price=offer_price.protobuf(),
            breakdown_type=offer_models_pb2.PriceBreakdown.BreakdownType.BREAKDOWN_TYPE_BASE_FARE,
        ),
    ]

    return offer_models_pb2.Offer(
        id=string.uuid(),
        segment_details=[
            offer_models_pb2.OfferSegmentDetails(
                id=string.uuid(),
                offer_segment_id=segment.id,
                cabin_class=models_pb2.CabinClass(
                    type=_get_cabin_class_type(veh_avail),
                    marketing_name="Snowfall",
                ),
                amenities=_get_amenities(veh_avail),
                vehicle=_get_vehicle_information(veh_avail),
                baggage_allowances=[
                    offer_models_pb2.BaggageAllowance(
                        free=_is_baggage_free(veh_avail),
                    ),
                ],
            ),
        ],
        price=offer_price.protobuf(),
        price_breakdown=price_breakdown,
        conditional_prices=get_conditional_prices(veh_avail),
        brand_name=get_optional_value(
            veh_avail,
            "veh_avail_core.vendor.company_short_name",
            "",
        ),
    )


def _parse_segment(
    veh_avail: CarnectVehAvail,
    pick_up_datetime: datetime.datetime,
    return_datetime: datetime.datetime,
) -> offer_models_pb2.OfferSegment:
    leg = _get_leg(veh_avail, pick_up_datetime, return_datetime)
    vendor = get_optional_value(veh_avail, "veh_avail_core.vendor.code", "")

    return offer_models_pb2.OfferSegment(
        id=string.uuid(),
        legs=[leg],
        vehicle=offer_models_pb2.Vehicle(
            equipment=_get_equipment(veh_avail),
        ),
        vendor=vendor,
        type=models_pb2.Schedule.TYPE_CAR,
    )


def _get_amenities(veh_avail: CarnectVehAvail) -> offer_models_pb2.SegmentAmenities:
    amenities = offer_models_pb2.SegmentAmenities()

    veh_avail_air_condition = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.air_condition_ind",
        default=False,
    )

    if veh_avail_air_condition:
        amenities.air_conditioner.availability = (
            offer_models_pb2.SegmentAmenity.TYPE_INCLUDED
        )

    try:
        is_unlimited = (
            veh_avail.veh_avail_core.rental_rate[0].rate_distance[0].unlimited  # type: ignore[union-attr] # noqa: WPS219
        )
    except (IndexError, AttributeError):
        is_unlimited = False

    if is_unlimited:
        amenities.unlimited_mileage.availability = (
            offer_models_pb2.SegmentAmenity.TYPE_INCLUDED
        )
    else:
        amenities.unlimited_mileage.availability = (
            offer_models_pb2.SegmentAmenity.TYPE_UNAVAILABLE
        )

    return amenities


def _get_vehicle_information(
    veh_avail: CarnectVehAvail,
) -> offer_models_pb2.VehicleInformation:
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
    fuel_type = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.fuel_type.value",
        None,
    )
    baggage_quantity = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.baggage_quantity",
        None,
    )
    drive_type = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.drive_type.value",
        None,
    )
    car_class = get_optional_value(
        veh_avail,
        "veh_avail_core.vehicle.vendor_car_type",
        None,
    )

    return offer_models_pb2.VehicleInformation(
        image_url=image_url,
        model=model,
        seats_count=_convert_to_integer(seats_count),
        doors_count=_convert_to_integer(doors_count),
        transmission=transmission,
        fuel_type=fuel_type,
        baggage_quantity=_convert_to_integer(baggage_quantity),
        drive_type=drive_type,
        car_class=car_class,
    )


def _convert_to_integer(value: str | None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _get_leg(
    veh_avail: CarnectVehAvail,
    pick_up_datetime: datetime.datetime,
    return_datetime: datetime.datetime,
) -> offer_models_pb2.OfferSegmentLeg:
    origin, destination = _get_coordinates(veh_avail)

    origin_coordinate = latlng_pb2.LatLng(
        latitude=origin[0],
        longitude=origin[1],
    )
    destination_coordinate = latlng_pb2.LatLng(
        latitude=destination[0],
        longitude=destination[1],
    )
    return offer_models_pb2.OfferSegmentLeg(
        id=string.uuid(),
        origin=models_pb2.Point(
            name=get_optional_value(
                veh_avail,
                "veh_avail_core.vendor_location.name",
                "",
            ),
            coordinates=origin_coordinate,
            time_zone=get_zone_for_coordinate(
                coordinate=origin_coordinate,
            ).key,
        ),
        destination=models_pb2.Point(
            name=get_optional_value(
                veh_avail,
                "veh_avail_core.drop_off_location.name",
                "",
            ),
            coordinates=destination_coordinate,
            time_zone=get_zone_for_coordinate(
                coordinate=destination_coordinate,
            ).key,
        ),
        departure_at=protobuf.datetime_to_protobuf(pick_up_datetime),
        arrival_at=protobuf.datetime_to_protobuf(return_datetime),
    )


class CarnectOfferMatcher(object):
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: config.Config,
    ):
        self._client = carnect_client
        self._config = carnect_config
        self._cut_off = 30
        self._logger = stdout.get_logger()

    async def get_matching_quote(
        self,
        offer_details: cache.OfferDetails,
    ) -> CarnectVehAvail | None:
        search_task = amqp_pb2.Criteria(
            origin=latlng_pb2.LatLng(
                latitude=offer_details.origin.latitude,
                longitude=offer_details.origin.longitude,
            ),
            destination=latlng_pb2.LatLng(
                latitude=offer_details.destination.latitude,
                longitude=offer_details.destination.longitude,
            ),
            passengers_count=offer_details.passengers_count,
            driver_age=offer_details.driver_age,
            pick_up_datetime=protobuf.datetime_to_protobuf_datetime(
                offer_details.departure_at,
            ),
            return_datetime=protobuf.datetime_to_protobuf_datetime(
                offer_details.arrival_at,
            ),
        )

        response = await self._client.get_avail_rate(
            _build_request(
                search_task=search_task,
                vendor_code=offer_details.vendor,
                carnect_config=self._config,
            ),
        )

        rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(response)

        if not rs_adapter.is_success():
            self._logger.error(
                "VehAvailRate search failed",
                criteria=str(search_task),
                message=rs_adapter.get_error(),
            )
            return None

        for availability_type in rs_adapter.available():
            veh_avails = get_optional_value(
                availability_type,
                "veh_avails.veh_avail",
                [],
            )

            for veh_avail in veh_avails:
                if self._offer_matches(veh_avail, offer_details):
                    return veh_avail

        return None

    def _offer_matches(
        self,
        veh_avail: CarnectVehAvail,
        offer_details: cache.OfferDetails,
    ) -> bool:
        return all(
            [
                int(_get_cabin_class_type(veh_avail)) == offer_details.cabin_class,
                _get_equipment(veh_avail) == offer_details.equipment,
                _is_baggage_free(veh_avail) == offer_details.free_baggage,
            ],
        )


class CarnectOffersAdapter(object):
    def __init__(
        self,
        carnect_client: client.CarnectClient,
        carnect_config: config.Config,
        offers_cache: cache.OffersCache,
        ttl: datetime.timedelta,
    ):
        self._client = carnect_client
        self._config = carnect_config
        self._logger = stdout.get_logger()
        self._offers_cache = offers_cache
        self._ttl = ttl

    async def gather_offer_groups(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        try:
            async for offer_group in self._gather_offer_groups(search_task):
                yield offer_group
        except httpx.HTTPError:
            self._logger.exception("Offer search failed")

    async def _gather_offer_groups(
        self,
        search_task: amqp_pb2.Criteria,
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        response = await self._client.get_avail_rate(
            _build_request(search_task, self._config),
        )
        rs_adapter = veh_avail_rate_adapter.VehAvailRateAdapter(response)
        if not rs_adapter.is_success():
            self._logger.error(
                "VehAvailRate search failed",
                criteria=str(search_task),
                message=rs_adapter.get_error(),
            )
            return

        veh_avail_map = self._get_veh_avail_map(rs_adapter.available())

        async for offer_group in self._generate_groups(search_task, veh_avail_map):
            yield offer_group

    def _get_veh_avail_map(
        self,
        veh_avails_type: list[service.VehicleVendorAvailabilityType],
    ) -> dict[CoordinatesTuple, list[CarnectVehAvail]]:
        mapping = defaultdict(list)
        for availability_type in veh_avails_type:
            veh_avails = get_optional_value(
                availability_type,
                "veh_avails.veh_avail",
                [],
            )
            for veh_avail in veh_avails:
                try:
                    key = _get_coordinates(veh_avail)
                except FieldMissingError:
                    self._logger.exception(
                        "Required field is missing while parsing coordinates",
                    )
                    continue
                mapping[key].append(veh_avail)
        return mapping

    async def _generate_groups(
        self,
        search_task: amqp_pb2.Criteria,
        veh_avail_map: dict[CoordinatesTuple, list[CarnectVehAvail]],
    ) -> AsyncIterator[offer_models_pb2.OfferGroup]:
        for veh_avails in veh_avail_map.values():
            try:
                segment = _parse_segment(
                    veh_avails[0],
                    protobuf.protobuf_to_datetime(search_task.pick_up_datetime),
                    protobuf.protobuf_to_datetime(search_task.return_datetime),
                )
            except FieldMissingError:
                self._logger.exception("Required field missing while parsing segment")
                continue

            offers = await self._generate_offers(search_task, veh_avails, segment)
            if not offers:
                continue

            yield offer_models_pb2.OfferGroup(
                id=string.uuid(),
                expires_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(datetime.UTC) + self._ttl,
                ),
                offers=offers,
                segments=[segment],
                provider_id=str(constants.PROVIDER_ID),
            )

    async def _generate_offers(
        self,
        search_task: amqp_pb2.Criteria,
        veh_avails: list[CarnectVehAvail],
        segment: offer_models_pb2.OfferSegment,
    ) -> list[offer_models_pb2.Offer]:
        offers = []
        for veh_avail in veh_avails:
            try:
                offer = _parse_offer(veh_avail, segment)
            except FieldMissingError:
                self._logger.exception("Missing field while parsing offer")
                continue

            vendor = get_optional_value(veh_avail, "veh_avail_core.vendor.code", None)

            await self._cache_offer(
                search_task=search_task,
                offer_id=offer.id,
                vendor=vendor,
                cabin_class_type=int(_get_cabin_class_type(veh_avail)),
                equipment=_get_equipment(veh_avail),
                free_baggage=_is_baggage_free(veh_avail),
            )
            offers.append(offer)
        return offers

    async def _cache_offer(
        self,
        search_task: amqp_pb2.Criteria,
        offer_id: str,
        vendor: str | None,
        cabin_class_type: int,
        equipment: str,
        *,
        free_baggage: bool,
    ) -> None:
        await self._offers_cache.store(
            cache.OfferDetails(
                origin=cache.Coordinates(
                    latitude=search_task.origin.latitude,
                    longitude=search_task.origin.longitude,
                ),
                destination=cache.Coordinates(
                    latitude=search_task.destination.latitude,
                    longitude=search_task.destination.longitude,
                ),
                passengers_count=search_task.passengers_count,
                driver_age=search_task.driver_age,
                vendor=vendor,
                cabin_class=cabin_class_type,
                equipment=equipment,
                free_baggage=free_baggage,
                departure_at=protobuf.protobuf_to_datetime(
                    search_task.pick_up_datetime,
                ),
                arrival_at=protobuf.protobuf_to_datetime(
                    search_task.return_datetime,
                ),
            ),
            expires_at=datetime.datetime.now(datetime.UTC) + self._ttl,
            key=offer_id,
        )


def _build_request(
    search_task: amqp_pb2.Criteria,
    carnect_config: config.Config,
    vendor_code: str | None = None,
) -> service.VehAvailRateRq:
    request = veh_avail_rate_builder.VehAvailRateRqBuilder(carnect_config)

    request.version(_REQ_RESP_VERSION)
    request.rate_query_type(service.RateQueryType.LIVE)
    request.rate_query_parameter_type(_TYPE_GEO_COORDINATES)
    request.add_driver_age(search_task.driver_age)
    request.add_passenger_quantity(search_task.passengers_count)
    if vendor_code:
        request.add_pref_vendor(vendor_code)
    rental_core = request.get_rental_core()
    rental_core.pick_up_date(
        protobuf.protobuf_to_datetime(
            search_task.pick_up_datetime,
        ),
    )
    rental_core.return_date(
        protobuf.protobuf_to_datetime(
            search_task.return_datetime,
        ),
    )
    origin = "{lat},{lon}".format(
        lat=search_task.origin.latitude,
        lon=search_task.origin.longitude,
    )
    destination = "{lat},{lon}".format(
        lat=search_task.destination.latitude,
        lon=search_task.destination.longitude,
    )
    rental_core.add_pick_up_location(origin, _LOCATION_CODE_CONTEXT)
    rental_core.return_location(destination, _LOCATION_CODE_CONTEXT)

    return request.build()
