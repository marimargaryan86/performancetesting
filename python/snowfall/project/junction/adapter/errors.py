from typing import Awaitable, TypeVar

from google.protobuf import message
from google.rpc import error_details_pb2
from grpc import aio

from snowfall.stdlib.transport.grpc import rich_status

Proto = TypeVar("Proto", bound=message.Message)


class CursorError(Exception):
    """Raised when a cursor is invalid."""


async def handle_grpc_errors(grpc_request: Awaitable[Proto]) -> Proto:
    try:
        return await grpc_request
    except aio.AioRpcError as err:
        for status in rich_status.iter_rich_statuses(err):
            if isinstance(status, error_details_pb2.BadRequest):
                _handle_bad_request(status, err)

        raise


def _handle_bad_request(
    status: error_details_pb2.BadRequest,
    err: aio.AioRpcError,
) -> None:
    for violation in status.field_violations:
        if violation.field == "page_token":
            raise CursorError(violation.description) from err
