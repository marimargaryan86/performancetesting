from snowfall.project.junction.rocket.service.api.air.models import AirSearchResult
from snowfall.stdlib.persistence.mongo import mixins, repository


class AirSearchRepository(
    repository.PydanticRepository[AirSearchResult],
    mixins.InsertMixin[AirSearchResult],
    mixins.ExistsMixin[AirSearchResult],
    mixins.FindByIdMixin[AirSearchResult],
):
    _model = AirSearchResult
