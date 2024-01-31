import pytest

from snowfall.project.junction.plus.service.notification_center import importer
from snowfall.project.junction.plus.service.notifications.v1 import models_pb2
from snowfall.stdlib.transport.amqp import types


async def test_notification_event_fail_validation(
    notification_event_importer: importer.NotificationEventImporter,
    invalid_message: types.Message[models_pb2.NotificationEvent],
) -> None:
    with pytest.raises(ExceptionGroup, match="ProtobufValidationErrors"):
        await notification_event_importer._process_message(  # noqa: SLF001
            invalid_message,
        )


async def test_notification_event(
    notification_event_importer: importer.NotificationEventImporter,
    valid_message: types.Message[models_pb2.NotificationEvent],
) -> None:
    await notification_event_importer._process_message(valid_message)  # noqa: SLF001
    assert len(notification_event_importer._channels._channels[2]._sent_messages) == 1  # type: ignore[attr-defined] # noqa: SLF001
