FROM python:3.9.9-slim AS runtime

ENV PIP_NO_CACHE_DIR "false"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONHASHSEED "random"
ENV PYTHONUNBUFFERED 1

COPY python.snowfall.junction.echo/main.pex /bin/echo

ARG VERSION "dev"
ENV VERSION $VERSION

LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION

ENTRYPOINT ["/bin/echo"]
