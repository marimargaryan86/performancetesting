import abc
import time
from collections.abc import Callable
from types import MappingProxyType

import prometheus_client
from google.protobuf.message import Message
from grpc import StatusCode, aio

from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.transport.grpc import interceptor


class _MetricsInterceptor(abc.ABC):
    _failed: prometheus_client.Counter
    _histogram: prometheus_client.Histogram
    _total: prometheus_client.Counter
    _request_bytes: prometheus_client.Histogram
    _response_bytes: prometheus_client.Histogram

    def _log_metrics(
        self,
        rpc_name: str,
        status_code: StatusCode,
        request: Message,
        response: Message | None,
        start: float,
    ) -> None:
        self._total.labels(
            rpc=rpc_name,
            status=status_code.name,
        ).inc()

        if status_code != StatusCode.OK:
            self._failed.labels(rpc=rpc_name).inc()

        self._request_bytes.labels(
            rpc=rpc_name,
            status=status_code.name,
        ).observe(request.ByteSize())

        if response:
            self._response_bytes.labels(
                rpc=rpc_name,
                status=status_code.name,
            ).observe(response.ByteSize())

        self._histogram.labels(
            rpc=rpc_name,
            status=status_code.name,
        ).observe(time.perf_counter() - start)


class MetricsClientInterceptor(aio.UnaryUnaryClientInterceptor, _MetricsInterceptor):
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

    _request_bytes = prometheus_client.Histogram(
        "grpc_client_requests_bytes",
        "Byte length of received gRPC requests",
        ["rpc", "status"],
        buckets=prometheus.BYTE_BUCKETS,
    )

    _response_bytes = prometheus_client.Histogram(
        "grpc_client_responses_bytes",
        "Byte length of received gRPC responses",
        ["rpc", "status"],
        buckets=prometheus.BYTE_BUCKETS,
    )

    async def intercept_unary_unary(
        self,
        continuation: Callable[[aio.ClientCallDetails, Message], aio.UnaryUnaryCall],
        client_call_details: aio.ClientCallDetails,
        request: Message,
    ) -> aio.UnaryUnaryCall | Message:
        start = time.perf_counter()
        response = await continuation(
            client_call_details,
            request,
        )

        self._log_metrics(
            rpc_name=bytes(client_call_details.method).decode(),
            status_code=await response.code(),
            request=request,
            response=response,
            start=start,
        )

        return response


class MetricsServerInterceptor(interceptor.ServerInterceptor, _MetricsInterceptor):
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

    _request_bytes = prometheus_client.Histogram(
        "grpc_server_requests_bytes",
        "Byte length of received gRPC requests",
        ["rpc", "status"],
        buckets=prometheus.BYTE_BUCKETS,
    )

    _response_bytes = prometheus_client.Histogram(
        "grpc_server_responses_bytes",
        "Byte length of received gRPC responses",
        ["rpc", "status"],
        buckets=prometheus.BYTE_BUCKETS,
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
        response = None

        try:
            response = await continuation(request, context)
        except Exception:
            context.set_code(StatusCode.UNKNOWN)
            raise
        else:
            return response
        finally:
            self._log_metrics(
                rpc_name=continuation.__name__,
                status_code=self._status_codes[context.code()],
                request=request,
                response=response,
                start=start,
            )
