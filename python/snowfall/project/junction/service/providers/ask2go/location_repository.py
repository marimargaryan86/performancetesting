from snowfall.project.junction.provider.airports import (
    Airport,
    AirportRepository,
)
from snowfall.project.junction.service.providers.ask2go.train_stations import (
    TrainStationRepository,
)
from snowfall.vendor.ask2go.models import offers


class LocationRepository(object):
    def __init__(
        self,
        airport_repository: AirportRepository,
        train_station_repository: TrainStationRepository,
    ):
        self.airport_repository = airport_repository
        self.train_station_repository = train_station_repository

    def retrieve_by_hub(self, orig_dest: offers.TripOriginDestination) -> Airport:
        if isinstance(orig_dest, offers.TripOriginDestinationFlight):
            return self.airport_repository.get_by_iata(
                orig_dest.airport_code,
            )
        if isinstance(orig_dest, offers.TripOriginDestinationRail):
            return self.train_station_repository.retrieve_by_code(
                orig_dest.trainstation_code,
            )
        raise NotImplementedError()
