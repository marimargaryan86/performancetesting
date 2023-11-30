import pytest
from grpc import aio

from snowfall.project.junction.service.gateway import providers
from snowfall.stdlib import sequence, string
from snowfall.stdlib.testing import asserts

_IDENTIFIERS = frozenset(string.uuid() for _ in range(10))


def test_marshal_and_unmarshal_resource_id() -> None:
    provider_id = string.uuid()
    resource_id = string.uuid()
    provider = providers.Provider(
        connection=providers.Connection(aio.insecure_channel("foobar")),
        identifier=provider_id,
    )

    marshalled_resource_id = provider.marshal_resource_id(resource_id)

    assert "=" not in marshalled_resource_id

    unmarshal_result = providers.unmarshal_resource_id(marshalled_resource_id)

    assert provider_id == unmarshal_result.provider_id
    assert resource_id == unmarshal_result.resource_id


async def test_unmarshal_resource_ids() -> None:
    all_ids: list[str] = []

    for provider_id in _IDENTIFIERS:
        provider = providers.Provider(
            connection=providers.Connection(aio.insecure_channel("foobar")),
            identifier=provider_id,
        )

        all_ids.extend(
            provider.marshal_resource_id(resource_id) for resource_id in _IDENTIFIERS
        )

    assert len(all_ids) == len(_IDENTIFIERS) * len(_IDENTIFIERS)

    grouped_unmarshal_results = providers.unmarshal_resource_ids(all_ids)

    await asserts.assert_iterable(grouped_unmarshal_results.keys(), _IDENTIFIERS)

    for group_provider_ids in grouped_unmarshal_results.values():
        await asserts.assert_iterable(group_provider_ids, _IDENTIFIERS)


async def test_unmarshal_resource_id_invalid_length() -> None:
    with pytest.raises(sequence.InvalidCompositeError):
        providers.unmarshal_resource_id(sequence.to_composite_id(["foo", "bar", "baz"]))
