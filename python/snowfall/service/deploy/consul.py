from typing import cast

from dns import asyncresolver
from dns.rdtypes.IN import SRV as SRV_RECORD
from dns.rdtypes.IN import A as A_RECORD


class Resolver(object):
    def __init__(self, nameserver: tuple[str, int], environment: str) -> None:
        self._environment = environment
        self._resolver = asyncresolver.Resolver()
        self._resolver.nameservers = [nameserver[0]]
        self._resolver.nameserver_ports = {
            nameserver[0]: nameserver[1],
        }

    async def query_service(self, name_command: tuple[str, str]) -> tuple[str, int]:
        srv_answers = await self._resolver.resolve(
            "{0}.{1}-{2}.service.consul".format(
                name_command[1],
                name_command[0],
                self._environment,
            ),
            "SRV",
        )
        srv_answer = cast(SRV_RECORD.SRV, srv_answers[0])
        a_answers = await self._resolver.resolve(srv_answer.target, "A")
        a_answer = cast(A_RECORD.A, a_answers[0])

        return a_answer.address, srv_answer.port
