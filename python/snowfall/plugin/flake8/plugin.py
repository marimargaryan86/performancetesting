import ast
from collections.abc import Iterator
from typing import NamedTuple, Type


def resolve_fullname(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return "{0}.{1}".format(resolve_fullname(node.value), node.attr)

    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Subscript):
        return resolve_fullname(node.value)

    if isinstance(node, ast.Call):
        return resolve_fullname(node.func)

    if isinstance(node, ast.BinOp):
        return "typing.Union"

    raise RuntimeError(
        "{0} on {1}:{2} is not a resolvable type".format(
            type(node),
            node.lineno,
            node.col_offset,
        ),
    )


class Error(NamedTuple):
    lineno: int
    col_offset: int
    msg: str


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[Error] = []
        self.imports: dict[str, str] = {}

    def visit_Import(self, import_: ast.Import) -> None:  # noqa: N802
        for name in import_.names:
            self.imports[name.asname or name.name] = name.name

        self.generic_visit(import_)

    def visit_ImportFrom(self, import_from: ast.ImportFrom) -> None:  # noqa: N802
        for name in import_from.names:
            self.imports[name.asname or name.name] = "{0}.{1}".format(
                import_from.module,
                name.name,
            )

        self.generic_visit(import_from)

    def _get_fullname(self, node: ast.AST) -> str:
        parts = resolve_fullname(node).split(".")
        overflow = []

        while parts and ".".join(parts) not in self.imports:
            overflow.append(parts.pop())

        try:
            return "{0}.{1}".format(
                self.imports[".".join(parts)],
                ".".join(overflow),
            ).rstrip(".")
        except KeyError:
            return ".".join(overflow)


class Plugin(object):
    visitor: Type[Visitor]

    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = self.visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:  # noqa: WPS526
            yield line, col, msg, type(self)
