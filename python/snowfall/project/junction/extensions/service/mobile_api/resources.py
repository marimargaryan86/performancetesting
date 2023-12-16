from __future__ import annotations

import datetime
import enum
from collections.abc import Mapping
from typing import Any, Literal

from google.protobuf.json_format import MessageToDict

from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.project.junction.plus.adapter.flight_delay_predictor import Prediction
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    grpc_pb2 as plus_services_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1 import money_pb2

_RELATIONSHIPS_FIELD: Literal["data"] = "data"


class OrderResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        order: Mapping[str, Any],
    ) -> OrderResource:
        return cls(**order)


class OrderStatus(enum.Enum):
    unspecified = "unspecified"
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    not_ticketed = "not-ticketed"
    error = "error"
    timeout = "timeout"


class TripSearchResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        trip_search: Mapping[str, Any],
    ) -> TripSearchResource:
        return cls(**trip_search)


class TripSearchTripsResource(models.Resource):
    @classmethod
    def from_mongo(
        cls,
        trip_search_trip: Mapping[str, Any],
    ) -> TripSearchTripsResource:
        return cls(**trip_search_trip)


class GuestResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        guest: models_pb2.Guest,
    ) -> GuestResource:
        return cls(
            id=guest.id,
            type="guests",
            attributes={
                "createdAt": protobuf.protobuf_to_datetime(guest.created_at),
            },
        )


class UserResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        user: models_pb2.User,
        data_type: str = "users",
    ) -> UserResource:
        user_dict = MessageToDict(user)
        user_dict.pop("id")
        for user_field in user_dict:
            if user_field == "phone":
                user_dict["phone"] = user_dict["phone"]["e164Number"]
            if user_field == "dateOfBirth":
                user_dict[user_field] = protobuf.protobuf_to_date(user.date_of_birth)
            if user_field == "createdAt":
                user_dict[user_field] = protobuf.protobuf_to_datetime(
                    user.created_at,
                )
            if user_field == "updatedAt":
                user_dict[user_field] = protobuf.protobuf_to_datetime(
                    user.updated_at,
                )
        return cls(
            id=user.id,
            type=data_type,
            attributes=user_dict,
        )

    @classmethod
    def from_dict(
        cls,
        user_id: str,
        data_type: str,
        user: Mapping[str, Any],
    ) -> UserResource:
        attributes = {}
        for field, attribute in user.items():
            camel_field = string.to_lower_camel(field)
            if camel_field == "phone":
                attributes[camel_field] = attribute["e164_number"]
            elif camel_field == "dateOfBirth":
                attributes[camel_field] = datetime.date(
                    attribute["year"],
                    attribute["month"],
                    attribute["day"],
                )
            elif camel_field == "loyaltyPrograms":
                attributes[camel_field] = [
                    {"program": program["program"], "number": program["number"]}
                    for program in attribute
                ]
            else:
                attributes[camel_field] = attribute
        return cls(
            id=user_id,
            type=data_type,
            attributes=attributes,
        )


class PlaceResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
    ) -> PlaceResource:
        name = place.name
        if place.country_code == "SE" and place.local_name:
            name = "{name} ({local_name})".format(
                name=place.name,
                local_name=place.local_name,
            )
        return cls(
            id=place.id,
            type="places",
            attributes={
                "countryCode": place.country_code,
                "countryName": place.country_name,
                "iataCode": place.iata or None,
                "latitude": place.coordinates.latitude,
                "longitude": place.coordinates.longitude,
                "name": name,
                "timeZone": place.time_zone,
                "population": place.population,
                "mainCity": place.main_city,
            },
            relationships={
                "types": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=protobuf.enum_value_to_slug(
                                enum_descriptor=models_pb2.Place.Type.DESCRIPTOR,
                                enum_value=place_type,
                            ),
                            type="place-types",
                        )
                        for place_type in place.types
                    ],
                },
            },
        )


class LoyaltyProgram(models.Resource):
    @classmethod
    def from_proto(
        cls,
        program: models_pb2.LoyaltyProgram,
    ) -> LoyaltyProgram:
        return cls(
            id=program.id,
            type="loyalty-programs",
            attributes={
                "iata": program.iata,
                "airline": program.airline,
                "name": program.name,
            },
        )


