import asyncio
from urllib import parse as urllib_parse

import pydantic

from snowfall.service.deploy import consul, verify
from snowfall.service.deploy.verifiers import junction_go, protocols
from snowfall.stdlib import service
from snowfall.stdlib.logging import stdout

_verifiers: tuple[protocols.Verifier, ...] = (junction_go.OfferSearchFlow(),)


class _VerifySettings(service.Settings):
    nomad_address: pydantic.HttpUrl
    services: list[str] = pydantic.Field(argument=True)


async def _verify(app: service.AsyncApplication[_VerifySettings]) -> None:
    logger = stdout.get_logger()
    dns_address = str(urllib_parse.urlparse(app.settings.nomad_address).hostname)
    resolver = consul.Resolver((dns_address, 8600), app.environment)
    deploy_is_ok = all(
        await asyncio.gather(
            *(
                verify.run(
                    verifier=verifier,
                    environment=app.environment,
                    changed_services=app.settings.services,
                    logger=logger,
                    resolver=resolver,
                )
                for verifier in _verifiers
            ),
        ),
    )

    if not deploy_is_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="deploy", cli_tool=True)

    entrypoint.enter_with_commands(
        service.Command(
            name="verify",
            callback=_verify,
            settings_class=_VerifySettings,
        ),
    )
