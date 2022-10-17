import datetime

from snowfall.vendor.ask2go import enums
from snowfall.vendor.ask2go.models import search


def test_inbound_and_outbound_are_datetimes() -> None:
    now = datetime.datetime.now()
    search_criteria = search.CreateSearchCriteria(
        origin_iata="ARN",
        destination_iata="LHR",
        outbound_date=now,
        cabin_class=enums.AirCabinClassType.first,
        adults=1,
        children=0,
        infants=0,
    )

    search_criteria.inbound_date = now

    assert search_criteria.inbound_date == search_criteria.outbound_date
