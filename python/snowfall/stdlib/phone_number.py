from __future__ import annotations

import phonenumbers

from snowfall.stdlib.v1 import phone_number_pb2


class PhoneNumber(phonenumbers.FrozenPhoneNumber):
    def __init__(self, phone_number: phonenumbers.PhoneNumber):
        super().__init__(phone_number)

        if not phonenumbers.is_valid_number(self):
            raise ValueError("Invalid phone number.")

    def __str__(self) -> str:
        return phonenumbers.format_number(
            numobj=self,
            num_format=phonenumbers.PhoneNumberFormat.RFC3966,
        )

    def protobuf(self) -> phone_number_pb2.PhoneNumber:
        proto = phone_number_pb2.PhoneNumber(
            e164_number=phonenumbers.format_number(
                numobj=self,
                num_format=phonenumbers.PhoneNumberFormat.E164,
            ),
        )

        if self.extension:
            proto.extension = self.extension

        return proto


def from_protobuf(proto: phone_number_pb2.PhoneNumber) -> PhoneNumber:
    match proto.WhichOneof("kind"):
        case "e164_number":
            try:
                internal_obj = phonenumbers.parse(
                    proto.e164_number,
                    region=phonenumbers.UNKNOWN_REGION,
                )
            except phonenumbers.NumberParseException as err:
                raise ValueError("Unable to parse phone number.") from err
        case "short_code":
            raise NotImplementedError
        case _:
            raise ValueError("Unable to parse phone number.")

    if proto.extension:
        internal_obj.extension = proto.extension

    return PhoneNumber(internal_obj)


def from_string(
    phone_number: str,
) -> PhoneNumber:
    try:
        internal_obj = phonenumbers.parse(
            phone_number,
            region=phonenumbers.UNKNOWN_REGION,
        )
    except phonenumbers.NumberParseException as err:
        raise ValueError("Unable to parse phone number.") from err

    return PhoneNumber(internal_obj)
