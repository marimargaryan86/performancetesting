import dataclasses
import datetime
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

import grpc_testing
from google.protobuf import message, symbol_database
from grpc import StatusCode, aio

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


class ServerTester(object):
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
