import datetime
from typing import Any

from snowfall.vendor.ask2go.models import search


def parse_search_criteria(
    origin_iata: str,
    destination_iata: str,
    date: datetime.date,
) -> dict[str, Any]:
    return {
        "origin": origin_iata,
        "destination": destination_iata,
        "departure": date.strftime("%Y-%m-%d"),
    }


def parse_search_request(criteria: search.CreateSearchCriteria) -> dict[str, Any]:
    search_criteria = [
        parse_search_criteria(
            criteria.origin_iata,
            criteria.destination_iata,
            criteria.outbound_date,
        ),
    ]

    if criteria.inbound_date:
        direction = "Both"

        search_criteria.append(
            parse_search_criteria(
                criteria.destination_iata,
                criteria.origin_iata,
                criteria.inbound_date,
            ),
        )
    else:
        direction = "Outbound"

    return {
        "adults": criteria.adults,
        "children": criteria.children,
        "infants": criteria.infants,
        "cabinClass": criteria.cabin_class.value,
        "direction": direction,
        "searchCriteria": search_criteria,
    }
