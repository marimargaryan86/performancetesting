FROM python@sha256:fa0de30c61765876263652ebc39325f34f1d918113e0a8b397c8090fc40febd0 AS runtime

ENV PIP_NO_CACHE_DIR "false"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONHASHSEED "random"
ENV PYTHONUNBUFFERED 1

COPY python.snowfall.junction.mobile_api/main.pex /bin/mobile_api

ARG VERSION "dev"
ENV VERSION $VERSION

LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION

ENTRYPOINT ["/bin/mobile_api"]
