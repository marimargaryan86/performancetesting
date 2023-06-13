import ast
from collections.abc import Iterator
from typing import NamedTuple


def resolve_fullname(node: ast.AST) -> str:
    match node:
        case ast.Attribute():
            fullname = "{0}.{1}".format(resolve_fullname(node.value), node.attr)
        case ast.Name():
            fullname = node.id
        case ast.Subscript():
            fullname = resolve_fullname(node.value)
        case ast.Call():
            fullname = resolve_fullname(node.func)
        case ast.BinOp():
            fullname = "typing.Union"
        case ast.Constant():
            fullname = str(node.value)
        case ast.Set():
            fullname = "typing.Set"
        case _:
            raise RuntimeError(
                "{0} on {1}:{2} is not a resolvable type".format(
                    type(node),
                    node.lineno,
                    node.col_offset,
                ),
            )

    return fullname


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
    visitor: type[Visitor]

    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        visitor = self.visitor()
        visitor.visit(self._tree)

        yield from (
            (line, column, message, type(self))
            for line, column, message in visitor.errors
        )
