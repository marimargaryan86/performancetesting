ARG REGISTRY
FROM ${REGISTRY}golang:1.18 AS build
WORKDIR /build
COPY golang/go.mod golang/go.sum /build/
RUN go mod download
COPY golang/ /build/
RUN go build -trimpath -ldflags "-s -w" -o gtfs-import cmd/gtfs-import/*.go

# hadolint ignore=DL3006
FROM gcr.io/distroless/base AS runtime
COPY --from=build /build/gtfs-import /bin/gtfs-import
ARG VERSION "dev"
ENV VERSION $VERSION
LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION
ENTRYPOINT ["/bin/gtfs-import"]
