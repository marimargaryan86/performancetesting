from snowfall.project.junction.rocket.service.api.hotel.models import HotelSearchResult
from snowfall.stdlib.persistence.mongo import mixins, repository


class HotelSearchRepository(
    repository.PydanticRepository[HotelSearchResult],
    mixins.InsertMixin[HotelSearchResult],
    mixins.ExistsMixin[HotelSearchResult],
    mixins.FindByIdMixin[HotelSearchResult],
):
    _model = HotelSearchResult
