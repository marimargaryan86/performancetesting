---
sidebar_position: 4
---

# Codebase Deep Dive

The Junction core codebase consists of many moving parts. This page will
contain the explanation of what sits where in the codebase, and how things are
glued together.

## Repository Organization

The repository is structured as a monolith git repository where the source code
is first split by technologies or format (`python`, `golang`, `protobuf`...),
and then by purpose. Here is the explanation of the main project structure:

* `/protobuf` Definitions of all the gRPC services and all gRPC payloads (protobufs).
* `/python/snowfall` Snowfall main python package, all sub packages should be defined here.
  * `/python/snowfall/stdlib` Snowfalls standard library. A home of all
  commonly used abstractions and helper methods.
  * `/python/snowfall/vendor` External dependencies that Snowfall code relies on.
  * `/python/snowfall/project/junction` Base folder for Junction project, contains all Junction-specific code and services.
    * `/python/snowfall/project/junction/go/services` All Junction Go services.
    For example you will find `client_api` (the customer-facing API) and multiple gRPC backends to implement the API (e.g.
    `places`, `offers`, ...).
  * `/python/snowfall/conftest.py` Testing helpers used across multiple Junction services.
* `/openapi/junction/client_api` OpenAPI definition of the `client_api`
* `/vendor` External dependencies explicitly listed for pants, this is where
  the global Python `requirements.txt` lives.

## Junction Services

