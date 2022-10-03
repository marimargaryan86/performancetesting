# python:3.10.5-slim-bullseye
ARG REGISTRY
FROM ${REGISTRY}python@sha256:df9e675c0f6f0f758f7d49ea1b4e12cf7b8688d78df7d9986085fa0f24933ade AS runtime

ENV PIP_NO_CACHE_DIR "false"
ENV PYTHONFAULTHANDLER 1
ENV PYTHONHASHSEED "random"
ENV PYTHONUNBUFFERED 1

COPY python.snowfall.project.pay.service.payers/main.pex /bin/payers

ARG VERSION "dev"
ENV VERSION $VERSION

LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION

RUN /bin/payers --help

ENTRYPOINT ["/bin/payers"]
