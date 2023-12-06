# Trip Service

This is what provides the results that power the route based trip search.
Always start with the most basic functionality, the one way trip search.

To register this implementation, just provide some additional information in
the`bootstrap.ProviderConfiguration` in the `_factory` function, by
providing a `bootstrap.TripSearchImplementation`. Here we have to make some
decisions based on what suits us best for this provider.

## Trip search capabilities

More information about the following options is available in the
`protobuf/snowfall/project/junction/provider/v2alpha/meta.proto` file.

### Stop identification method

`stop_identification_method` tells Junction Go what type of stop identifiers
to provide in the requests to most easily find good results.

There are currently three different options to choose from:
* IATA codes, which is best for air travel providers
* Coordinates, which just gives the coordinates of the stops
* Provider IDs, which would give the custom identifiers that a provider uses

:::warning

The last option, provider IDs, is currently not going to work at all until
the new route service and some additional provider interfaces have been
implemented, because Junction Go can't determine these without additional
information.

:::

### Passenger identification method

`passenger_age_identification_method` tells Junction Go how the service
would like to receive information about passengers.

There are only two options to choose from:
* Date of birth, which gives the most granular information about passengers
* Provider types, which would give a text representation of the provider's own type

:::warning

The second option, provider types, is currently not available, as it requires another service
to be implemented, so Junction Go can figure out how to map between its
internal types and the provider types.

:::

### Supported segment types

`supported_segment_types` tells Junction Go which segment types the provider
can return results for. This allows Junction Go to entirely skip searching
in certain providers if it knows that it is looking for results for only
certain segment types, so it won't make unnecessary requests.

## Trip searcher

This is where the magic happens. Always start with implementing one way searches,
as this is the minimum functionality that needs to be available.

Unless there are any benefits of doing roundtrip searches, like receiving a single ticket for both trips,
getting a reduced price or performance reasons, there is no point in adding support
for roundtrip, as Junction Go will split roundtrip searches into two oneway searches
when communicating with the provider integration services.

Multi-city searches is something that is usually only available for air providers
and is the last thing that should be implemented.

:::warning Important

Low response times for a provider is extremely important. If searches take too long or errors occur,
the provider service might be automatically flagged as unhealthy by Junction and switched off.

10 seconds is the maximum allowed response time, but sub-second responses are preferred.

:::

### Interface

All trip search implementations receive a `NamedTuple` with its particular request type
and passengers. Each passenger will contain information according to the `passenger_age_identification_method` specified.
The request will contain one or multiple criteria (depending on the search mode)
that each contain a travel date, along with an origin and destination pair in the format specified by `stop_identification_method`.

Responses should contain a list of results, each containing trips and price information.
Each result corresponds to one offer, in the old way of returning results,
which means that if a provider says you can travel from point A to point B at time X in three different fare classes,
it will mean three different results.

## Putting it all together

Along with the previously mentioned options, we have to provide a callable
that will return results for the specific search mode:

```python title="/python/snowfall/projects/junction/content/service/provider_name/main.py"
import uuid

from snowfall.project.junction.content.service.provider_name import trips
from snowfall.project.junction.content import bootstrap
from snowfall.project.junction.provider.v2alpha import meta_pb2
from snowfall.project.junction.v1 import segment_type_pb2

async def _factory(
    app: bootstrap.Application[bootstrap.Settings],
) -> bootstrap.ProviderConfiguration:
    trip_searcher = trips.TripsSearcher(
        # Whatever dependencies the class will need
    )

    return bootstrap.ProviderConfiguration(
        provider_id=uuid.UUID("<valid UUIDv4>"),
        provider_name="Provider Name",
        trip_search_implementation=bootstrap.TripSearchImplementation(
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_IATA_CODES,
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=trip_searcher.find_one_way,
        ),
    )
```
