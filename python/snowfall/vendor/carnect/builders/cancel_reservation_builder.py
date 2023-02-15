from __future__ import annotations

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.builders.common import PosBuilder
from snowfall.vendor.carnect.models.service import (
    CancelInfoRqtype,
    PersonNameType,
    UniqueIdType,
    VehCancelResRq,
    VehCancelResRqTarget,
)


class CancelInfoTypeBuilder(object):
    def __init__(self) -> None:
        self._builder = CancelInfoRqtype()
        self._builder.unique_id = []

    def get(self) -> CancelInfoRqtype:
        return self._builder

    def add_unique_id(self) -> UniqueIdTypeBuilder:
        unique_id = UniqueIdTypeBuilder()
        self._builder.unique_id.append(unique_id.get())
        return unique_id

    def get_person_name(self) -> PersonNameTypeBuilder:
        person_name = PersonNameTypeBuilder()
        self._builder.person_name = person_name.get()
        return person_name


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


class CancelReservationRqBuilder(object):
    def __init__(self, conf: config.Config) -> None:
        self._rq = VehCancelResRq()
        self._pos = PosBuilder()
        self._pos.set_credentials(conf)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehCancelResRqTarget.TEST
            if conf.is_test
            else VehCancelResRqTarget.PRODUCTION
        )

    def build(self) -> VehCancelResRq:
        return self._rq

    def unique_context_id(self, unique_context_id: str) -> None:
        self._rq.veh_cancel_rqcore = CancelInfoRqtype(
            [
                UniqueIdType(
                    id_context=unique_context_id,
                ),
            ],
        )

    def unique_id_and_surname(self, unique_id: str, surname: str) -> None:
        self._rq.veh_cancel_rqcore = CancelInfoRqtype(
            [
                UniqueIdType(
                    id=unique_id,
                    type="14",
                ),
            ],
            person_name=PersonNameType(
                surname=surname,
            ),
        )

    def get_cancel_info_type(self) -> CancelInfoTypeBuilder:
        cancel_info_type = CancelInfoTypeBuilder()
        self._rq.veh_cancel_rqcore = cancel_info_type.get()
        return cancel_info_type
