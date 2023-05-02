import pathlib
import sys
import tokenize
from collections import defaultdict
from collections.abc import Sequence
from typing import BinaryIO

_ENTRY_POINTS = (":", "None")


def _validate_service(
    path: pathlib.Path,
    base_dir: pathlib.Path,
    nomad_files: Sequence[pathlib.Path],
) -> bool:
    build_file = base_dir / "BUILD"
    relative_path = str(build_file).removeprefix(str(path.parent))

    if not build_file.exists():
        _log_error("{0}: file does not exist".format(relative_path))
        return True

    with open(build_file, "rb") as build_fp:
        relevant_line = _parse_build_file(build_fp)

    if not relevant_line:
        _log_error(
            '{0}: file is missing a "nomad_template" target'.format(
                relative_path,
            ),
        )
        return True

    return _validate_build_file(relevant_line, frozenset(nomad_files), relative_path)


def _parse_build_file(build_fp: BinaryIO) -> str | None:
    all_tokens = tokenize.tokenize(build_fp.readline)

    for token in all_tokens:
        if token.type == tokenize.NAME and token.string == "nomad_template":
            break
    else:
        return None

    relevant_tokens = [next(all_tokens)]
    open_no = 1

    while open_no > 0:
        next_token = next(all_tokens)

        match next_token.string:
            case "(":
                open_no += 1
            case ")":
                open_no -= 1
            case "\n":
                continue

        relevant_tokens.append(next_token)

    return "".join([relevant_token.string for relevant_token in relevant_tokens])


def _validate_build_file(
    build_line: str,
    nomad_files: frozenset[pathlib.Path],
    relative_path: str,
) -> bool:
    errors = False
    is_built_service = False

    for nomad_file in nomad_files:
        tests = [
            '"{0}"'.format(nomad_file.stem) in build_line,
            '"{0}#'.format(nomad_file.stem) in build_line,
        ]

        if not any(tests):
            errors = True
            _log_error(
                "{0}: {1} is not configured".format(
                    relative_path,
                    nomad_file.name,
                ),
            )
            continue

        with open(nomad_file) as nomad_fp:
            if "docker_image" in nomad_fp.read():
                is_built_service = True

    if is_built_service and all(string not in build_line for string in _ENTRY_POINTS):
        errors = True
        _log_error(
            "{0}: service entry point missing".format(relative_path),
        )

    return errors


def _log_error(msg: str) -> None:
    print(msg, file=sys.stderr)  # noqa: WPS421


def _main(root_path: pathlib.Path) -> bool:
    errors = False
    dirs = defaultdict[pathlib.Path, list[pathlib.Path]](list)

    for nomad_file in root_path.rglob("*.nomad"):
        dirs[nomad_file.parent].append(nomad_file)

    for base_dir, nomad_files in dirs.items():
        if _validate_service(root_path, base_dir, nomad_files):
            errors = True

    return errors


if len(sys.argv) != 2:
    _log_error(
        "usage: {0} path/to/nomad/root/".format(sys.argv[0]),
    )
    sys.exit(1)

if _main(pathlib.Path(sys.argv[1])):
    sys.exit(1)
