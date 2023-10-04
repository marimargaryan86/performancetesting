import asyncio

import pydantic

from snowfall.service.deploy import consul, dependencies, verify
from snowfall.service.deploy.verifiers import junction_go, protocols
from snowfall.stdlib.service import application

_verifiers: tuple[protocols.Verifier, ...] = (junction_go.OfferSearchFlow(),)


class _VerifySettings(application.Settings):
    nomad_address: pydantic.HttpUrl
    nomad_templates_path: pydantic.DirectoryPath
    changed_services: list[str] = pydantic.Field(json_schema_extra={"argument": True})


async def _verify(app: application.Application[_VerifySettings]) -> None:
    dns_address = str(app.settings.nomad_address.host)
    dns_resolver = consul.Resolver((dns_address, 8600), app.environment)
    deps_resolver = await dependencies.resolver_from_nomad_templates(
        app.settings.nomad_templates_path,
    )
    deploy_is_ok = all(
        await asyncio.gather(
            *(
                verify.run(
                    verifier=verifier,
                    environment=app.environment,
                    changed_services=app.settings.changed_services,
                    dns_resolver=dns_resolver,
                    deps_resolver=deps_resolver,
                )
                for verifier in _verifiers
            ),
        ),
    )

    if not deploy_is_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="deploy", cli_tool=True)

    entrypoint.enter_with_commands(
        application.Command(
            name="verify",
            callback=_verify,
            settings_class=_VerifySettings,
        ),
    )
