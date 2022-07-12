import itertools
from typing import Any, Callable, Coroutine, Mapping, Sequence, Union, cast

import lagom
from starlette import requests, responses, status

from snowfall.project.junction.adapter import offers as offers_adapter
from snowfall.project.junction.adapter import orders as orders_adapter
from snowfall.project.junction.service.offers.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import models, request_helpers

_OFFERS = "offers"
_OFFER_AGGREGATE_ID = "offerAggregateId"
_OFFER_IDS = "offerIds"
_OfferMap = Mapping[str, Union[str, Sequence[str]]]


def _validate_unique_offer_ids(
    aggregate_ids: frozenset[str],
    offers: Sequence[_OfferMap],
) -> list[models.Error]:
    if len(aggregate_ids) == len(offers):
        return []

    remaining_ids = set(aggregate_ids.copy())
    errors: list[models.Error] = []

    for idx, offer in enumerate(offers):
        try:
            remaining_ids.remove(cast(str, offer[_OFFER_AGGREGATE_ID]))
        except KeyError:
            errors.append(
                models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code="duplicated_offer",
                    detail="'{0}' is duplicated".format(
                        offer[_OFFER_AGGREGATE_ID],
                    ),
                    source=models.ErrorSource(
                        pointer="/data/attributes/offers/{0}/offerAggregateId".format(
                            idx,
                        ),
                    ),
                ),
            )

    return errors


def _get_group_with_option_id(
    groups: Mapping[str, frozenset[str]],
    option_id: str,
) -> str:
    return next(
        group for group, group_offers in groups.items() if option_id in group_offers
    )


def _validate_offer_options_against_groups(
    offer_index: int,
    offer: _OfferMap,
    groups: Mapping[str, frozenset[str]],
) -> tuple[set[str], list[models.Error]]:
    errors: list[models.Error] = []
    picked_groups = set()

    for option_index, option_id in enumerate(offer[_OFFER_IDS]):
        try:
            group = _get_group_with_option_id(groups, option_id)
        except StopIteration:
            errors.append(
                models.Error(
                    status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                    code="invalid",
                    detail="'{0}' is not a valid option for this offer".format(
                        option_id,
                    ),
                    source=models.ErrorSource(
                        pointer="/data/attributes/offers/{0}/offerIds/{1}".format(
                            offer_index,
                            option_index,
                        ),
                    ),
                ),
            )
        else:
            if group in picked_groups:
                errors.append(
                    models.Error(
                        status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                        code="duplicated_group",
                        detail=(
                            "'{0}' belongs to the same group as another provided option"
                        ).format(option_id),
                        source=models.ErrorSource(
                            pointer="/data/attributes/offers/{0}/offerIds/{1}".format(
                                offer_index,
                                option_index,
                            ),
                        ),
                    ),
                )

            picked_groups.add(group)

    return groups.keys() - picked_groups, errors


def _validate_offer_options(
    id_to_offer_aggregate: Mapping[str, models_pb2.OfferAggregate],
    offer_index: int,
    offer: _OfferMap,
) -> list[models.Error]:
    try:
        aggregate = id_to_offer_aggregate[cast(str, offer[_OFFER_AGGREGATE_ID])]
    except KeyError:
        return [
            models.Error(
                status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                code="not_found",
                detail="'{0}' was not found or has expired".format(
                    offer[_OFFER_AGGREGATE_ID],
                ),
                source=models.ErrorSource(
                    pointer="/data/attributes/offers/{0}/offerAggregateId".format(
                        offer_index,
                    ),
                ),
            ),
        ]

    groups, errors = _validate_offer_options_against_groups(
        offer_index,
        offer,
        {
            group.id: frozenset((offer.id for offer in group.offers))
            for group in aggregate.groups
        },
    )

    for group_id in groups:
        errors.append(
            models.Error(
                status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                code="missing",
                detail="No option chosen for offer group '{0}'".format(
                    group_id,
                ),
                source=models.ErrorSource(
                    pointer="/data/attributes/offers/{0}/offerIds".format(
                        offer_index,
                    ),
                ),
            ),
        )

    return errors


async def _fetch_all_offers(
    offers_client: offers_adapter.Client,
    aggregate_ids: Sequence[str],
) -> list[models_pb2.OfferAggregate]:
    cursor = ""
    offers: list[models_pb2.OfferAggregate] = []

    while True:
        offers_page = await offers_client.find_by_ids(
            identifiers=aggregate_ids,
            cursor=cursor,
        )

        if not offers_page.offers:
            break

        offers.extend(offers_page.offers)

        cursor = offers_page.next_page_token

    return offers


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
        offer_ids = (await request_helpers.flatten_request(request))[_OFFERS]
        aggregate_ids = frozenset((offer[_OFFER_AGGREGATE_ID] for offer in offer_ids))
        errors = _validate_unique_offer_ids(aggregate_ids, offer_ids)

        if errors:
            return models.JsonApiResponse(
                models.Body(errors=errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        aggregate_map = {
            aggregate.id: aggregate
            for aggregate in await _fetch_all_offers(offers_client, list(aggregate_ids))
        }

        errors = list(
            itertools.chain(
                *[
                    _validate_offer_options(aggregate_map, *offer)
                    for offer in enumerate(offer_ids)
                ],
            ),
        )

        if errors:
            return models.JsonApiResponse(
                models.Body(errors=errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return await function(self, request, orders_client)

    return wrapper
