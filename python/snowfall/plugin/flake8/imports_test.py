import ast

from snowfall.plugin.flake8 import imports


def test_imports_ok() -> None:
    visitor = imports.Visitor("snowfall.stdlib.persistence.redis")
    tree = ast.parse("import aioredis")

    visitor.visit(tree)

    assert not visitor.errors


def test_imports_nok() -> None:
    visitor = imports.Visitor("foobar")
    tree = ast.parse("import aioredis")

    visitor.visit(tree)

    assert len(visitor.errors) == 1
