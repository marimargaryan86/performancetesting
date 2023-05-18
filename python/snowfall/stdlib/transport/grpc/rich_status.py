from typing import Awaitable, Iterator, NoReturn, cast

import grpc
from google.protobuf import any_pb2, message, symbol_database
from google.rpc import error_details_pb2, status_pb2
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


def build_rich_status(
    code: grpc.StatusCode,
    error: message.Message,
    description: str | None = None,
) -> status_pb2.Status:
    detail = any_pb2.Any()
    detail.Pack(error)
    return status_pb2.Status(
        code=code.value[0],
        message=description,
        details=[detail],
    )


def build_bad_request(
    field_name: str,
    field_description: str,
    description: str | None = None,
) -> status_pb2.Status:
    return build_rich_status(
        code=grpc.StatusCode.INVALID_ARGUMENT,
        error=error_details_pb2.BadRequest(
            field_violations=[
                error_details_pb2.BadRequest.FieldViolation(
                    field=field_name,
                    description=field_description,
                ),
            ],
        ),
        description=description,
    )


def build_precondition_failure(
    subject: str,
    description: str,
) -> status_pb2.Status:
    return build_rich_status(
        code=grpc.StatusCode.FAILED_PRECONDITION,
        error=error_details_pb2.PreconditionFailure(
            violations=[
                error_details_pb2.PreconditionFailure.Violation(
                    type="logical",
                    subject=subject,
                    description=description,
                ),
            ],
        ),
        description=description,
    )


async def abort_with_rich_status(
    context: grpc.aio.ServicerContext,
    status: status_pb2.Status,
) -> NoReturn:
    rich_status = rpc_status.to_status(status)

    await cast(
        Awaitable[NoReturn],
        context.abort(
            code=rich_status.code,
            details=rich_status.details,
            trailing_metadata=rich_status.trailing_metadata,
        ),
    )
