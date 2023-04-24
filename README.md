# Junction

Junction is a mono-repository that uses [Pants][pants].

## Setup

Check the [CONTRIBUTING.md](CONTRIBUTING.md) file for the setup instructions.


## Project Architecture
Follow this image of the Junction [architecture][junction-architecture].

When a client sends an HTTP request to the `client_api`, `starlette` checks if there is an endpoint defined in `python/snowfall/project/junction/go/service/client_api/routes/router.py` for the route the user specified.

For example, the client sends a `GET` request on the `/places` route.
`Starlette` checks if there is a route `/places` specified in the `python/snowfall/project/junction/go/service/client_api/routes/router.py`:

```python
dependencies.route(
    "/places",
    places.Places,
    name="ListPlaces",
)
```

This tells `starlette` to forward the request to the `places.Places` class specified in the `python/snowfall/project/junction/go/service/client_api/routes/places.py`.
The `places.Places` also receives an adapter `Client` object as an argument that is injected using `lagom`.
The `Client` is an abstract class is defined in `python/snowfall/project/junction/adapter/places.py`.
The `GrpcClient` implementation defines communication with the `python/snowfall/project/junction/go/service/places` service using the `grpc` protocol.
The `places grpc` service then reads the places from the `mongo` collection and returns them to the adapter `Client` which returns the data to the endpoint which in turn forwards it to the user.


[junction-architecture]: https://miro.com/app/board/uXjVOIhsVCg=/
[pants]: https://pantsbuild.github.io/
