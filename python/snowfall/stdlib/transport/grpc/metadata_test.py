from typing import Any
from unittest import mock

import pytest
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
