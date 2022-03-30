import ast

from snowfall.plugin.flake8 import plugin

PLUGIN_NAME = "snowfall-immutability"
PLUGIN_VERSION = "1.0.0"

SF10 = "SF10 All dataclasses should be frozen."


class Visitor(plugin.Visitor):
    def visit_ClassDef(self, class_def: ast.ClassDef) -> None:  # noqa: N802
        for node in (*class_def.bases, *class_def.decorator_list):
            if self._get_fullname(node) == "dataclasses.dataclass":
                self._ensure_dataclass_is_frozen(node)

        self.generic_visit(class_def)

    def _ensure_dataclass_is_frozen(
        self,
        node: ast.AST,
    ) -> None:
        if not isinstance(node, ast.Call):
            self.errors.append(plugin.Error(node.lineno, node.col_offset, SF10))
            return

        for keyword in node.keywords:
            if keyword.arg != "frozen":
                continue

            if not isinstance(keyword.value, ast.Constant):
                continue

            if keyword.value.value is True:
                return

        self.errors.append(plugin.Error(node.lineno, node.col_offset, SF10))


class Plugin(plugin.Plugin):
    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    visitor = Visitor
