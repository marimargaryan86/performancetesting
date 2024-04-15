import pathlib
from collections.abc import Generator, Mapping
from typing import Protocol

import aiofiles
import orjson
import pydantic
from packaging import requirements, version

from snowfall.stdlib.service import application


class _OutdatedSettings(application.Settings):
    requirements_path: pydantic.FilePath = pydantic.Field(
        json_schema_extra={"argument": True},
    )


async def _outdated(app: application.Application[_OutdatedSettings]) -> None:
    await _parse_requirements_file(app.settings.requirements_path)


class _PinSettings(application.Settings):
    requirements_path: pydantic.FilePath = pydantic.Field(
        json_schema_extra={"argument": True},
    )
    constraints_path: pydantic.FilePath = pydantic.Field(
        json_schema_extra={"argument": True},
    )


async def _parse_constraints_file(constraints_path: pathlib.Path) -> Mapping[str, str]:
    async with aiofiles.open(constraints_path, "r") as constraints_file:
        parsed_file = orjson.loads(
            (await constraints_file.read()).split(
                "--- END PANTS LOCKFILE METADATA ---",
                maxsplit=1,
            )[1],
        )["locked_resolves"]

    return {
        package["project_name"]: package["version"]
        for resolve in parsed_file
        for package in resolve["locked_requirements"]
    }


async def _parse_requirements_file(
    requirements_path: pathlib.Path,
) -> set[tuple[requirements.Requirement, str | None]]:
    requirements_comments: set[tuple[requirements.Requirement, str | None]] = set()

    async with aiofiles.open(requirements_path, "r") as requirements_file:
        async for line in requirements_file:
            parts = line.strip().split("#", maxsplit=1)
            requirement = requirements.Requirement(parts[0])
            requirements_comments.add((
                requirement,
                parts[1].strip() if len(parts) > 1 else None,
            ))

    return requirements_comments


class _SpecifierGenerator(Protocol):
    def __call__(
        self,
        requirement: requirements.Requirement,
        *,
        is_frozen: bool,
    ) -> str:
        """Return a new version specifier for the requirement."""


def _generate_requirements_line(
    requirement_comment: tuple[requirements.Requirement, str | None],
    specifier_generator: _SpecifierGenerator,
) -> str:
    line_str = requirement_comment[0].name
    is_frozen = bool(requirement_comment[1] and "freeze" in requirement_comment[1])

    if requirement_comment[0].extras:
        line_str += "[{0}]".format(",".join(list(requirement_comment[0].extras)))

    line_str += specifier_generator(requirement_comment[0], is_frozen=is_frozen)

    if is_frozen:
        line_str += "  # {0}".format(requirement_comment[1])

    return line_str


async def _write_requirements_file(
    requirements_path: pathlib.Path,
    lines: Generator[str, None, None],
) -> None:
    async with aiofiles.open(requirements_path, "w") as requirements_file:
        for line in lines:
            await requirements_file.write("{0}\n".format(line))

        await requirements_file.flush()


async def _pin(app: application.Application[_PinSettings]) -> None:
    requirements_comments = await _parse_requirements_file(
        app.settings.requirements_path,
    )
    versions = await _parse_constraints_file(app.settings.constraints_path)

    def wrapper(requirement: requirements.Requirement, *, is_frozen: bool) -> str:
        return "=={0}".format(
            versions[requirement.name.lower().replace("_", "-").replace(".", "-")],
        )

    await _write_requirements_file(
        app.settings.requirements_path,
        (
            _generate_requirements_line(requirement_comment, wrapper)
            for requirement_comment in sorted(
                requirements_comments,
                key=lambda req: req[0].name.casefold(),
            )
        ),
    )


class _UnpinSettings(application.Settings):
    requirements_path: pydantic.FilePath = pydantic.Field(
        json_schema_extra={"argument": True},
    )
    allow_breaking: bool = False


def _generate_unpinned_specifier(
    requirement: requirements.Requirement,
    *,
    is_frozen: bool,
) -> str:
    if is_frozen:
        return str(requirement.specifier)

    pkg_version = version.Version(str(requirement.specifier).lstrip("="))

    if not pkg_version.major:
        return ">=0.{0},<0.{1}".format(pkg_version.minor, pkg_version.minor + 1)

    return ">={0},<{1}".format(pkg_version.major, pkg_version.major + 1)


def _generate_unpinned_breaking_specifier(
    requirement: requirements.Requirement,
    *,
    is_frozen: bool,
) -> str:
    if is_frozen:
        return str(requirement.specifier)

    return ""


async def _unpin(app: application.Application[_UnpinSettings]) -> None:
    requirements_comments = await _parse_requirements_file(
        app.settings.requirements_path,
    )

    await _write_requirements_file(
        app.settings.requirements_path,
        (
            _generate_requirements_line(
                requirement_comment,
                _generate_unpinned_breaking_specifier
                if app.settings.allow_breaking
                else _generate_unpinned_specifier,
            )
            for requirement_comment in sorted(
                requirements_comments,
                key=lambda req: req[0].name.casefold(),
            )
        ),
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="python-dependencies", cli_tool=True)

    entrypoint.enter_with_commands(
        application.Command(
            name="outdated",
            callback=_outdated,
            settings_class=_OutdatedSettings,
        ),
        application.Command(
            name="pin",
            callback=_pin,
            settings_class=_PinSettings,
        ),
        application.Command(
            name="unpin",
            callback=_unpin,
            settings_class=_UnpinSettings,
        ),
    )
