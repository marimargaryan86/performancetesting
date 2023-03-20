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
        aio.Metadata(),
        aio.Metadata(("foo", "bar")),
    ],
)
async def test_missing_token_raises_error(context_metadata: Any) -> None:
    context = mock.create_autospec(aio.ServicerContext)
    context.invocation_metadata = mock.Mock(return_value=context_metadata)
    context.abort = mock.Mock(side_effect=_AbortError)

    with pytest.raises(_AbortError):
        await metadata.get_auth_token(context)


async def test_token_can_be_retrieved() -> None:
    expected_auth = "foobar"
    expected_metadata = aio.Metadata(("authentication", expected_auth))
    context = mock.create_autospec(aio.ServicerContext)
    context.invocation_metadata = mock.Mock(return_value=expected_metadata)
    context.abort = mock.Mock(side_effect=_AbortError)

    assert await metadata.get_auth_token(context) == expected_auth
