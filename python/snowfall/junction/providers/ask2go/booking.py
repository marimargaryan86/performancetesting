import datetime

import phonenumbers
import pycountry

from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.junction.providers.ask2go import criteria
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.models import common


async def book(
    a2g: client.Ask2GoClient,
    order: models_pb2.Order,
    details: tuple[str, str],
) -> str:
    passenger = order.passengers[0]  # todo: handle multiple passengers when client does
    gender = common.Gender.unknown

    if passenger.gender == models_pb2.Passenger.GENDER_MALE:
        gender = common.Gender.male
    elif passenger.gender == models_pb2.Passenger.GENDER_FEMALE:
        gender = common.Gender.female

    number = phonenumbers.parse(order.contact_details.phone.e164_number)
    country = pycountry.countries.get(
        alpha_2=order.contact_details.address.region_code,
    )

    response = await a2g.create_booking(
        pricing_id=details[0],
        transaction_id=details[1],
        passenger=common.Passenger(
            first_name=passenger.first_name,
            last_name=passenger.last_name,
            name_title=None,
            gender=gender,
            type=criteria.get_passenger_type(
                protobuf.protobuf_to_date(passenger.date_of_birth),
                datetime.date.today(),  # todo: date of travel
            ),
            birth_date=protobuf.protobuf_to_date(passenger.date_of_birth),
        ),
        contact=common.Contact(
            address="\n".join(order.contact_details.address.address_lines),
            city=order.contact_details.address.locality,
            postal_code=order.contact_details.address.postal_code,
            country=common.Country(
                code=country.code,
                name=country.name,
            ),
            phone=common.Phone(
                country_code=str(number.country_code),
                number=str(number.national_number),
            ),
            email=order.contact_details.email,
        ),
    )

    return response.json()
