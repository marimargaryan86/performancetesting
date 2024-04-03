import contextlib
import dataclasses
import datetime
from collections.abc import Awaitable, Callable, Iterator
from typing import Generic, TypeVar

import grpc_testing
import pytest
from google.protobuf import message, symbol_database
from google.rpc import status_pb2
from grpc import RpcError, StatusCode, aio

from snowfall.stdlib.transport.grpc import service

_Request = TypeVar("_Request", bound=message.Message)
_Response = TypeVar("_Response", bound=message.Message)
_Server = TypeVar("_Server", bound=service.Service)
_Method = Callable[
    [_Server, _Request, aio.ServicerContext[_Request, _Response]],
    Awaitable[_Response],
]


@dataclasses.dataclass(frozen=True)
class Response(Generic[_Response]):
    code: StatusCode
    details: str
    message: _Response
    trailing_metadata: aio.Metadata


class ServerTester:
    _pool = symbol_database.Default().pool

    def __init__(self, srv: _Server) -> None:
        self._service = self._pool.FindServiceByName(srv.get_name())
        self._server = grpc_testing.server_from_dictionary(
            {
                self._service: srv,
            },
            grpc_testing.strict_real_time(),
        )

    async def invoke_unary_unary(
        self,
        method: _Method[_Server, _Request, _Response],
        request: _Request,
        metadata: aio.Metadata | None = None,
        timeout: datetime.timedelta | None = None,
    ) -> Response[_Response]:
        rpc = self._server.invoke_unary_unary(
            self._service.FindMethodByName(method.__name__),
            metadata or aio.Metadata(),
            request,
            timeout.total_seconds() if timeout else 1,
        )

        rpc.initial_metadata()

        callback, trailing_metadata, code, details = rpc.termination()

        return Response(
            code=code,
            details=details,
            message=(await callback),
            trailing_metadata=trailing_metadata,
        )


class AbortError(RpcError):
    def __init__(
        self,
        code: StatusCode,
        details: str | None,
        trailing_metadata: tuple[tuple[str, str], ...] | None,
    ):
        self.code = code
        self.details = details
        self.trailing_metadata = trailing_metadata


class _Aborted:
    def __init__(self) -> None:
        self.error = message.Message()
        self.rich_status = message.Message()


def _detail_from_trailing_metadata(
    trailing_metadata: tuple[tuple[str, str], ...],
) -> message.Message:
    status = status_pb2.Status.FromString(trailing_metadata[0][1])
    detail = status.details[0]
    detail_type = symbol_database.Default().GetSymbol(detail.TypeName())
    unpacked = detail_type()
    detail.Unpack(unpacked)

    return unpacked


@contextlib.contextmanager
def assert_aborted(error_code: StatusCode) -> Iterator[_Aborted]:
    aborted = _Aborted()

    with pytest.raises(AbortError) as exc_info:
        yield aborted

    exc_value = exc_info.value  # noqa: WPS441

    assert exc_value.code == error_code
    aborted.error = exc_value

    if exc_value.trailing_metadata:
        aborted.rich_status = _detail_from_trailing_metadata(
            exc_value.trailing_metadata,
        )
