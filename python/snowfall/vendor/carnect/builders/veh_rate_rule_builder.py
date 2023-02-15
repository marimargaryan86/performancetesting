from __future__ import annotations

from snowfall.vendor.carnect.builders.common import BaseBuilderRq, PosBuilder
from snowfall.vendor.carnect.models.service import (
    UniqueIdType,
    VehRateRuleRq,
    VehRateRuleRqTarget,
)


class VehRateRuleRqBuilder(BaseBuilderRq):
    def __init__(self) -> None:
        self._rq = VehRateRuleRq()
        self._pos = PosBuilder()
        self._rq.pos = self._pos.get()

    def build(self) -> VehRateRuleRq:
        return self._rq

    def echo_token(self, echo_token: str) -> None:
        self._rq.echo_token = echo_token

    def target(self, target: VehRateRuleRqTarget) -> None:
        self._rq.target = target

    def pos(self) -> PosBuilder:
        return self._pos

    def reference(self, reference: str) -> None:
        if self._rq.reference is None:
            self._rq.reference = UniqueIdType()

        self._rq.reference.id_context = reference
        self._rq.reference.type = "16"  # unique id type ‘reference’
