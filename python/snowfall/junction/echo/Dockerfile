FROM curlimages/curl:7.80.0 AS grpc_health_probe
RUN curl -fsSL "https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.2/grpc_health_probe-linux-amd64" >/tmp/grpc_health_probe && chmod +x /tmp/grpc_health_probe

FROM python:3.9.9-slim AS runtime

ENV PIP_NO_CACHE_DIR "false"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONHASHSEED "random"
ENV PYTHONUNBUFFERED 1

COPY --from=grpc_health_probe /tmp/grpc_health_probe /bin/grpc_health_probe
COPY python.snowfall.junction.echo/main.pex /bin/echo

EXPOSE 50051

ARG VERSION "dev"
ENV VERSION $VERSION

LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION

ENTRYPOINT ["/bin/echo"]
