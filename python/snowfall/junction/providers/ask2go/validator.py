import structlog

from snowfall.junction.providers.ask2go import models
from snowfall.vendor.ask2go.models import offers


class OfferValidator(object):
    def __init__(self) -> None:
        self._logger = structlog.get_logger(__name__)

    def matches(
        self,
        offer: offers.Offer,
        requirements: models.Requirements,
    ) -> bool:
        last_index = 0

        for trip in offer.trips:
            for segment_index, segment in enumerate(trip.segments, start=last_index):
                try:
                    requirement = requirements[segment_index]
                except IndexError:
                    return False

                if not self._segment_in_requirements(segment, requirement):
                    return False

                last_index = segment_index

        return True

    def _segment_in_requirements(
        self,
        segment: offers.TripSegment,
        requirement: models.Requirement,
    ) -> bool:
        departure_at = segment.departure.date_time.replace(
            tzinfo=requirement.departure_tz,
        )

        if departure_at != requirement.departure_at:
            self._logger.info(
                "Departure times do not match",
                requirement_departure_at=requirement.departure_at.isoformat(),
                offer_departure_at=departure_at.isoformat(),
            )

            return False

        arrival_at = segment.arrival.date_time.replace(tzinfo=requirement.arrival_tz)

        if arrival_at != requirement.arrival_at:
            self._logger.info(
                "Arrival times do not match",
                requirement_arrival_at=requirement.arrival_at.isoformat(),
                offer_arrival_at=arrival_at.isoformat(),
            )

            return False

        return True
