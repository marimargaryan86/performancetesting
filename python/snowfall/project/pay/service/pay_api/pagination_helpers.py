import types
from typing import Mapping

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
    query_params: Mapping[str, str],
    params_mapping: types.MappingProxyType[str, str],
) -> dict[str, str]:
    mapped_params = {}

    for parameter in query_params.keys():
        if params_mapping.get(parameter):
            mapped_params[params_mapping[parameter]] = query_params[parameter]
        else:
            mapped_params[parameter] = query_params[parameter]

    return mapped_params
