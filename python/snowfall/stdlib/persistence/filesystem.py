import abc
import hashlib
import pathlib
import pkgutil
import zipfile
from importlib import _bootstrap, util  # type: ignore[attr-defined] # noqa: WPS450
from os import path
from sys import modules
from typing import Any, Union

import aiofiles
import orjson

_PkgLoaderReturn = Union[
    list[dict[str, Any]],
    dict[str, Any],
]


class Loader(abc.ABC):
    @abc.abstractmethod
    def load(self, ref: str) -> _PkgLoaderReturn:
        """Load the file."""


class FileLoader(Loader):
    def load(self, ref: str) -> _PkgLoaderReturn:
        try:
            with open(ref) as file_handle:
                return orjson.loads(file_handle.read())
        except FileNotFoundError as err:
            raise FileNotFoundError(
                "Schema file '{ref}' not found.".format(ref=ref),
            ) from err


class PkgLoader(Loader):
    def __init__(self, pkg: str):
        self._pkg = pkg

    def load(self, ref: str) -> _PkgLoaderReturn:
        try:
            file_content = pkgutil.get_data(self._pkg, ref)
        except (AttributeError, OSError) as err:
            raise FileNotFoundError(
                "Schema file '{ref}' not found.".format(ref=ref),
            ) from err

        if not file_content:
            raise FileNotFoundError(
                "Schema file '{ref}' not found.".format(ref=ref),
            )

        return orjson.loads(file_content)


def package_path(package: str) -> pathlib.Path:
    """Based on pkgutil.get_data()."""
    spec = util.find_spec(package)

    if spec is None:
        raise RuntimeError()

    mod = modules.get(package) or _bootstrap._load(spec)  # noqa: WPS437

    if mod is None:
        raise RuntimeError()

    try:
        return pathlib.Path(path.dirname(str(mod.__file__)))
    except AttributeError as err:
        raise RuntimeError() from err


def resource_path(package: str, resource: str) -> pathlib.Path:
    """Based on pkgutil.get_data()."""
    parts = resource.split("/")

    try:
        parts.insert(0, str(package_path(package)))
    except AttributeError as err:
        raise RuntimeError() from err

    return pathlib.Path(path.join(*parts))


async def hash_file(filepath: pathlib.Path, chunk_size: int = 1024) -> str:
    checksum = hashlib.sha384()

    async with aiofiles.open(str(filepath), "rb") as pointer:
        while True:
            chunk = await pointer.read(chunk_size)

            if not chunk:
                break

            checksum.update(chunk)

    return checksum.hexdigest()


def unzip_file(feed_path: pathlib.Path) -> set[pathlib.Path]:
    with zipfile.ZipFile(str(feed_path)) as zip_handle:
        if zip_handle.testzip():
            raise RuntimeError(
                "{filename} is not a valid zip file".format(filename=str(feed_path)),
            )

        zip_handle.extractall(str(feed_path.parent))

        return {
            feed_path.parent.joinpath(file_in_zip.filename)
            for file_in_zip in zip_handle.filelist
        }
