from abc import ABC, abstractmethod
from typing import Any

import lagom
import orjson
from pymongo import MongoClient

from snowfall.project.junction.rocket.service.api.models import AirSearchResult


class AbstractAirSearchRepo(ABC):
    @abstractmethod
    def insert(self, value: AirSearchResult) -> None:
        "Insert."

    @abstractmethod
    def exists_id(self, search_id: str) -> bool:
        "ID exists."


class AirSearchRepo(AbstractAirSearchRepo):
    def __init__(self, mongo_client: MongoClient[Any] = lagom.injectable):
        self.collection = mongo_client["j1"]["air_results"]

    def insert(self, value: AirSearchResult) -> None:
        # Using model_dump_json so UUIDs are converted to strs.
        json_str = value.model_dump_json(exclude_none=True)
        self.collection.insert_one(orjson.loads(json_str))

    def exists_id(self, search_id: str) -> bool:
        collection_object = self.collection.find_one({"_id": search_id})
        return bool(collection_object)
