from __future__ import annotations

import datetime
import enum
from typing import Any, Mapping

from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.v1alpha import money_pb2

_RELATIONSHIPS_FIELD = "data"


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


class UserResource(models.Resource):
    @classmethod
    def from_proto(cls, user: models_pb2.User) -> UserResource:
        attributes = {
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "phone": user.phone.e164_number,
            "loyaltyPrograms": [
                {"program": program.program, "number": program.number}
                for program in user.loyalty_programs
            ],
            "createdAt": protobuf.protobuf_to_datetime(
                user.created_at,
            ),
            "updatedAt": protobuf.protobuf_to_datetime(
                user.updated_at,
            ),
        }
        if user.gender:
            attributes["gender"] = user.gender
        if user.title:
            attributes["title"] = user.title
        if user.country_code:
            attributes["countryCode"] = user.country_code
        if user.date_of_birth.year:
            attributes["dateOfBirth"] = protobuf.protobuf_to_date(user.date_of_birth)
        return cls(
            id=user.id,
            type="users",
            attributes=attributes,
        )

    @classmethod
    def from_dict(cls, user_id: str, user: Mapping[str, Any]) -> UserResource:
        attributes = {}
        for field in user.keys():
            camel_field = string.to_lower_camel(field)
            attribute = user[field]
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
            type="users",
            attributes=attributes,
        )


class PlaceResource(models.Resource):
    @classmethod
    def from_proto(
        cls,
        place: models_pb2.Place,
    ) -> PlaceResource:
        return cls(
            id=place.id,
            type="places",
            attributes={
                "countryCode": place.country_code,
                "countryName": place.country_name,
                "iataCode": None,
                "latitude": place.coordinates.latitude,
                "longitude": place.coordinates.longitude,
                "name": place.name,
                "timeZone": place.time_zone,
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
