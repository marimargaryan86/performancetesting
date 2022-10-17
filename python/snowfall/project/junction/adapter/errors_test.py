from typing import NoReturn

import grpc
import pytest
from grpc_status import rpc_status

from snowfall.project.junction.adapter import errors
from snowfall.stdlib.transport.grpc import rich_status


async def _raise_grpc_bad_request_error(field: str) -> NoReturn:
    status = rpc_status.to_status(
        rich_status.build_bad_request(
            field_name=field,
            field_description="foo",
            description="bar",
        ),
    )
    raise grpc.aio.AioRpcError(
        code=status.code,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=status.trailing_metadata,
        details=status.details,
    )


async def _raise_grpc_error() -> NoReturn:
    raise grpc.aio.AioRpcError(
        code=grpc.StatusCode.UNKNOWN,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )


async def test_cursor_error_is_handled() -> None:
    with pytest.raises(errors.CursorError):
        await errors.handle_grpc_errors(_raise_grpc_bad_request_error("page_token"))


async def test_unknown_field_is_not_handled() -> None:
    with pytest.raises(grpc.aio.AioRpcError):
        await errors.handle_grpc_errors(_raise_grpc_bad_request_error("unknown"))


async def test_unknown_error_is_not_handled() -> None:
    with pytest.raises(grpc.aio.AioRpcError):
        await errors.handle_grpc_errors(_raise_grpc_error())
