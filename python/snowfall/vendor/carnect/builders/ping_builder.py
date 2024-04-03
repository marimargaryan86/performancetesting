from __future__ import annotations

from snowfall.vendor.carnect.models.service import PingRq


class PingRqBuilder:
    def __init__(self) -> None:
        self._rq = PingRq()

    def build(self) -> PingRq:
        return self._rq

    def add_echo(self, echo: str) -> PingRqBuilder:
        self._rq.echo_data = echo
        return self