Most Junction services sit in
[`/python/snowfall/project/junction/go/service`](https://git.snowfall.se/junction/junction/-/tree/main/python/snowfall/project/junction/go/service).

The common practices shared between Junction services are:

1. Naming a folder after the service in
`/python/snowfall/project/junction/go/service` directory.
2. Having a `main.py` file that contains only the settings objects and
dependency injection of needed objects into the function that should run when
given an entry point argument to the `main.py` command. Almost all services have
at least a `grpc` or an `http` entry point, they can have additional ones for
other modes.
3. Having a `grpc.py` file that contains the implementation of the `gRPC`
interface for the service defined in
`/protobuf/snowfall/project/junction/go/service/<service_name>/v1/<service_name>.proto`
4. Having a `<service_name>.py` file that contains the definition of the mongo
collection that will be assigned to that service
5. Having a `.env.dist` file that contains the definitions of all environment
variables required for local development

Below we describe a couple services to illustrate the patterns.

### Resellers

The Reseller service is one of the most simple services we have. In `main.py` at
the bottom of the file, a single entry point is defined:

```python
if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="resellers")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_ServeSettings,
        ),
    )
```

The `grpc` service is defined in
`/protobuf/snowfall/project/junction/go/service/resellers/v1/resellers.proto`:

```protobuf
service ResellerService {
  rpc CreateReseller(CreateResellerRequest) returns (CreateResellerResponse) {}
  rpc GetReseller(GetResellerRequest) returns (GetResellerResponse) {}
  rpc ListResellers(ListResellersRequest) returns (ListResellersResponse) {}
  rpc UpdateReseller(UpdateResellerRequest) returns (UpdateResellerResponse) {}
  rpc PromoteResellerConfig(PromoteResellerConfigRequest) returns (PromoteResellerConfigResponse) {}
}
```

And the service is implemented in
`/python/snowfall/project/junction/go/service/resellers/grpc.py`:

```python
class ResellerService(
    service.Service,
    resellers_pb2_grpc.ResellerServiceServicer,
):
    ...
```

### Places

The places service is another simple service and it follows a very similar
organization. In `main.py` at the bottom of the file, two entry points are
defined:

```python
if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        application.Command(
            name="generate-cities",
            callback=_generate_cities,
            settings_class=_CitiesSettings,
        ),
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
```

The entry points are `grpc` and `generate-cities`. The `grpc` entry point
starts the `_serve` function using the `_GrpcSettings` as context. The
`generate-cities` entry point is a convenient way to run a CLI using internal
logic from the Places service.

The `grpc` service is defined in
`/protobuf/snowfall/project/junction/go/service/places/v1/places.proto`:

```protobuf
service PlacesService {
  rpc GetPlace(GetPlaceRequest) returns (GetPlaceResponse) {}
  rpc ListPlaces(ListPlacesRequest) returns (ListPlacesResponse) {}
  rpc CreatePlace(CreatePlaceRequest) returns (CreatePlaceResponse) {}
  rpc DeletePlace(DeletePlaceRequest) returns (DeletePlaceResponse) {}
  rpc UpdatePlace(UpdatePlaceRequest) returns (UpdatePlaceResponse) {}
  rpc GetPlaceByCoordinate(GetPlaceByCoordinateRequest) returns (GetPlaceByCoordinateResponse) {}
}
```

And the service is implemented in
`/python/snowfall/project/junction/go/service/places/grpc.py`:

```python
class PlacesService(
    service.Service,
    places_pb2_grpc.PlacesServiceServicer
):
    ...
```

The places service is only used by the places adapter defined in the
`/python/snowfall/project/junction/go/adapter/places.py`, and all other
services that want to use the places service use it only through that adapter.

:::info

Note that in newly written code, we are looking to stop using these adapters.
The plan is to use the gRPC stub directly, see [this](
https://git.snowfall.se/junction/junction/-/blob/c6b99eb95996808e0c783ee36087f022bd1d8491/python/snowfall/project/junction/rocket/service/api/multi_modality/routes.py#L44)
for example.

Don't be surprised if you see inconsistencies as we go through this transition.

:::

### Client API

The `Client API` service contains:

* `routes` — directory where all endpoints are defined, `routes/router.py`
contains endpoint mappings to the rest of the files in the directory
* `resources.py` — a file where all endpoint responses are defines and mapped to
from protobuf messages
* `main.py` — contains the definition of the entrypoint and maps the required
arguments to the service
* `bootstrap.py` — contains the `Settings` class which reads environment
variables from `.env.dist` when running Junction locally, or env variables when
Junction is deployed. Also, it contains the `lagom` mappings for dependency
injection. Currently, we only map adapters to singleton objects in the
container mapping.
* `jwt.py` —  adds authentication to starlette
* `...` — the rest of the files are mostly used for testing or helper functions,
e.g. `conftest.py`, `fixtures/`, `*_test.py`
* `.env.dist` — definitions of environment variables used when developing locally

For an endpoint to work properly the bare minimum would be to add a new route
in `client_api/routes/router.py` that when invoked calls a function in class in
a file in `client_api/routes/` directory. If that route handler also needs to
communicate with some grpc service one would have to create an adapter in
`python/snowfall/project/junction/go/adapter/` directory.

### Provider service

"Provider service" is a name for multiple micro-services that are run to
accommodate finding priced offers from providers (e.g. 3rd party APIs) and booking them.

Currently, there are 4 services each provider service runs:

1. grpc
2. offers
3. pricing
4. orders

When the provider services are run the following things happen:

1. the service loads the provider locations (e.g. stations, airports, ports etc) from a file and maps them to places using an h3 mapping

After the `grpc` service publishes an `OfferTask` to the offer searches
queue, The provider `offers` service:

1. consumes an `OfferTask` from the `offer searches` queue
2. converts the `OfferTask` into information that can be used to call the provider API -- `SearchCriteria`
3. publishes the search criteria to the `provider queue`, as a `SearchCriteriaTask`

The provider `offers` service:

1. consumes the `SearchCriteriaTask` from the `provider queue`
2. asks the provider for offers
3. publishes the offers on the `offers queue` for the `offers grpc` service to consume and aggregate it

The provider `pricing` will receive a selected offer option ID (offer choice for a segment of a full trip):

1. consumes the `TripPriceQuoteTask` from the `pricing queue`
2. checks to see if the offer option is available in the provider's cache
3. if so, it will perform a refresh of price, if necessary, move the chosen offer to a quote cache and fetch any other info, e.g. fare rules.
4. publishes the quote on the `pricing results queue`  as a `TripPriceQuoteResult` for the `offers import` service to consume it and add it to the quote container

After the `orders grpc` service publishes to the place order queue, The
provider `orders` service:

1. consumes from the place orders queue
2. asks the provider to book the offer
3. publishes the result to the orders result queue
