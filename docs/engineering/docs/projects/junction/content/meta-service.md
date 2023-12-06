# Meta Service

The only gRPC service that is required to deploy an implementation is the
`MetaService`, but that will only allow Junction Go to be aware of its
existence, as no other capabilities would be available.

This is a minimal example of a `MetaService` implementation would look like:

```python title="/python/snowfall/projects/junction/content/service/provider_name/main.py"
import uuid

from snowfall.project.junction.content import bootstrap


async def _factory(
    app: bootstrap.Application[bootstrap.Settings],
) -> bootstrap.ProviderConfiguration:
    return bootstrap.ProviderConfiguration(
        provider_id=uuid.UUID("<valid UUIDv4>"),
        provider_name="Provider Name",
    )


if __name__ == "__main__":
    entrypoint = bootstrap.Entrypoint(
        name="provider_name",
        implementation_factory=_factory,
        settings_class=bootstrap.Settings,
    )
    entrypoint.enter()
```

This will result in a service with a `grpc` command with the `MetaService`
available, being able to report its identifier and name, in addition to
revealing that it currently has no other capabilities.

The `provider_id` should be a UUIDv4 that is unique for that provider.
If there is an existing old version of the provider, use the same UUID.
