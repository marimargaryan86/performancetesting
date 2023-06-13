from pydantic import BaseModel

from snowfall.vendor.save_a_train.models.search import SearchResult


class SearchResultSeatPreferenceOption(BaseModel):
    code: str
    name: str
    description: str | None


class SearchResultSeatPreference(BaseModel):
    currency: str
    amount: str
    status: str
    options: list[SearchResultSeatPreferenceOption]


class SearchResultSelected(SearchResult):
    seat_preference: SearchResultSeatPreference | None


class SearchResultSelectionResponse(BaseModel):
    search_identifier: str
    outbound_selected_result: SearchResultSelected
    inbound_selected_result: SearchResultSelected | None
