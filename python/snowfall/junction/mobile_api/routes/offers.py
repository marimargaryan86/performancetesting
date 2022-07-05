import datetime
from typing import Any

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.junction.client_api import resources
from snowfall.junction.mobile_api import repository
from snowfall.junction.mobile_api import resources as mobile_resources
from snowfall.junction.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.vendor.junction import client

_DATA_KEY = "data"
_ID_KEY = "id"
_ATTRIBUTES_KEY = "attributes"
_TYPE_KEY = "type"
_DETAILS_KEY = "details"


class OfferSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        offers_repository: repository.OffersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        user_id = request.user.username
        offer_search = await junction_client.create_offer_search(
            trip_ids=body["trips"],
            passengers_dates_of_birth=[
                datetime.date.fromisoformat(passenger["dateOfBirth"])
                for passenger in body["passengers"]
            ],
        )
        await offers_repository.append_offer_search(
            user_id,
            models_pb2.OfferSearchHistoryEntity(
                offer_search_id=offer_search[_DATA_KEY][_ID_KEY],
            ),
        )
        return models.JsonApiResponse(
            models.Body(
                data=resources.TripOfferSearchResource(**offer_search[_DATA_KEY]),
            ),
            status.HTTP_201_CREATED,
        )


class OffersByOfferSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        offer_search_id = request.path_params["offerSearchId"]
        offers_response = await get_response(offer_search_id, junction_client)
        return models.JsonApiResponse(
            models.Body(
                data=[
                    mobile_resources.OfferSearchOffersResource.from_dict(offer_response)
                    for offer_response in offers_response
                ],
            ),
        )


async def get_response(
    offer_search_id: str,
    junction_client: client.JunctionClient,
) -> Any:
    return [
        {
            _ID_KEY: offer[_ID_KEY],
            _TYPE_KEY: offer[_TYPE_KEY],
            _ATTRIBUTES_KEY: {
                "groups": [
                    {
                        _ID_KEY: group[_ID_KEY],
                        _TYPE_KEY: group[_TYPE_KEY],
                        _ATTRIBUTES_KEY: {
                            "options": [
                                {
                                    _ID_KEY: offer_option[_ID_KEY],
                                    _TYPE_KEY: offer_option[_TYPE_KEY],
                                    _ATTRIBUTES_KEY: {
                                        "price": offer_option[_ATTRIBUTES_KEY]["price"],
                                        _DETAILS_KEY: [
                                            {
                                                _ID_KEY: offer_option_detail[_ID_KEY],
                                                _TYPE_KEY: offer_option_detail[
                                                    _TYPE_KEY
                                                ],
                                                _ATTRIBUTES_KEY: {
                                                    "cabinClassName": offer_option_detail[
                                                        _ATTRIBUTES_KEY
                                                    ][
                                                        "cabinClassName"
                                                    ],
                                                    _DETAILS_KEY: offer_option_detail[
                                                        "relationships"
                                                    ][_DETAILS_KEY],
                                                },
                                            }
                                            for offer_option_detail in (
                                                await junction_client.get_offer_option_details_by_offer_option_id(  # noqa: B950
                                                    offer_option[_ID_KEY],
                                                )
                                            )[_DATA_KEY]
                                        ],
                                    },
                                }
                                for offer_option in (
                                    await junction_client.get_offer_options_by_offer_group_id(  # noqa: B950
                                        group[_ID_KEY],
                                    )
                                )[_DATA_KEY]
                            ],
                            _DETAILS_KEY: [
                                {
                                    _ID_KEY: group_details[_ID_KEY],
                                    _TYPE_KEY: group_details[_TYPE_KEY],
                                    _ATTRIBUTES_KEY: group_details[_ATTRIBUTES_KEY],
                                }
                                for group_details in (
                                    await junction_client.get_offer_group_details_by_offer_group_id(  # noqa: B950
                                        group[_ID_KEY],
                                    )
                                )[_DATA_KEY]
                            ],
                        },
                    }
                    for group in (
                        await junction_client.get_offer_groups_by_offer_id(
                            offer[_ID_KEY],
                        )
                    )[_DATA_KEY]
                ],
                "expiresAt": offer[_ATTRIBUTES_KEY]["expiresAt"],
            },
        }
        for offer in (
            await junction_client.get_offers_by_offer_search_id(offer_search_id)
        )[_DATA_KEY]
    ]
