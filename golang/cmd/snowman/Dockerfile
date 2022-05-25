FROM golang:1.18 AS build
WORKDIR /build
COPY golang/go.mod golang/go.sum /build/
RUN go mod download
COPY golang/ /build/
RUN go build -trimpath -ldflags "-s -w" -o snowman cmd/snowman/*.go

# hadolint ignore=DL3006
FROM gcr.io/distroless/base AS runtime
COPY --from=build /build/snowman /bin/snowman
ARG VERSION "dev"
ENV VERSION $VERSION
LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION
ENTRYPOINT ["/bin/snowman"]
