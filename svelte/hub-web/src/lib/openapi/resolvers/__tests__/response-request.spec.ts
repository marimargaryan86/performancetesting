import { describe, it, expect } from "vitest";
import { resolveRequest, resolveResponse, resolveResponses } from "../response-request";
import type { OpenAPIObject } from "../../openapi/types";
import Repository from "../../repository";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {},
} satisfies OpenAPIObject;

describe("resolveResponse", () => {
  it("Should resolve a response", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveResponse(
        {
          description: "A response",
        },
        repository,
      ),
    ).resolves.toEqual({});
    await expect(
      resolveResponse(
        {
          description: "A response",
          content: {
            "application/json": {
              schema: {
                type: "boolean",
              },
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      content: {
        "application/json": {
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
    });
    await expect(
      resolveResponse(
        {
          description: "A response",
          content: {
            "application/json": {
              schema: {
                type: "boolean",
              },
            },
          },
          headers: {
            foo: {
              schema: {
                type: "number",
              },
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      content: {
        "application/json": {
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
      headers: {
        foo: {
          in: "header",
          name: "foo",
          required: false,
          schema: {
            read: "number",
            write: "number",
          },
        },
      },
    });
  });
});

describe("resolveRequest", () => {
  it("Should resolve a request", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveRequest(
        {
          content: {},
        },
        repository,
      ),
    ).resolves.toEqual({
      content: {},
      required: false,
    });
    await expect(
      resolveRequest(
        {
          content: {
            "application/json": {
              schema: {
                type: "array",
                items: {
                  type: "string",
                },
              },
            },
          },
          required: true,
        },
        repository,
      ),
    ).resolves.toEqual({
      content: {
        "application/json": {
          schema: {
            read: "(string)[]",
            write: "(string)[]",
          },
        },
      },
      required: true,
    });
  });
});

describe("resolveResponses", () => {
  it("Should resolve responses", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveResponses({}, repository)).resolves.toEqual({});
    await expect(
      resolveResponses(
        {
          200: {
            description: "A response",
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      "200": {},
    });
    await expect(
      resolveResponses(
        {
          200: {
            description: "A response",
            content: {
              "application/json": {
                schema: {
                  type: "boolean",
                },
              },
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      "200": {
        content: {
          "application/json": {
            schema: {
              read: "boolean",
              write: "boolean",
            },
          },
        },
      },
    });
  });
});
