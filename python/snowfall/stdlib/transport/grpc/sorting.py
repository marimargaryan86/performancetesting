from typing import Mapping

import pymongo

from snowfall.stdlib.v1 import sort_pb2


def get_sort(
    sort: sort_pb2.Sort,
    sort_mapping: Mapping[str, str],
) -> tuple[str, int] | None:
    if not sort.field:
        return None

    order = pymongo.ASCENDING

    if sort.order == sort_pb2.Sort.Order.ORDER_DESCENDING:
        order = pymongo.DESCENDING

    return sort_mapping[sort.field], order
