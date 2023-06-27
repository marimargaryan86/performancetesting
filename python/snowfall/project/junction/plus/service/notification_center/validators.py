from snowfall.project.junction.plus.adapter import validation
from snowfall.project.junction.plus.service.notification_center.v1alpha import amqp_pb2


def validate_notifications(
    notification: amqp_pb2.NotificationEvent,
) -> None:
    errors = validation.validate_completeness(notification)
    if errors:
        raise ExceptionGroup(
            "ProtobufValidationErrors",
            [validation.ProtobufValidationError(msg) for msg in errors],
        )
