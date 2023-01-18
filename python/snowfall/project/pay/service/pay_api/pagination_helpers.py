import types
from typing import Dict

import currencycloud
from furl import furl

PAGE_CURSOR_KEY = "page[cursor]"
PAGE_LIMIT_KEY = "page[limit]"

PAGINATION_PARAMS_MAPPING = types.MappingProxyType(
    {
        "sort": "order",
        PAGE_CURSOR_KEY: "page",
        PAGE_LIMIT_KEY: "per_page",
    },
)


def map_query_params(
    query_params: Dict[str, str],  # noqa: SF20
    params_mapping: types.MappingProxyType[str, str],
) -> Dict[str, str]:
    mapped_params = {}

    for parameter in query_params.keys():
        if params_mapping.get(parameter):
            mapped_params[params_mapping[parameter]] = query_params[parameter]
        else:
            mapped_params[parameter] = query_params[parameter]

    return mapped_params


def get_next_link(
    url: str,
    pagination: currencycloud.resources.pagination.Pagination,
) -> dict[str, str]:
    next_url = furl(url)
    next_url.args[PAGE_CURSOR_KEY] = pagination.next_page
    next_url.args[PAGE_LIMIT_KEY] = pagination.per_page

    return {"next": next_url.url}
