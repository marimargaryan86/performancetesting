import asyncio
from collections.abc import Iterable, Sequence

from snowfall.project.junction.go.service.offers.v1 import models_pb2
from snowfall.project.junction.service.providers.benerail import helper_functions
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.http import errors
from snowfall.vendor.benerail import client
from snowfall.vendor.benerail.models.products import response as product_response
from snowfall.vendor.benerail.models.trip_offers import offer, response

_logger = stdout.get_logger()


def _rules_from_products(
    products: Sequence[product_response.GetProductResponse],
) -> list[models_pb2.FareRule]:
    rules = []

    for product in products:
        rules.extend(
            [
                models_pb2.FareRule(
                    title=condition.condition_type.replace("_", " ").title(),
                    body=condition.description,
                )
                for condition in product.response_result.conditions or []
            ],
        )

    return rules


async def _get_products(
    benerail_client: client.BenerailClient,
    offer_parts: Iterable[response.GetOfferPartResponse],
) -> Sequence[product_response.GetProductResponse]:
    seen = set()
    coros = []

    for offer_part in offer_parts:
        product_ref = offer_part.response_result.offer_part_common.product.href

        if not product_ref.path:
            continue

        tariff_ref = helper_functions.last_id_of_url(product_ref)

        if tariff_ref in seen:
            continue

        coros.append(
            benerail_client.trip_offers_client.get_product_in_trip_offer_collection(
                trip_offer_collection_id=product_ref.path.rsplit("/", 3)[-3],
                tariff_ref=tariff_ref,
            ),
        )

        seen.add(tariff_ref)

    return await asyncio.gather(*coros)


async def get_fare_rules(
    benerail_client: client.BenerailClient,
    offer_obj: offer.Offer,
) -> list[models_pb2.FareRule]:
    try:
        offer_parts = await asyncio.gather(
            *(
                benerail_client.offers_client.get_offer_part_info(
                    offer_id=offer_obj.identifier,
                    offer_part_id=helper_functions.last_id_of_url(offer_part.href),
                )
                for offer_part in offer_obj.offer_parts
            ),
        )
    except errors.HttpError:
        _logger.exception("Failed to get one or more offer part")

        return []

    try:
        products = await _get_products(benerail_client, offer_parts)
    except errors.HttpError:
        _logger.exception("Failed to get one or more product")

        return []

    return _rules_from_products(products)
