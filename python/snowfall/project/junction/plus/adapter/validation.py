from collections.abc import Sequence
from typing import Any

from google.protobuf import descriptor, message


class ProtobufValidationError(Exception):
    """Raises in case of invalid or missing argument."""


def validate_completeness(
    model: message.Message,
) -> list[str]:
    errors = []
    one_of_list_to_skip = _get_one_of_unused_fields(model)
    descriptor_fields = _get_descriptor_fields(
        model.DESCRIPTOR.fields,
        one_of_list_to_skip,
    )

    for field in descriptor_fields:
        field_value = getattr(model, field.name)
        errors.extend(_validate_field(field, field_value))

    return errors


def _validate_field(field: descriptor.FieldDescriptor, field_value: Any) -> list[str]:
    if field.label == descriptor.FieldDescriptor.LABEL_REPEATED:
        if not field_value:
            return ["Message '{0}' is missing or unset".format(field.name)]

        errors = []

        for nested_value in field_value:
            if isinstance(nested_value, message.Message):
                errors.extend(validate_completeness(nested_value))

        return errors

    if field.message_type:
        return validate_completeness(field_value)

    if field_value == "":
        return ["Field '{0}' is missing or unset".format(field.name)]

    return []


def _get_one_of_unused_fields(
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


def _get_descriptor_fields(
    fields: Sequence[descriptor.FieldDescriptor],
    fields_to_skip: Sequence[str],
) -> list[descriptor.FieldDescriptor]:
    return [field for field in fields if field.name not in fields_to_skip]


def get_whatsapp_number(field: str) -> str:
    field_array = field.split("whatsapp:")
    if len(field_array) == 2:
        return field_array[1]
    raise RuntimeError("Wrong format for whatsapp number: {0}".format(field))


def validate_search_url_template(
    search_url_template: str | None,
) -> None:
    dynamic_fields = ["{origin}", "{destination}", "{day}", "{month}", "{year}"]
    if not search_url_template:
        raise ValueError("Search URL template should not be empty")
    if not any(  # noqa: WPS337
        dynamic_field in search_url_template for dynamic_field in dynamic_fields
    ):
        raise ValueError(
            "Missing field, must have dynamic fields: {0}".format(
                ",".join(dynamic_fields),
            ),
        )
    try:
        search_url_template.format(
            origin="origin",
            destination="destination",
            day="11",
            month="11",
            year="2011",
        )
    except LookupError as err:
        raise ValueError("Template is not formattable") from err
