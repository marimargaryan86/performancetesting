from collections.abc import Mapping
from typing import ClassVar, Literal, Protocol, TypeAlias

_DependencyTuple: TypeAlias = tuple[str, str]
Dependencies: TypeAlias = set[_DependencyTuple]
Environments: TypeAlias = set[Literal["development", "sandbox", "production"]]
ResolvedDependencies: TypeAlias = Mapping[_DependencyTuple, tuple[str, int]]


class Verifier(Protocol):
    dependencies: ClassVar[Dependencies]
    environments: ClassVar[Environments]

    async def run(self, environment: str, dependencies: ResolvedDependencies) -> None:
        """Run the verifier."""
