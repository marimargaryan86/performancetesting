import ast
from typing import Union

from snowfall.plugin.flake8 import plugin

PLUGIN_NAME = "snowfall-typing"
PLUGIN_VERSION = "1.0.0"

BANNED_ARG_TYPES = frozenset(
    (
        "dict",
        "list",
        "set",
        "typing.Dict",
        "typing.List",
        "typing.Set",
    ),
)

BANNED_RETURN_TYPES: frozenset[str] = frozenset()

SF20 = "SF20 Found forbidden argument type: {0}"
SF21 = "SF21 Found forbidden return type: {0}"


class Visitor(plugin.Visitor):
    def visit_AsyncFunctionDef(  # noqa: N802
        self,
        async_function_def: ast.AsyncFunctionDef,
    ) -> None:
        self._func_visitor(async_function_def)
        self.generic_visit(async_function_def)

    def visit_FunctionDef(self, function_def: ast.FunctionDef) -> None:  # noqa: N802
        self._func_visitor(function_def)
        self.generic_visit(function_def)

    def _func_visitor(self, node: Union[ast.AsyncFunctionDef, ast.FunctionDef]) -> None:
        for arg in (*node.args.args, node.args.kwarg, node.args.vararg):
            if not arg or not arg.annotation:
                continue

            self._no_forbidden_type_hints(arg.annotation, BANNED_ARG_TYPES, SF20)

        if not node.returns or isinstance(node.returns, ast.Constant):
            return

        self._no_forbidden_type_hints(node.returns, BANNED_RETURN_TYPES, SF21)

    def _no_forbidden_type_hints(
        self,
        node: ast.AST,
        banned: frozenset[str],
        error_msg: str,
    ) -> None:
        fullname = self._get_fullname(node)

        if fullname in banned:
            self.errors.append(
                plugin.Error(node.lineno, node.col_offset, error_msg.format(fullname)),
            )

        if not isinstance(node, ast.Subscript):
            return

        if isinstance(node.slice, ast.Constant):
            return

        if not isinstance(node.slice, ast.Tuple):
            self._no_forbidden_type_hints(node.slice, banned, error_msg)
            return

        self._handle_slice(node.slice, banned, error_msg)

    def _handle_slice(
        self,
        node: ast.Tuple,
        banned: frozenset[str],
        error_msg: str,
    ) -> None:
        for elt in node.elts:
            if isinstance(elt, ast.Constant):
                continue

            if not isinstance(elt, ast.List):
                self._no_forbidden_type_hints(elt, banned, error_msg)
                continue

            for subelt in elt.elts:
                self._no_forbidden_type_hints(subelt, banned, error_msg)


class Plugin(plugin.Plugin):
    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    visitor = Visitor
