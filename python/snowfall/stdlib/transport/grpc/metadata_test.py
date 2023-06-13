from collections.abc import Callable
from typing import Any
from unittest import mock

import pytest
from google.protobuf import message
from grpc import aio

from snowfall.stdlib.transport.grpc import metadata


class _AbortError(Exception):
    """Error to use in mocked methods."""


@pytest.mark.parametrize(
    "context_metadata",
    [
        None,
        (),
        [],
        (("foo", "bar"),),
        [["foo", "bar"]],
    ],
)
async def test_missing_token_raises_error(context_metadata: Any) -> None:
    context = mock.create_autospec(aio.ServicerContext)
    context.invocation_metadata = mock.Mock(return_value=context_metadata)
    context.abort = mock.Mock(side_effect=_AbortError)

    with pytest.raises(_AbortError):
        await metadata.get_auth_token(context)


@pytest.mark.parametrize(
    "context_metadata",
    [
        (
            (
                "authentication",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJzaW9uIjoiMS4wIiwiY2xpZW50X2lkIjoiSm9obiBEb2UifQ.BfpxXHdHJ2R0kVQonNMrY2-D7M7lxNp7YQ7ejwlrpiZU4V9IN4zFdpqyVzIhAr_QTyrdaTaHqjCrF_hh58uLGMxWfmQlPP8e20oP8bFfAMuqqZSAvIyO2wuxmSsv8h2MmSbOPK05alCaz4vyJ2xS0KbJOREFY7AcRPtfiKtlME1EODDxqfWDhblwRF1Geee5UHj-8NqVW0J6oVHpOZ-ont6wbn4zO-LF0ciyd4q73gDhnyykESUTYPbbwWiXhvLQam67ieItL0NVbmf83GHFIIa07aAobcaZi1fA48LGQFJUH1Zrx1n5veV1-RCTXYo6QltWow3PZw4LuIIp_puajA",
            ),
        ),
        [
            [
                "authentication",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJzaW9uIjoiMS4wIiwiY2xpZW50X2lkIjoiSm9obiBEb2UifQ.BfpxXHdHJ2R0kVQonNMrY2-D7M7lxNp7YQ7ejwlrpiZU4V9IN4zFdpqyVzIhAr_QTyrdaTaHqjCrF_hh58uLGMxWfmQlPP8e20oP8bFfAMuqqZSAvIyO2wuxmSsv8h2MmSbOPK05alCaz4vyJ2xS0KbJOREFY7AcRPtfiKtlME1EODDxqfWDhblwRF1Geee5UHj-8NqVW0J6oVHpOZ-ont6wbn4zO-LF0ciyd4q73gDhnyykESUTYPbbwWiXhvLQam67ieItL0NVbmf83GHFIIa07aAobcaZi1fA48LGQFJUH1Zrx1n5veV1-RCTXYo6QltWow3PZw4LuIIp_puajA",
            ],
        ],
        (
            ("foo", "bar"),
            (
                "authentication",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJzaW9uIjoiMS4wIiwiY2xpZW50X2lkIjoiSm9obiBEb2UifQ.BfpxXHdHJ2R0kVQonNMrY2-D7M7lxNp7YQ7ejwlrpiZU4V9IN4zFdpqyVzIhAr_QTyrdaTaHqjCrF_hh58uLGMxWfmQlPP8e20oP8bFfAMuqqZSAvIyO2wuxmSsv8h2MmSbOPK05alCaz4vyJ2xS0KbJOREFY7AcRPtfiKtlME1EODDxqfWDhblwRF1Geee5UHj-8NqVW0J6oVHpOZ-ont6wbn4zO-LF0ciyd4q73gDhnyykESUTYPbbwWiXhvLQam67ieItL0NVbmf83GHFIIa07aAobcaZi1fA48LGQFJUH1Zrx1n5veV1-RCTXYo6QltWow3PZw4LuIIp_puajA",
            ),
        ),
        [
            ["foo", "bar"],
            [
                "authentication",
                "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJzaW9uIjoiMS4wIiwiY2xpZW50X2lkIjoiSm9obiBEb2UifQ.BfpxXHdHJ2R0kVQonNMrY2-D7M7lxNp7YQ7ejwlrpiZU4V9IN4zFdpqyVzIhAr_QTyrdaTaHqjCrF_hh58uLGMxWfmQlPP8e20oP8bFfAMuqqZSAvIyO2wuxmSsv8h2MmSbOPK05alCaz4vyJ2xS0KbJOREFY7AcRPtfiKtlME1EODDxqfWDhblwRF1Geee5UHj-8NqVW0J6oVHpOZ-ont6wbn4zO-LF0ciyd4q73gDhnyykESUTYPbbwWiXhvLQam67ieItL0NVbmf83GHFIIa07aAobcaZi1fA48LGQFJUH1Zrx1n5veV1-RCTXYo6QltWow3PZw4LuIIp_puajA",
            ],
        ],
    ],
)
async def test_token_can_be_retrieved(context_metadata: Any) -> None:
    context = mock.create_autospec(aio.ServicerContext)
    context.invocation_metadata = mock.Mock(return_value=context_metadata)
    context.abort = mock.Mock(side_effect=_AbortError)

    token = await metadata.get_auth_token(context)
    assert token["client_id"] == "John Doe"


class TestInterceptor(object):
    _interceptor = metadata.MetadataContextClientInterceptor()
    _continuation = mock.AsyncMock(
        Callable[[aio.ClientCallDetails, message.Message], aio.UnaryUnaryCall],
    )
    _request = mock.Mock(spec=message.Message)

    async def test_interceptor_works_without_context(self) -> None:
        client_call_details = mock.create_autospec(spec=aio.ClientCallDetails)
        client_call_details.metadata = mock.create_autospec(spec=aio.Metadata)

        await self._interceptor.intercept_unary_unary(
            continuation=self._continuation,
            client_call_details=client_call_details,
            request=self._request,
        )

        client_call_details.metadata.add.assert_not_called()

    async def test_interceptor_works_with_context(self) -> None:
        client_call_details = mock.create_autospec(spec=aio.ClientCallDetails)
        client_call_details.metadata = mock.create_autospec(spec=aio.Metadata)

        mock_context = "foo"

        with metadata.auth_context(mock_context):
            await self._interceptor.intercept_unary_unary(
                continuation=self._continuation,
                client_call_details=client_call_details,
                request=self._request,
            )

        client_call_details.metadata.add.assert_called_once_with(mock.ANY, mock_context)
