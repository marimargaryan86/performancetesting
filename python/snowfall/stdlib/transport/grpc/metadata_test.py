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
        (("authentication", "foo"),),
        [["authentication", "foo"]],
        (("foo", "bar"), ("authentication", "foo")),
        [["foo", "bar"], ["authentication", "foo"]],
    ],
)
async def test_token_can_be_retrieved(context_metadata: Any) -> None:
    context = mock.create_autospec(aio.ServicerContext)
    context.invocation_metadata = mock.Mock(return_value=context_metadata)
    context.abort = mock.Mock(side_effect=_AbortError)

    assert await metadata.get_auth_token(context)
