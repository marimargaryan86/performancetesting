from __future__ import annotations

import contextlib
import hashlib
import os
import pathlib
import pkgutil
import zipfile
from collections.abc import AsyncGenerator
from importlib import _bootstrap, util  # type: ignore[attr-defined] # noqa: WPS450
from sys import modules
from typing import Any
from urllib import parse as urllib_parse

import aiofiles
import orjson
import s3fs
from fsspec import asyn
from fsspec.implementations import memory

from snowfall.stdlib import string

_PkgLoaderReturn = list[dict[str, Any]] | dict[str, Any]  # noqa: WPS221


class UnsupportedStorageSchemeError(Exception):
    """Raised when an unsupported storage scheme is used."""


class NotFoundError(Exception):
    """Raised when a resource is not found."""


class Storage(object):
    def __init__(
        self,
        filesystem: asyn.AsyncFileSystem,
        base_path: pathlib.Path | None = None,
    ):
        self._filesystem = filesystem
        self._base_path = base_path or pathlib.Path("")

    async def put(self, path: pathlib.Path, file_contents: bytes) -> None:
        file_path = self._base_path.joinpath(path)

        try:
            await self._filesystem._pipe(str(file_path), file_contents)  # noqa: WPS437
        except FileNotFoundError as err:
            raise NotFoundError() from err

    async def get(self, path: pathlib.Path) -> bytes:
        file_path = self._base_path.joinpath(path)

        try:
            open_file = await self._filesystem.open_async(str(file_path), "rb")
        except FileNotFoundError as file_open_error:
            raise NotFoundError() from file_open_error

        async with open_file as file_handle:
            try:
                return await file_handle.read()
            except FileNotFoundError as file_read_error:
                raise NotFoundError() from file_read_error

    @classmethod
    @contextlib.asynccontextmanager
    async def from_dsn(cls, dsn: str) -> AsyncGenerator[Storage, None]:
        filesystem, base_path = cls._parse_dsn_to_instance(dsn)

        try:
            yield cls(filesystem=filesystem, base_path=base_path)
        finally:
            if isinstance(filesystem, s3fs.S3FileSystem):
                s3fs.S3FileSystem.close_session(asyn.get_loop(), filesystem.s3)

    @classmethod
    def _parse_dsn_to_instance(
        cls,
        dsn: str,
    ) -> tuple[asyn.AsyncFileSystem, pathlib.Path | None]:
        parsed_dsn = urllib_parse.urlparse(dsn)

        if parsed_dsn.scheme == "memory":
            return _AsyncMemoryFileSystem(), pathlib.Path(string.random(24))

        if parsed_dsn.scheme == "s3":
            return s3fs.S3FileSystem(
                asynchronous=True,
                key=parsed_dsn.username,
                secret=urllib_parse.unquote(str(parsed_dsn.password)),
            ), pathlib.Path(parsed_dsn.path.strip("/"))

        raise UnsupportedStorageSchemeError(
            "{0} is an unsupported storage scheme.".format(parsed_dsn.scheme),
        )


class PkgLoader(object):
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
        return pathlib.Path(os.path.dirname(str(mod.__file__)))
    except AttributeError as err:
        raise RuntimeError() from err


def resource_path(package: str, resource: str) -> pathlib.Path:
    """Based on pkgutil.get_data()."""
    parts = resource.split("/")

    try:
        parts.insert(0, str(package_path(package)))
    except AttributeError as err:
        raise RuntimeError() from err

    return pathlib.Path(os.path.join(*parts))


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


class _AsyncMemoryFile(asyn.AbstractAsyncStreamedFile):
    def __init__(self, file_handle: memory.MemoryFile):
        self._file_handle = file_handle

    async def read(self, length: int | None = -1) -> bytes:
        return self._file_handle.read(length)

    async def write(self, data: bytes) -> int:  # noqa: WPS110
        return self._file_handle.write(data)

    async def _fetch_range(self, start: int, end: int) -> Any:
        raise NotImplementedError

    async def _upload_chunk(self, final: bool = False) -> Any:  # noqa: FBT001,FBT002
        raise NotImplementedError


class _AsyncMemoryFileSystem(  # noqa: WPS214
    memory.MemoryFileSystem,
    asyn.AsyncFileSystem,
):
    async def open_async(
        self,
        path: str,
        mode: str = "rb",
        **kwargs: Any,
    ) -> _AsyncMemoryFile:
        if "b" not in mode or kwargs.get("compression"):
            raise ValueError

        return _AsyncMemoryFile(self.open(path, mode, **kwargs))

    async def _rm_file(self, path: str, **kwargs: Any) -> None:
        return self.rm_file(path)

    async def _cp_file(self, path1: str, path2: str, **kwargs: Any) -> None:
        return self.cp_file(path1, path2, **kwargs)

    async def _pipe_file(
        self,
        path: str,
        value: bytes,  # noqa: WPS110
        **kwargs: Any,
    ) -> memory.MemoryFile:
        return self.pipe_file(path, value, **kwargs)

    async def _cat_file(
        self,
        path: str,
        start: int | None = None,
        end: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        return self.cat_file(path, start, end, **kwargs)

    async def _put_file(self, lpath: str, rpath: str, **kwargs: Any) -> None:
        return self.put_file(lpath, rpath, **kwargs)

    async def _get_file(self, rpath: str, lpath: str, **kwargs: Any) -> None:
        return self.get_file(rpath, lpath, **kwargs)

    async def _info(self, path: str, **kwargs: Any) -> dict[str, Any]:  # noqa: WPS110
        return self.info(path, **kwargs)

    async def _ls(
        self,
        path: str,
        detail: bool = True,  # noqa: FBT001,FBT002
        **kwargs: Any,
    ) -> list[str]:
        return self.ls(path, detail, **kwargs)
