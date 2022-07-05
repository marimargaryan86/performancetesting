import pytest

from snowfall import fixtures
from snowfall.project.junction.adapter import offer_searches
from snowfall.project.junction.service.offers.v1alpha import models_pb2


@pytest.mark.asyncio
async def test_offer_search_can_be_saved(
    offer_searches_client: offer_searches.Client,
    offer_search: models_pb2.OfferSearch,
) -> None:
    await offer_searches_client.create(offer_search)


@pytest.mark.asyncio
async def test_offer_search_can_be_retrieved(
    offer_searches_client: offer_searches.Client,
    offer_search: models_pb2.OfferSearch,
) -> None:
    offer_search = await offer_searches_client.create(offer_search)
    assert await offer_searches_client.get(offer_search.id)


@pytest.mark.asyncio
async def test_missing_offer_search_throws_error(
    offer_searches_client: offer_searches.Client,
) -> None:
    with pytest.raises(offer_searches.NotFoundError):
        await offer_searches_client.get(fixtures.NOT_FOUND)
