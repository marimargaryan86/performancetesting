import itertools
from collections import defaultdict
from collections.abc import Iterable
from typing import Generic

from snowfall.stdlib.h3 import MappedValue


class IdMappingRepository(Generic[MappedValue]):
    def __init__(
        self,
        mapping: Iterable[MappedValue],
    ):
        self._mapping: dict[str, list[MappedValue]] = defaultdict(list)
        for coordinates_item in mapping:
            self._mapping[coordinates_item.identifier].append(coordinates_item)

    def find_mapped_values(
        self,
        identifiers: Iterable[str],
    ) -> set[MappedValue]:
        return set(
            itertools.chain.from_iterable(
                self._mapping[identifier]
                for identifier in identifiers
                if identifier in self._mapping
            ),
        )
