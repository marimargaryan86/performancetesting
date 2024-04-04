from snowfall.project.fti.service.bigxtra_api.routes import examples
from snowfall.project.fti.service.bigxtra_api.schemas import SchemaGenerator


class TestSchemaGenerator:
    async def test_generator(self, schema_generator: SchemaGenerator) -> None:
        route = SchemaGenerator.to_route(None, "/examples", examples.Examples)
        schema = schema_generator.get_schema([route])

        expected_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Example API", "version": "1.0"},
            "paths": {
                "/examples": {
                    "get": {
                        "description": "Use this endpoint to get Examples",
                        "summary": "List examples",
                        "responses": {
                            201: {
                                "description": "Successful Response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "additionalProperties": False,
                                            "properties": {
                                                "examples": {
                                                    "items": {
                                                        "$ref": "#/components/schemas/ExampleModel",
                                                    },
                                                    "title": "Examples",
                                                    "type": "array",
                                                },
                                            },
                                            "required": ["examples"],
                                            "title": "ExamplesModel",
                                            "type": "object",
                                        },
                                    },
                                },
                            },
                        },
                        "parameters": [
                            {
                                "name": "cursor",
                                "in": "query",
                                "schema": {
                                    "default": "",
                                    "description": "Pagination cursor that defines your place in the list.",
                                    "example": "MTogIjAwNGNjOTQ5LWQ4NjYtNWM1MS05MmYxLTRjMTUxYTA4YzBjOSIgMjogIjM0ZmQwZmUzMDRhYjY3ZmIiIDM6ICIyZjhiZDU3MDljMjI3Mjg0Ig%3D%3D",
                                    "title": "Cursor",
                                    "type": "string",
                                },
                                "description": "Pagination cursor that defines your place in the list.",
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {
                                    "default": 20,
                                    "description": "A limit on the number of objects to be returned, between 1 and 100.",
                                    "example": 20,
                                    "maximum": 100,
                                    "minimum": 1,
                                    "title": "Limit",
                                    "type": "integer",
                                },
                                "description": "A limit on the number of objects to be returned, between 1 and 100.",
                            },
                        ],
                    },
                    "post": {
                        "description": "Use this endpoint to create an Example",
                        "summary": "Create example",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "additionalProperties": False,
                                        "properties": {
                                            "exampleId": {
                                                "example": "04f83af5-10bb-4a0f-1881-03e1e690f0f5",
                                                "format": "uuid",
                                                "readOnly": True,
                                                "title": "Exampleid",
                                                "type": "string",
                                            },
                                            "exampleNumber": {
                                                "example": 20,
                                                "title": "Examplenumber",
                                                "type": "integer",
                                            },
                                            "exampleDetails": {
                                                "title": "Exampledetails",
                                                "type": "string",
                                            },
                                        },
                                        "required": [
                                            "exampleId",
                                            "exampleNumber",
                                            "exampleDetails",
                                        ],
                                        "title": "ExampleModel",
                                        "type": "object",
                                    },
                                },
                            },
                        },
                        "responses": {
                            204: {
                                "description": "Successful Response",
                                "content": {"application/json": {"schema": {}}},
                            },
                        },
                        "parameters": [],
                    },
                },
            },
            "components": {
                "schemas": {
                    "ExampleModel": {
                        "additionalProperties": False,
                        "properties": {
                            "exampleId": {
                                "example": "04f83af5-10bb-4a0f-1881-03e1e690f0f5",
                                "format": "uuid",
                                "readOnly": True,
                                "title": "Exampleid",
                                "type": "string",
                            },
                            "exampleNumber": {
                                "example": 20,
                                "title": "Examplenumber",
                                "type": "integer",
                            },
                            "exampleDetails": {
                                "title": "Exampledetails",
                                "type": "string",
                            },
                        },
                        "required": ["exampleId", "exampleNumber", "exampleDetails"],
                        "title": "ExampleModel",
                        "type": "object",
                    },
                },
            },
        }

        assert schema == expected_schema
