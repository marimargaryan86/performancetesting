from typing import TypedDict


class Dataset(TypedDict):
    active: bool
    country: str
    name: str
    url: str
