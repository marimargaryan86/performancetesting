from snowfall.vendor.flight_stats.models.flight_stats import Error


class FlightStatsError(Exception):
    def __init__(
        self,
        http_status_code: int,
        error_id: str,
        error_message: str,
        error_code: str,
    ):
        super().__init__(error_message)
        self.http_status_code = http_status_code
        self.error_id = error_id
        self.error_message = error_message
        self.error_code = error_code

    @classmethod
    def from_error(cls, error: Error) -> "FlightStatsError":
        return cls(
            **error.model_dump(),
        )
