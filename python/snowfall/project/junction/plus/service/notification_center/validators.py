from snowfall.project.junction.plus.service.notification_center.v1alpha import amqp_pb2
from snowfall.project.junction.plus.service.orders_registration.validators import (
    ProtobufValidationError,
    validate_completeness,
)


async def validate_notifications(
    notification: amqp_pb2.NotificationEvent,
) -> None:
    errors = await validate_completeness(notification)
    if errors:
        raise ExceptionGroup(
            "ProtobufValidationErrors",
            [ProtobufValidationError(msg) for msg in errors],
        )
