from collections.abc import Mapping
from typing import cast

from starlette import requests

from snowfall.stdlib.v1 import sort_pb2


def get_sort(request: requests.Request, mapping: Mapping[str, str]) -> sort_pb2.Sort:
    sort_parameter = cast(str, request.scope["parsed_query_string"]["sort"])
    sort_field = sort_parameter.removeprefix("-")
    sort_order = sort_pb2.Sort.ORDER_ASCENDING

    if sort_parameter != sort_field:
        sort_order = sort_pb2.Sort.ORDER_DESCENDING

    return sort_pb2.Sort(field=mapping[sort_field], order=sort_order)
