import httpx

from snowfall.project.junction.rocket.service.api.flights.repositories import (
    QuoteRepository,
)
from snowfall.project.junction.rocket.service.api.v1alpha import pricing_pb2


async def test_get_flight_quote(
    client: httpx.AsyncClient,
    quote_repo: QuoteRepository,
) -> None:
    quote_id = "16038163-ad97-418c-a970-c9e8e919844a"
    quote = pricing_pb2.Quote(
        id=quote_id,
        offer_id="8dca6a9f-ebf6-4a56-aecb-765176a828b6",
        status=pricing_pb2.Quote.Status.STATUS_COMPLETED,
    )
    await quote_repo.insert(quote)

    response = await client.get("/quotes/{0}".format(quote_id))

    assert response.json() == {
        "data": {
            "attributes": {
                "expiresAt": "1970-01-01T00:00:00Z",
                "quotedOffers": [],
                "status": "completed",
            },
            "id": "16038163-ad97-418c-a970-c9e8e919844a",
            "links": {
                "self": "https://example.com/quotes/16038163-ad97-418c-a970-c9e8e919844a",
            },
            "relationships": {
                "offers": {
                    "data": [
                        {
                            "id": "8dca6a9f-ebf6-4a56-aecb-765176a828b6",
                            "type": "flight-offers",
                        },
                    ],
                },
            },
            "type": "quotes",
        },
    }

    assert response.status_code == 200
