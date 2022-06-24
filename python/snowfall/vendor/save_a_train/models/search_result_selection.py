from typing import Optional

from pydantic import BaseModel

from snowfall.vendor.save_a_train.models.search import SearchResult


class SearchResultSeatPreferenceOption(BaseModel):
    code: str
    name: str
    description: Optional[str]


class SearchResultSeatPreference(BaseModel):
    currency: str
    amount: str
    status: str
    options: list[SearchResultSeatPreferenceOption]


class SearchResultSelected(SearchResult):
    seat_preference: Optional[SearchResultSeatPreference]


class SearchResultSelectionResponse(BaseModel):
    search_identifier: str
    outbound_selected_result: SearchResultSelected
    inbound_selected_result: Optional[SearchResultSelected]
