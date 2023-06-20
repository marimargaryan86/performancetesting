import email_validator
import phonenumbers
from google.protobuf import message

from snowfall.project.junction.plus.service.orders_registration.v1alpha import (
    models_pb2,
)
from snowfall.stdlib.format import protobuf


class ProtobufValidationError(Exception):
    """Raises in case of invalid or missing argument."""


async def validate_orders(
    order: models_pb2.IncomingOrder,
) -> None:
    errors = await validate_completeness(order)
    email_error = await validate_email(order.contact_details.email)
    phone_error = await validate_phone(order.contact_details.phone.e164_number)
    if email_error:
        errors.append(email_error)
    if phone_error:
        errors.append(phone_error)
    if errors:
        raise ExceptionGroup(
            "ProtobufValidationErrors",
            [ProtobufValidationError(msg) for msg in errors],
        )


async def validate_completeness(  # noqa: WPS231
    model: message.Message,
) -> list[str]:
    errors = []
    for field in model.DESCRIPTOR.fields:
        field_value = getattr(model, field.name)
        if field.label == protobuf.descriptor.FieldDescriptor.LABEL_REPEATED:
            if not field_value:
                errors.append("Message '{0}' is missing or unset".format(field.name))
                continue
            for nested_value in field_value:
                if isinstance(nested_value, protobuf.message.Message):
                    errors.extend(await validate_completeness(nested_value))
        elif field.message_type:
            errors.extend(await validate_completeness(field_value))
        elif field_value == "":
            errors.append("Field '{0}' is missing or unset".format(field.name))
    return errors


async def validate_email(
    email: str,
) -> str:
    try:
        email_validator.validate_email(
            email=email,
            check_deliverability=False,
        )
    except email_validator.EmailSyntaxError as err:
        return str(err)
    return ""


async def validate_phone(
    phone_number: str,
) -> str:
    try:
        phone = phonenumbers.parse(phone_number, None)
    except phonenumbers.NumberParseException as err:
        return str(err)
    if not phonenumbers.is_valid_number(phone):
        return "Invalid phone number"
    return ""
