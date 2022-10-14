from typing import Awaitable, Iterator, NoReturn, cast

import grpc
from google.protobuf import any_pb2, message, symbol_database
from google.rpc import status_pb2
from grpc_status import rpc_status

_SYMBOL_DATABASE = symbol_database.Default()


def iter_rich_statuses(
    error: grpc.RpcError,
) -> Iterator[message.Message]:
    status = rpc_status.from_call(error)

    if not status:
        return

    for detail in status.details:
        try:
            detail_type = _SYMBOL_DATABASE.GetSymbol(detail.TypeName())
        except KeyError:
            continue

        error = detail_type()
        detail.Unpack(error)
        yield error


async def abort_with_rich_status(
    context: grpc.aio.ServicerContext,
    code: grpc.StatusCode,
    error: message.Message,
    description: str | None = None,
) -> NoReturn:
    detail = any_pb2.Any()
    detail.Pack(error)
    rich_status = status_pb2.Status(
        code=code.value[0],
        message=description,
        details=[detail],
    )
    status = rpc_status.to_status(rich_status)

    await cast(
        Awaitable[NoReturn],
        context.abort(
            code=status.code,
            details=status.details,
            trailing_metadata=status.trailing_metadata,
        ),
    )
