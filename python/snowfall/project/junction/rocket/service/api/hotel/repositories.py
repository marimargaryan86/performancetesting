from snowfall.project.junction.rocket.service.api.hotel.models import (
    HotelRoomsSearchResult,
    HotelSearchResult,
)
from snowfall.stdlib.persistence.mongo import mixins, repository


class HotelSearchRepository(
    repository.PydanticRepository[HotelSearchResult],
    mixins.InsertMixin[HotelSearchResult],
    mixins.ExistsMixin[HotelSearchResult],
    mixins.FindByIdMixin[HotelSearchResult],
):
    _model = HotelSearchResult


class HotelRoomsSearchRepository(
    repository.PydanticRepository[HotelRoomsSearchResult],
    mixins.InsertMixin[HotelRoomsSearchResult],
    mixins.ExistsMixin[HotelRoomsSearchResult],
    mixins.FindByIdMixin[HotelRoomsSearchResult],
):
    _model = HotelRoomsSearchResult
