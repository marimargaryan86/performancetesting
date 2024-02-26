import copy
from unittest import mock

import aiofiles
import aiosmtplib
import pytest
from jinja2 import Template

from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.transport.smtp import notifications

_TEST_ID = "123"
_MOCK_NOTIFICATION_SUBJECT = "Mock Notification: {test_id}"
_MOCK_HTML_TEMPLATE_PATH = "snowfall.stdlib.transport.smtp.html_templates"
_MOCK_HTML_TEMPLATE_RESOURCE = "mock_template.html"
_MOCK_NOTIFICATION_TEMPLATE = """
Mock Notification

Test ID: {test_id}
"""


class MockNotification(notifications.Notification):
    _template = _MOCK_NOTIFICATION_TEMPLATE

    def __init__(self, test_id: str = _TEST_ID) -> None:
        self._test_id = test_id

    @property
    def subject(self) -> str:
        return "Mock Notification: {test_id}".format(test_id=self._test_id)

    @property
    def template_parameters(self) -> dict[str, str]:
        return {"test_id": self._test_id}


class MockHtmlNotification(notifications.HtmlNotification):
    _template_path = _MOCK_HTML_TEMPLATE_PATH
    _template_resource = _MOCK_HTML_TEMPLATE_RESOURCE

    def __init__(self, test_id: str = _TEST_ID) -> None:
        self._test_id = test_id

    @property
    def subject(self) -> str:
        return "Mock Notification: {test_id}".format(test_id=self._test_id)

    @property
    def template_parameters(self) -> dict[str, str]:
        return {"test_id": self._test_id}


@pytest.fixture()
def mock_notification() -> MockNotification:
    return MockNotification()


@pytest.fixture()
def mock_html_notification() -> MockHtmlNotification:
    return MockHtmlNotification()


@pytest.fixture()
async def mock_smtp_client() -> mock.AsyncMock:
    mock_client = mock.create_autospec(aiosmtplib.SMTP)
    mock_client.send_message = mock.AsyncMock(return_value=({}, "OK"))
    return mock_client


@pytest.fixture()
async def mock_smtp_error_client() -> mock.AsyncMock:
    mock_client = mock.create_autospec(aiosmtplib.SMTP)
    mock_client.send_message = mock.AsyncMock(side_effect=ValueError())
    return mock_client


@pytest.fixture()
async def smtp_notifier(
    mock_smtp_client: aiosmtplib.SMTP,
) -> notifications.SmtpNotifier:
    return notifications.SmtpNotifier(
        smtp_client=mock_smtp_client,
        sender="sender@email.com",
        recipient="recipient@email.com",
    )


class TestNotification(object):
    async def test_notification_body(self, mock_notification: MockNotification) -> None:
        expected_body = (
            copy.copy(_MOCK_NOTIFICATION_TEMPLATE).strip().format(test_id=_TEST_ID)
        )
        assert mock_notification.body == expected_body

    async def test_notification_subject(
        self,
        mock_notification: MockNotification,
    ) -> None:
        assert mock_notification.subject == _MOCK_NOTIFICATION_SUBJECT.format(
            test_id=_TEST_ID,
        )


class TestHtmlNotification(object):
    async def test_html_notification_body(
        self,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        async with aiofiles.open(
            filesystem.resource_path(
                _MOCK_HTML_TEMPLATE_PATH,
                _MOCK_HTML_TEMPLATE_RESOURCE,
            ),
        ) as template_file:
            template = Template(await template_file.read())

        body = await mock_html_notification.body

        assert body == template.render(test_id=_TEST_ID)

    async def test_html_notification_subject(
        self,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        assert mock_html_notification.subject == _MOCK_NOTIFICATION_SUBJECT.format(
            test_id=_TEST_ID,
        )


class TestSmtpNotifier(object):
    async def test_smtp_notifier_send_no_sender_failure(
        self,
        mock_smtp_client: mock.AsyncMock,
        mock_notification: MockNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_client,
            recipient="recipient@email.com",
        )

        with pytest.raises(ValueError, match="A sender must be specified!"):
            await smtp_notifier.send(mock_notification)

    async def test_smtp_notifier_send_no_recipient_failure(
        self,
        mock_smtp_client: mock.AsyncMock,
        mock_notification: MockNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_client,
            sender="sender@email.com",
        )

        with pytest.raises(ValueError, match="A recipient must be specified!"):
            await smtp_notifier.send(mock_notification)

    async def test_smtp_notifier_send(
        self,
        smtp_notifier: notifications.SmtpNotifier,
        mock_smtp_client: mock.AsyncMock,
        mock_notification: MockNotification,
    ) -> None:
        await smtp_notifier.send(mock_notification)

        mock_smtp_client.send_message.assert_called_once()

    async def test_smtp_notifier_send_failure(
        self,
        mock_smtp_error_client: mock.AsyncMock,
        mock_notification: MockNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_error_client,
            sender="sender@email.com",
            recipient="recipient@email.com",
        )

        with pytest.raises(notifications.NotificationError):
            await smtp_notifier.send(mock_notification)

    async def test_smtp_notifier_send_with_attachment(
        self,
        smtp_notifier: notifications.SmtpNotifier,
        mock_smtp_client: mock.AsyncMock,
        mock_notification: MockNotification,
    ) -> None:
        attachment = notifications.Attachment(
            payload="",
            main_type="",
            sub_type="",
            file_name="",
        )
        await smtp_notifier.send(mock_notification, attachment=attachment)

        mock_smtp_client.send_message.assert_called_once()

    async def test_smtp_notifier_send_html(
        self,
        smtp_notifier: notifications.SmtpNotifier,
        mock_smtp_client: mock.AsyncMock,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        await smtp_notifier.send_html(mock_html_notification)

        mock_smtp_client.send_message.assert_called_once()

    async def test_smtp_notifier_send_html_failure(
        self,
        mock_smtp_error_client: mock.AsyncMock,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_error_client,
            sender="sender@email.com",
            recipient="recipient@email.com",
        )

        with pytest.raises(notifications.NotificationError):
            await smtp_notifier.send_html(mock_html_notification)

    async def test_smtp_notifier_send_html_no_sender_failure(
        self,
        mock_smtp_client: mock.AsyncMock,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_client,
            recipient="recipient@email.com",
        )

        with pytest.raises(ValueError, match="A sender must be specified!"):
            await smtp_notifier.send_html(mock_html_notification)

    async def test_smtp_notifier_send_html_no_recipient_failure(
        self,
        mock_smtp_client: mock.AsyncMock,
        mock_html_notification: MockHtmlNotification,
    ) -> None:
        smtp_notifier = notifications.SmtpNotifier(
            smtp_client=mock_smtp_client,
            sender="sender@email.com",
        )

        with pytest.raises(ValueError, match="A recipient must be specified!"):
            await smtp_notifier.send_html(mock_html_notification)
