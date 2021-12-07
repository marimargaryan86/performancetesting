import abc
import json
import pkgutil


class Loader(abc.ABC):
    @abc.abstractmethod
    def load(self, ref: str) -> dict:
        """Load the file."""


class FileLoader(Loader):
    def load(self, ref: str) -> dict:
        try:
            with open(ref) as file_handle:
                return json.load(file_handle)
        except FileNotFoundError as err:
            raise FileNotFoundError(
                "Schema file '{ref}' not found.".format(ref=ref),
            ) from err


class PkgLoader(Loader):
    def __init__(self, pkg: str):
        self._pkg = pkg

    def load(self, ref: str) -> dict:
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

        return json.loads(file_content)
