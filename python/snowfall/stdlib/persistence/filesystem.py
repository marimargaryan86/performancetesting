import abc
import hashlib
import pathlib
import pkgutil
import zipfile
from typing import Any

import aiofiles
import rapidjson


class Loader(abc.ABC):
    @abc.abstractmethod
    def load(self, ref: str) -> dict[str, Any]:
        """Load the file."""


class FileLoader(Loader):
    def load(self, ref: str) -> dict[str, Any]:
        try:
            with open(ref) as file_handle:
                return rapidjson.load(file_handle)
        except FileNotFoundError as err:
            raise FileNotFoundError(
                "Schema file '{ref}' not found.".format(ref=ref),
            ) from err


class PkgLoader(Loader):
    def __init__(self, pkg: str):
        self._pkg = pkg

    def load(self, ref: str) -> dict[str, Any]:
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

        return rapidjson.loads(file_content)


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
