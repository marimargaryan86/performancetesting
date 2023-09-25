import contextlib
import pathlib
import re
import shutil
import tempfile
from collections.abc import Iterator, Sequence
from typing import TypeAlias

from snowfall.stdlib.persistence import filesystem

_Replacement: TypeAlias = tuple[re.Pattern[str] | str, str]


def _replace_in_file(
    path: pathlib.Path,
    replacements: Sequence[_Replacement],
) -> None:
    with path.open("r") as read_handle:
        file_content = read_handle.read()

        for find, replace in replacements:
            file_content = re.sub(
                find,
                replace,
                file_content,
            )

    with path.open("w") as write_handle:
        write_handle.write(file_content)


def _create_temporary_spec_file(
    temp_path: pathlib.Path,
    original_file: pathlib.Path,
) -> pathlib.Path:
    temp_folder_path = pathlib.Path(temp_path, original_file.parent.name)
    temp_folder_path.mkdir(parents=True, exist_ok=True)
    temp_spec_path = pathlib.Path(temp_folder_path, "openapi.json")
    shutil.copy(original_file, temp_spec_path)

    return temp_spec_path


@contextlib.contextmanager
def get_api_spec() -> Iterator[pathlib.Path]:
    with tempfile.TemporaryDirectory() as temp:
        temp_path = pathlib.Path(temp)
        client_api_spec_path = _create_temporary_spec_file(
            temp_path,
            filesystem.resource_path(
                "junction.client_api",
                "openapi.json",
            ),
        )
        mobile_api_spec_path = _create_temporary_spec_file(
            temp_path,
            filesystem.resource_path(
                "junction.mobile_api",
                "openapi.json",
            ),
        )

        _replace_in_file(
            client_api_spec_path,
            [
                (
                    r'"\$ref": "#/',
                    '"$ref": "./../client_api/openapi.json#/',
                ),
            ],
        )

        yield mobile_api_spec_path
