from collections.abc import Sequence

import email_validator
import phonenumbers
from google.protobuf import descriptor, message

from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2


class ProtobufValidationError(Exception):
    """Raises in case of invalid or missing argument."""


async def validate_orders(
    order: amqp_pb2.IncomingOrder,
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


async def get_one_of_unused_fields(  # noqa: WPS210
    model: message.Message,
) -> list[str]:
    fields_to_skip = []
    for field in model.DESCRIPTOR.fields:
        if field.containing_oneof:
            one_of_title = field.containing_oneof.name
            one_of_field = model.WhichOneof(one_of_title)
            if one_of_field and field.name != one_of_field:
                fields_to_skip.append(field.name)
    return fields_to_skip


async def get_descriptor_fields(
    fields: Sequence[descriptor.FieldDescriptor],
    fields_to_skip: Sequence[str],
) -> list[descriptor.FieldDescriptor]:
    return [field for field in fields if field.name not in fields_to_skip]


async def validate_completeness(  # noqa: WPS231, WPS210
    model: message.Message,
) -> list[str]:
    errors = []
    one_of_list_to_skip = await get_one_of_unused_fields(model)
    descriptor_fields = await get_descriptor_fields(
        model.DESCRIPTOR.fields,
        one_of_list_to_skip,
    )
    for field in descriptor_fields:
        field_value = getattr(model, field.name)
        if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
            if not field_value:
                errors.append("Message '{0}' is missing or unset".format(field.name))
                continue
            for nested_value in field_value:
                if isinstance(nested_value, message.Message):
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
