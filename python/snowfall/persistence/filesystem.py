import hashlib
import pathlib
import zipfile

import aiofiles


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
