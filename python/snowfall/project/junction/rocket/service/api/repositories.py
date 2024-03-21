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

    @abstractmethod
    def find_by_id(self, id_: str) -> AirSearchResult:
        "Find by id."


class AirSearchRepo(AbstractAirSearchRepo):
    def __init__(self, mongo_client: MongoClient[Any] = lagom.injectable):
        self.collection = mongo_client["j1"]["air_results"]

    def insert(self, value: AirSearchResult) -> None:
        # Using model_dump_json so UUIDs are converted to strs.
        json_str = value.model_dump_json(exclude_none=True)
        self.collection.insert_one(orjson.loads(json_str))

    def exists_id(self, search_id: str) -> bool:
        document = self.collection.find_one({"id": search_id})
        return bool(document)

    def find_by_id(self, id_: str) -> AirSearchResult:
        result = self.collection.find_one({"id": id_})
        if not result:
            raise ValueError("No result for id:{0}".format(id_))
        return AirSearchResult(**result)
