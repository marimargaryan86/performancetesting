from __future__ import annotations

from snowfall.vendor.carnect import config
from snowfall.vendor.carnect.builders.common import BaseBuilderRq, PosBuilder
from snowfall.vendor.carnect.models.service import (
    UniqueIdType,
    VehRateRuleRq,
    VehRateRuleRqTarget,
)


class VehRateRuleRqBuilder(BaseBuilderRq):
    def __init__(self, conf: config.Config) -> None:
        self._rq = VehRateRuleRq()
        self._pos = PosBuilder()
        self._pos.set_credentials(conf)
        self._rq.pos = self._pos.get()
        self._rq.target = (
            VehRateRuleRqTarget.TEST if conf.is_test else VehRateRuleRqTarget.PRODUCTION
        )

    def build(self) -> VehRateRuleRq:
        return self._rq

    def echo_token(self, echo_token: str) -> None:
        self._rq.echo_token = echo_token

    def pos(self) -> PosBuilder:
        return self._pos

    def reference(self, reference: str) -> None:
        if self._rq.reference is None:
            self._rq.reference = UniqueIdType()

        self._rq.reference.id_context = reference
        self._rq.reference.type = "16"  # unique id type ‘reference’
