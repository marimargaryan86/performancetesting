from collections.abc import Sequence

from pydantic import Field

from snowfall.vendor.benerail.models import etag as etag_models
from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.dialogue.customer import BookerResponse
from snowfall.vendor.benerail.models.dialogue.dialogue import Dialogue
from snowfall.vendor.benerail.models.dialogue.passenger import Passenger
from snowfall.vendor.benerail.models.dialogue.trip import TripFilter
from snowfall.vendor.benerail.models.link import Link, ResourceLink
from snowfall.vendor.benerail.models.metadata import Metadata
from snowfall.vendor.benerail.models.trip_offers.trip_offers import TripOfferFilter


class GetBookerResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: BookerResponse | None = Field(None, alias="result")
    links: list[Link] | None = Field(
        None,
        example=[
            {
                "href": "https://api.example.com/dialogues/10001/passengers/50001",
                "title": "John Massis - 1995-12-17",
                "rel": "self",
                "type": "GET",
            },
            {
                "href": "https://api.example.com/dialogues/10001/passengers",
                "title": "Passengers dialogue 10001",
                "rel": "collection",
                "type": "GET",
            },
            {
                "href": "https://api.example.com/dialogues/10001/passengers/50001",
                "title": "John Massis - 1995-12-17",
                "rel": "self",
                "type": "DELETE",
            },
        ],
    )


class GetDialoguesResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: list[ResourceLink] | None = Field(None, alias="result")
    links: list[Link] | None = None

    def get_dialogue_ids(self) -> Sequence[str]:
        if not self.response_result:
            return []

        return [
            url.href.path.split("/")[-1]  # type: ignore[union-attr]
            for url in self.response_result
        ]


class GetDialogueResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: Dialogue = Field(..., alias="result")
    links: list[Link] | None = None
    etag: str

    def set_etags(self, etag_data: etag_models.EtagData) -> None:
        etag_data.dialogue_etag = self.etag


class GetPassengerResponse(BenerailBaseModel):
    metadata: Metadata
    response_result: Passenger = Field(..., alias="result")
    links: list[Link] | None = None
    etag: str

    def set_etags(self, etag_data: etag_models.EtagData) -> None:
        etag_data.passenger_etags[self.response_result.identifier] = (
            self.metadata.resource_etag or ""
        )


class GetTripFilterResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: TripFilter = Field(..., alias="result")
    links: list[Link] | None = None
    etag: str


class GetTripOfferFilterResponse(BenerailBaseModel):
    metadata: Metadata | None = None
    response_result: TripOfferFilter = Field(..., alias="result")
    links: list[Link] | None = None
    etag: str
