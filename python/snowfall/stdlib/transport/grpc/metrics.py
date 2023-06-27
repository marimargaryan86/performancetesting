import time
from collections.abc import Callable
from types import MappingProxyType

import prometheus_client
from google.protobuf.message import Message
from grpc import StatusCode, aio

from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.transport.grpc import interceptor


class MetricsClientInterceptor(aio.UnaryUnaryClientInterceptor):
    _failed = prometheus_client.Counter(
        "grpc_client_failed_requests_total",
        "Total number of failed sent gRPC requests",
        ["rpc"],
    )

    _histogram = prometheus_client.Histogram(
        "grpc_client_request_duration_seconds",
        "Duration of sent gRPC requests in seconds",
        ["rpc", "status"],
        buckets=prometheus.BUCKETS,
    )

    _total = prometheus_client.Counter(
        "grpc_client_requests_total",
        "Total number of sent gRPC requests",
        ["rpc", "status"],
    )

    async def intercept_unary_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> aio.UnaryUnaryCall | Message:
        start = time.perf_counter()
        rpc_name = bytes(client_call_details.method).decode()
        response = await continuation(
            client_call_details,
            request,
        )

        code = await response.code()

        self._total.labels(
            rpc=rpc_name,
            status=code.name,
        ).inc()

        if code != StatusCode.OK:
            self._failed.labels(rpc=rpc_name).inc()

        self._histogram.labels(
            rpc=rpc_name,
            status=code.name,
        ).observe(time.perf_counter() - start)

        return response


class MetricsServerInterceptor(interceptor.ServerInterceptor):
    _failed = prometheus_client.Counter(
        "grpc_server_failed_requests_total",
        "Total number of failed received gRPC requests",
        ["rpc"],
    )

    _histogram = prometheus_client.Histogram(
        "grpc_server_request_duration_seconds",
        "Duration of received gRPC requests in seconds",
        ["rpc", "status"],
        buckets=prometheus.BUCKETS,
    )

    _total = prometheus_client.Counter(
        "grpc_server_requests_total",
        "Total number of received gRPC requests",
        ["rpc", "status"],
    )

    _status_codes: MappingProxyType[int, StatusCode] = MappingProxyType(
        {status_code.value[0]: status_code for status_code in StatusCode},
    )

    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: Message,
        context: aio.ServicerContext,
    ) -> Message:
        start = time.perf_counter()
        rpc_name = continuation.__name__

        try:
            return await continuation(request, context)
        except Exception:
            context.set_code(StatusCode.UNKNOWN)
            raise
        finally:
            status_code = self._status_codes[context.code()]

            self._total.labels(
                rpc=rpc_name,
                status=status_code.name,
            ).inc()

            if status_code != StatusCode.OK:
                self._failed.labels(rpc=rpc_name).inc()

            self._histogram.labels(
                rpc=rpc_name,
                status=status_code.name,
            ).observe(time.perf_counter() - start)
