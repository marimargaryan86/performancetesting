import ast
import contextlib
import types
from typing import Mapping

from snowfall.plugin.flake8 import plugin

PLUGIN_NAME = "snowfall-typing"
PLUGIN_VERSION = "1.0.0"

BANNED_ARG_TYPES = types.MappingProxyType(
    {
        "typing.Optional": "| None",
        "typing.Tuple": "tuple",
        "typing.Type": "type",
        "typing.Union": "|",
    },
)

MUTABLE_ARG_TYPES = types.MappingProxyType(
    {
        "collections.abc.MutableMapping": "typing.Mapping",
        "collections.abc.MutableSequence": "typing.Sequence",
        "collections.abc.MutableSet": "frozenset",
        "dict": "typing.Mapping",
        "list": "typing.Sequence",
        "set": "frozenset",
        "typing.Dict": "typing.Mapping",
        "typing.List": "typing.Sequence",
        "typing.MutableMapping": "typing.Mapping",
        "typing.MutableSequence": "typing.Sequence",
        "typing.MutableSet": "frozenset",
        "typing.Set": "frozenset",
    },
)

BANNED_RETURN_TYPES = types.MappingProxyType(
    {
        "typing.Dict": "dict",
        "typing.List": "list",
        "typing.Optional": "| None",
        "typing.Set": "set",
        "typing.Tuple": "tuple",
        "typing.Type": "type",
        "typing.Union": "|",
    },
)

SF20 = 'SF20 Found mutable argument type: {0} (use "{1}" instead)'
SF21 = 'SF21 Found forbidden return type: {0} (use "{1}" instead)'
SF22 = 'SF22 Found forbidden argument type: {0} (use "{1}" instead)'


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

    def _func_visitor(self, node: ast.AsyncFunctionDef | ast.FunctionDef) -> None:
        for arg in (*node.args.args, node.args.kwarg, node.args.vararg):
            if not arg or not arg.annotation:
                continue

            self._no_forbidden_type_hints(arg.annotation, MUTABLE_ARG_TYPES, SF20)
            self._no_forbidden_type_hints(arg.annotation, BANNED_ARG_TYPES, SF22)

        if not node.returns or isinstance(node.returns, ast.Constant):
            return

        self._no_forbidden_type_hints(node.returns, BANNED_RETURN_TYPES, SF21)

    def _no_forbidden_type_hints(
        self,
        node: ast.AST,
        banned: Mapping[str, str],
        error_msg: str,
    ) -> None:
        fullname = self._get_fullname(node)

        with contextlib.suppress(KeyError):
            self.errors.append(
                plugin.Error(
                    node.lineno,
                    node.col_offset,
                    error_msg.format(fullname, banned[fullname]),
                ),
            )

        if isinstance(node, ast.BinOp):
            self._no_forbidden_type_hints(node.left, banned, error_msg)
            self._no_forbidden_type_hints(node.right, banned, error_msg)
            return

        if not isinstance(node, ast.Subscript):
            return

        if isinstance(node.slice, ast.Constant):
            return

        if not isinstance(node.slice, ast.Tuple):
            self._no_forbidden_type_hints(node.slice, banned, error_msg)
            return

        self._handle_tuple(node.slice, banned, error_msg)

    def _handle_tuple(
        self,
        node: ast.Tuple,
        banned: Mapping[str, str],
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
