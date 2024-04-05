import { describe, it, expect } from "vitest";
import { resolveOperation, resolvePathItem, resolvePaths } from "../path";
import type { OpenAPIObject } from "../../openapi/types";
import Repository from "../../repository";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/bar": {
      $ref: "#/paths/~1foo",
    },
    "/baz": {
      $ref: "#/paths/~1foo",
    },
    "/foo": {
      parameters: [
        {
          in: "query",
          name: "foo-bar",
          schema: {
            type: "boolean",
          },
        },
      ],
      get: {
        responses: {
          200: {
            description: "An operation",
            content: {
              "application/json": {
                schema: {
                  type: "string",
                },
              },
            },
          },
        },
      },
      post: {
        parameters: [
          {
            in: "query",
            name: "baz",
            schema: {
              type: "number",
            },
          },
        ],
        requestBody: {
          content: {
            "application/json": {
              schema: {
                type: "boolean",
              },
            },
          },
        },
        responses: {
          200: {
            description: "An operation",
          },
        },
      },
    },
  },
} satisfies OpenAPIObject;

describe("resolveOperation", () => {
  it("Should resolve an operation", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveOperation(openApi.paths["/foo"].get, [], repository)).resolves.toEqual({
      parameters: {},
      responses: {
        "200": {
          content: {
            "application/json": {
              schema: {
                read: "string",
                write: "string",
              },
            },
          },
        },
      },
    });

    await expect(resolveOperation(openApi.paths["/foo"].post, [], repository)).resolves.toEqual({
      parameters: {
        query: {
          baz: {
            in: "query",
            name: "baz",
            required: false,
            schema: {
              read: "number",
              write: "number",
            },
          },
        },
      },
      requestBody: {
        content: {
          "application/json": {
            schema: {
              read: "boolean",
              write: "boolean",
            },
          },
        },
        required: false,
      },
      responses: {
        "200": {},
      },
    });
  });
});

describe("resolvePathItem", () => {
  it("Should resolve a path item", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolvePathItem(openApi.paths["/foo"], repository)).resolves.toEqual({
      get: {
        parameters: {
          query: {
            "foo-bar": {
              in: "query",
              name: "foo-bar",
              required: false,
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
          },
        },
        responses: {
          "200": {
            content: {
              "application/json": {
                schema: {
                  read: "string",
                  write: "string",
                },
              },
            },
          },
        },
      },
      post: {
        parameters: {
          query: {
            "foo-bar": {
              in: "query",
              name: "foo-bar",
              required: false,
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
            baz: {
              in: "query",
              name: "baz",
              required: false,
              schema: {
                read: "number",
                write: "number",
              },
            },
          },
        },
        requestBody: {
          content: {
            "application/json": {
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
          },
          required: false,
        },
        responses: {
          "200": {},
        },
      },
    });
  });
});

describe("resolvePaths", () => {
  it("Should resolve paths", async () => {
    const repository = new Repository("./openapi.json", openApi);

    const pathItem = {
      get: {
        parameters: {
          query: {
            "foo-bar": {
              in: "query",
              name: "foo-bar",
              required: false,
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
          },
        },
        responses: {
          "200": {
            content: {
              "application/json": {
                schema: {
                  read: "string",
                  write: "string",
                },
              },
            },
          },
        },
      },
      post: {
        parameters: {
          query: {
            "foo-bar": {
              in: "query",
              name: "foo-bar",
              required: false,
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
            baz: {
              in: "query",
              name: "baz",
              required: false,
              schema: {
                read: "number",
                write: "number",
              },
            },
          },
        },
        requestBody: {
          content: {
            "application/json": {
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
          },
          required: false,
        },
        responses: {
          "200": {},
        },
      },
    };

    await expect(resolvePaths(openApi.paths, repository)).resolves.toEqual({
      "/foo": pathItem,
      "/bar": pathItem,
      "/baz": pathItem,
    });
  });
});
