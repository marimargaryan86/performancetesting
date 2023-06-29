from snowfall.stdlib import service


class _VerifySettings(service.Settings):
    """Settings for the verify command."""


async def _verify(app: service.AsyncApplication[_VerifySettings]) -> None:
    """Verify that a deployment is working as expected."""


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="deploy")

    entrypoint.enter_with_commands(
        service.Command(
            name="verify",
            callback=_verify,
            settings_class=_VerifySettings,
        ),
    )
