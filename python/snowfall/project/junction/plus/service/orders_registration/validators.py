import email_validator
import phonenumbers

from snowfall.project.junction.plus.adapter import validation
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2


def validate_orders(
    order: amqp_pb2.IncomingOrder,
) -> None:
    errors = validation.validate_completeness(order)
    email_error = _validate_email(order.contact_details.email)
    phone_error = _validate_phone(order.contact_details.phone.e164_number)
    if email_error:
        errors.append(email_error)
    if phone_error:
        errors.append(phone_error)
    if errors:
        raise ExceptionGroup(
            "ProtobufValidationErrors",
            [validation.ProtobufValidationError(msg) for msg in errors],
        )


def _validate_email(
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


def _validate_phone(
    phone_number: str,
) -> str:
    try:
        phone = phonenumbers.parse(phone_number, None)
    except phonenumbers.NumberParseException as err:
        return str(err)
    if not phonenumbers.is_valid_number(phone):
        return "Invalid phone number"
    return ""
