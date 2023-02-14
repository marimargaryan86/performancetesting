from abc import ABC, abstractmethod

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.models.service import ArrayOfSourceType, SourceType


class PosSourceBuilder(object):
    def __init__(self) -> None:
        self._source = SourceType()

    def get(self) -> SourceType:
        return self._source

    def iso_country(self, country_code: str) -> None:
        self._source.isocountry = country_code

    def user_name(self, user_name: str) -> None:
        if self._source.requestor_id is None:
            self._source.requestor_id = SourceType.RequestorId()

        self._source.requestor_id.type = user_name

    def password(self, password: str) -> None:
        if self._source.requestor_id is None:
            self._source.requestor_id = SourceType.RequestorId()

        self._source.requestor_id.id_context = password


class PosBuilder(object):
    def __init__(self) -> None:
        self._pos = ArrayOfSourceType()

    def get(self) -> ArrayOfSourceType:
        return self._pos

    def add_source(self) -> PosSourceBuilder:
        source = PosSourceBuilder()
        self._pos.source.append(source.get())
        return source

    def set_credentials(self, conf: config.Config) -> PosSourceBuilder:
        source = PosSourceBuilder()
        self._pos.source.append(source.get())

        source.iso_country("EN")
        source.user_name(conf.username)
        source.password(conf.password)
        return source


class BaseBuilderRq(ABC):
    @abstractmethod
    def pos(self) -> PosBuilder:
        """Return POS builder."""
