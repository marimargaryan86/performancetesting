import enum
import pathlib
import sys
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import NamedTuple, TypedDict

import httpx
import orjson
from packaging import requirements, version


class Colors(enum.StrEnum):
    blue = "\033[94m"
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    reset = "\033[0m"


class Status(enum.IntEnum):
    frozen = 0
    breaking = 1
    latest = 2
    available = 3


_status_to_color = MappingProxyType(
    {
        Status.frozen: Colors.blue,
        Status.breaking: Colors.red,
        Status.latest: Colors.green,
        Status.available: Colors.yellow,
    },
)


class Dependency(NamedTuple):
    package: requirements.Requirement
    our_version: version.Version
    their_version: version.Version
    status: Status
    comment: str | None


def _log_error(msg: str) -> None:
    print(msg, file=sys.stderr)  # noqa: T201,WPS421


def _print_dependencies(dependencies: frozenset[Dependency]) -> None:
    longest_package_name = max(len(dep.package.name) for dep in dependencies)
    longest_our_version = max(len(str(dep.our_version)) for dep in dependencies)
    longest_their_version = max(len(str(dep.their_version)) for dep in dependencies)

    for dep in sorted(dependencies, key=lambda pkg: pkg.package.name.casefold()):
        _log_error(
            "{0}{1}{2}".format(
                _status_to_color[dep.status],
                "\t".join(
                    [
                        dep.package.name.ljust(longest_package_name, " "),
                        str(dep.our_version).ljust(longest_our_version, " "),
                        str(dep.their_version).ljust(longest_their_version, " "),
                    ],
                ),
                Colors.reset,
            ),
        )


def _is_breaking_change(ours: version.Version, theirs: version.Version) -> bool:
    if ours.major != theirs.major:
        return True

    if not ours.major and ours.minor != theirs.minor:
        return True

    return not ours.major and not ours.minor and ours.micro != theirs.micro


def _read_constraints_file(constraints_path: pathlib.Path) -> Mapping[str, str]:
    with constraints_path.open() as constraints_file:
        parsed_file = orjson.loads(
            constraints_file.read().split(
                "--- END PANTS LOCKFILE METADATA ---",
                maxsplit=1,
            )[1],
        )["locked_resolves"]

        return {
            package["project_name"]: package["version"]
            for resolve in parsed_file
            for package in resolve["locked_requirements"]
        }


def _write_requirements_file(
    requirements_path: pathlib.Path,
    dependencies: frozenset[Dependency],
) -> None:
    with requirements_path.open("wb") as requirements_file:
        for dep in sorted(dependencies, key=lambda pkg: pkg.package.name.casefold()):
            picked_version = dep.our_version

            if dep.status == Status.available:
                picked_version = dep.their_version

            line_str = dep.package.name

            if dep.package.extras:
                line_str += "[{0}]".format(",".join(list(dep.package.extras)))

            line_str += "=={0}".format(picked_version)

            if dep.comment:
                line_str += "  # {0}".format(dep.comment)

            requirements_file.write("{0}\n".format(line_str).encode())

        requirements_file.flush()


class _DependencyKwargs(TypedDict):
    package: requirements.Requirement
    our_version: version.Version
    their_version: version.Version
    comment: str | None


def _build_dependency(
    parts: Sequence[str],
    requirement: requirements.Requirement,
    our_version: version.Version,
    their_version: version.Version,
) -> Dependency:
    kwargs = _DependencyKwargs(
        package=requirement,
        our_version=our_version,
        their_version=their_version,
        comment=parts[1].strip() if len(parts) > 1 else None,
    )

    if len(parts) > 1 and "freeze" in parts[1]:
        return Dependency(**kwargs, status=Status.frozen)

    if our_version == their_version:
        return Dependency(**kwargs, status=Status.latest)

    if _is_breaking_change(our_version, their_version):
        return Dependency(**kwargs, status=Status.breaking)

    return Dependency(**kwargs, status=Status.available)


def _main() -> None:  # noqa: WPS210
    if len(sys.argv) != 3:
        _log_error(
            "usage: {0} path/to/requirements.txt path/to/constraints.txt".format(
                sys.argv[0],
            ),
        )
        sys.exit(1)

    versions = _read_constraints_file(pathlib.Path(sys.argv[2]))
    requirements_path = pathlib.Path(sys.argv[1])

    with requirements_path.open() as requirements_file:
        dependencies: set[Dependency] = set()

        for line in requirements_file:
            parts = line.strip().split("#", maxsplit=1)
            requirement = requirements.Requirement(parts[0])
            response = httpx.get(
                "https://pypi.org/pypi/{0}/json".format(requirement.name),
            )

            response.raise_for_status()

            dependencies.add(
                _build_dependency(
                    parts=parts,
                    requirement=requirement,
                    our_version=version.parse(
                        versions[requirement.name.lower().replace("_", "-")],
                    ),
                    their_version=version.parse(response.json()["info"]["version"]),
                ),
            )

    _print_dependencies(frozenset(dependencies))
    _write_requirements_file(requirements_path, frozenset(dependencies))


_main()
