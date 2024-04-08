import pytest

from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


@pytest.fixture()
async def schema_generator() -> SchemaGenerator:
    return SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
        health=False,
    )
