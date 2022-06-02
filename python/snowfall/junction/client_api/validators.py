from itertools import zip_longest
from typing import Any, Callable, Coroutine, Sequence

import lagom
from starlette import exceptions, requests, responses, status

from snowfall.adapter import offers as offers_adapter
from snowfall.adapter import orders as orders_adapter
from snowfall.junction.offers.v1alpha import models_pb2 as offer_models_pb2
from snowfall.stdlib.integration.starlette import request_helpers

_OFFERS = "offers"
_OFFER_AGGREGATE_ID = "offerAggregateId"


def _offer_ids_match_aggregate(
    offer_ids: Sequence[str],
    offer_aggregate: offer_models_pb2.OfferAggregate,
) -> bool:
    return all(
        any(offer_id == offer.id for offer in offer_group.offers)
        for offer_id, offer_group in zip_longest(offer_ids, offer_aggregate.groups)
    )


def order_request_validator(
    function: Callable[  # noqa: WPS320
        [Any, requests.Request, orders_adapter.Client],
        Coroutine[Any, Any, responses.Response],
    ],
) -> Callable[..., Any]:
    async def wrapper(
        self: Any,
        request: requests.Request,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        offers = (await request_helpers.flatten_request(request))[_OFFERS]

        offers_page = await offers_client.find_by_ids(
            identifiers=[offer[_OFFER_AGGREGATE_ID] for offer in offers],
            limit=len(offers),
        )

        if len(offers_page.offers) != len(offers):
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="offers requested: `{0}`, offers found: `{1}`".format(
                    [offer[_OFFER_AGGREGATE_ID] for offer in offers],
                    [offer.id for offer in offers_page.offers],
                ),
            )

        id_to_offer_aggregate = {
            aggregate.id: aggregate for aggregate in offers_page.offers
        }

        for offer in offers:
            aggregate = id_to_offer_aggregate[offer[_OFFER_AGGREGATE_ID]]
            if not _offer_ids_match_aggregate(offer["offerIds"], aggregate):
                raise exceptions.HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="offer aggregate id: {0}".format(
                        offer[_OFFER_AGGREGATE_ID],
                    ),
                )

        return await function(self, request, orders_client)

    return wrapper
