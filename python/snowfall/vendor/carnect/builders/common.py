from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.models.service import (
    AddressType,
    ArrayOfSourceType,
    CountryNameType,
    PersonNameType,
    SourceType,
    StateProvType,
    UniqueIdType,
)

T = TypeVar("T")  # noqa: WPS111
A = TypeVar("A", bound=AddressType)  # noqa: WPS111


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


class UniqueIdTypeBuilder(object):
    def __init__(self) -> None:
        self._builder = UniqueIdType()

    def get(self) -> UniqueIdType:
        return self._builder

    def unique_id(self, unique_id: str) -> UniqueIdTypeBuilder:
        self._builder.id = unique_id
        return self

    def id_context(self, unique_id_context: str) -> UniqueIdTypeBuilder:
        self._builder.id_context = unique_id_context
        return self

    def unique_id_type(self, unique_id_type: str) -> UniqueIdTypeBuilder:
        self._builder.type = unique_id_type
        return self


class PersonNameTypeBuilder(object):
    def __init__(self) -> None:
        self._builder = PersonNameType()

    def get(self) -> PersonNameType:
        return self._builder

    def surname(self, surname: str) -> PersonNameTypeBuilder:
        self._builder.surname = surname
        return self


class AddressInfoBuilder(Generic[A]):
    def __init__(self, address: A) -> None:
        self._address = address

    def get(self) -> A:
        return self._address

    def street_nmbr(self, street_nmbr: str) -> None:
        self._address.street_nmbr = AddressType.StreetNmbr(value=street_nmbr)

    def add_address_line(self, address_line: str) -> None:
        self._address.address_line.append(address_line)

    def city_name(self, city_name: str) -> None:
        self._address.city_name = city_name

    def postal_code(self, postal_code: str) -> None:
        self._address.postal_code = postal_code

    def state_code(self, state_code: str) -> None:
        self._address.state_prov = StateProvType(state_code=state_code)

    def country_code(self, country_code: str) -> None:
        self._address.country_name = CountryNameType(code=country_code)


class BaseBuilderRq(ABC, Generic[T]):
    @abstractmethod
    def pos(self) -> PosBuilder:
        """Return POS builder."""

    @abstractmethod
    def build(self) -> T:
        """Return built object."""
