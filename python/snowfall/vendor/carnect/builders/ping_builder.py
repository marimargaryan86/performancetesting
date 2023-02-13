from typing import Any

from snowfall.vendor.carnect.models.service import PingRq


class PingRqBuilder(object):
    def __init__(self) -> None:
        self._rq = PingRq()

    def build(self) -> PingRq:
        return self._rq

    def add_echo(self, echo: str) -> Any:
        self._rq.echo_data = echo
        return self
