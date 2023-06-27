import ast
import types
from collections.abc import Iterator

from snowfall.plugin.flake8 import plugin

PLUGIN_NAME = "snowfall-imports"
PLUGIN_VERSION = "1.0.0"

SF30 = "SF30 Found restricted import: not allowed to import {0} here"

_CALLEE_WHITELIST = types.MappingProxyType(
    {
        "redis.asyncio": frozenset(("snowfall.stdlib.persistence.redis.types",)),
    },
)


class Visitor(plugin.Visitor):
    def __init__(self, module: str):
        self._module = module
        super().__init__()

    def visit_Import(self, import_: ast.Import) -> None:  # noqa: N802
        for name in import_.names:
            self._enforce_callee_whitelist(import_, name.name)

        self.generic_visit(import_)

    def visit_ImportFrom(self, import_from: ast.ImportFrom) -> None:  # noqa: N802
        for name in import_from.names:
            self._enforce_callee_whitelist(
                import_from,
                "{0}.{1}".format(import_from.module, name.name),
            )

        self.generic_visit(import_from)

    def _enforce_callee_whitelist(self, node: ast.AST, import_: str) -> None:
        for callee, whitelisted in _CALLEE_WHITELIST.items():
            if not import_.startswith(callee):
                continue

            if any(module for module in whitelisted if self._module.startswith(module)):
                continue

            self.errors.append(
                plugin.Error(
                    node.lineno,
                    node.col_offset,
                    SF30.format(callee),
                ),
            )


class Plugin(plugin.Plugin):
    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    visitor = Visitor

    def __init__(self, tree: ast.Module, filename: str) -> None:
        super().__init__(tree)
        self._filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        module = self._filename.replace("/", ".").lstrip("python.").rstrip(".py")
        visitor = self.visitor(module)
        visitor.visit(self._tree)

        yield from (
            (line, column, message, type(self))
            for line, column, message in visitor.errors
        )