class PushNotificationToken(models.Resource):
    @classmethod
    def from_proto(
        cls,
        token: models_pb2.NotificationToken,
    ) -> PushNotificationToken:
        return cls(
            id=token.notification_token,
            type="push-notification-tokens",
            attributes={
                "deviceToken": token.device_token,
                "createdAt": protobuf.protobuf_to_datetime(
                    token.created_at,
                ),
                "updatedAt": protobuf.protobuf_to_datetime(
                    token.updated_at,
                ),
            },
        )


class PreferenceResource(models.Resource):
    @classmethod
    def from_dict(
        cls,
        preference: Mapping[str, Any],
    ) -> PreferenceResource:
        return cls(
            id=preference["ref"],
            type="preferences",
            attributes={
                "title": preference["title"],
                "ref": preference["ref"],
                "type": preference["type"],
                "category": preference["category"],
                "value": preference["value"],
            },
        )


class Price(models.BaseModel):
    currency: str
    amount: str

    @classmethod
    def from_proto(cls, price: money_pb2.Money) -> Price:
        money_price = money.from_protobuf(price)

        return cls(
            currency=money_price.currency.code,
            amount=str(money_price),
        )


class VoucherResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        coupon: models_pb2.Voucher,
    ) -> VoucherResource:
        return cls(
            id=coupon.id,
            type="vouchers",
            attributes={
                "code": coupon.code,
                "expiresAt": protobuf.protobuf_to_date(
                    coupon.expires_at,
                ),
                "price": Price.from_proto(coupon.price),
                "status": protobuf.enum_value_to_slug(
                    models_pb2.Voucher.Status.DESCRIPTOR,
                    coupon.status,
                ),
            },
        )


class UserGroupResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        group: models_pb2.UserGroup,
    ) -> UserGroupResource:
        return cls(
            id=group.id,
            type="user-groups",
            attributes={
                "name": group.name,
                "createdAt": protobuf.protobuf_to_datetime(
                    group.created_at,
                ),
                "updatedAt": protobuf.protobuf_to_datetime(
                    group.updated_at,
                ),
            },
            relationships={
                "members": {
                    _RELATIONSHIPS_FIELD: [
                        models.ResourceIdentifier(
                            id=member.id,
                            type="user-group-members",
                        )
                        for member in group.members
                    ],
                },
            },
        )


class MarkupResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        markup: models_pb2.Markup,
    ) -> MarkupResource:
        return cls(
            id=markup.id,
            type="markups",
            attributes={
                "serviceFee": Price.from_proto(markup.service_fee),
                "agencyMarkup": Price.from_proto(markup.agency_markup),
                "totalToCollect": Price.from_proto(markup.total_to_collect),
                "createdAt": protobuf.protobuf_to_datetime(
                    markup.created_at,
                ),
                "updatedAt": protobuf.protobuf_to_datetime(
                    markup.updated_at,
                ),
            },
            relationships={
                "order": {
                    _RELATIONSHIPS_FIELD: models.ResourceIdentifier(
                        id=markup.order_id,
                        type="orders",
                    ),
                },
            },
        )


class PredictionResource(models.Resource):
    @classmethod
    def from_dict(
        cls,
        prediction: Prediction,
    ) -> PredictionResource:
        return cls(
            id=prediction.id,
            type="flight-delay-prediction",
            attributes={
                "flightNumber": prediction.flight_number,
                "scheduledDepartureAt": prediction.scheduled_departure_at,
                "delay": prediction.delay,
            },
        )


class Co2EmissionsResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        co2_emission: plus_services_pb2.FlightEmission,
        departure_date: str,
    ) -> Co2EmissionsResource:
        return cls(
            id="{0}{1}".format(
                co2_emission.operating_carrier_code,
                co2_emission.flight_number,
            ),
            type="emissions",
            attributes={
                "flight": {
                    "origin": co2_emission.origin,
                    "destination": co2_emission.destination,
                    "operatingCarrierCode": co2_emission.operating_carrier_code,
                    "flightNumber": co2_emission.flight_number,
                    "departureDate": departure_date,
                },
                "emissions": {
                    "first": co2_emission.emissions_per_pax.first,
                    "business": co2_emission.emissions_per_pax.business,
                    "premiumEconomy": co2_emission.emissions_per_pax.premium_economy,
                    "economy": co2_emission.emissions_per_pax.economy,
                    "unit": co2_emission.unit,
                },
            },
        )
