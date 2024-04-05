import { describe, it, expect } from "vitest";
import { resolveHeader, resolveHeaders, resolveParameter, resolveParameterAux } from "../parameter";
import type { OpenAPIObject } from "../../openapi/types";
import Repository from "../../repository";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {
    headers: {
      "foo-bar": {
        required: true,
        schema: {
          type: "string",
        },
      },
      "bar-baz": {
        schema: {
          type: "number",
        },
      },
      "foo-bar-2": {
        $ref: "#/components/headers/foo-bar",
      },
      "foo-bar-3": {
        $ref: "#/components/headers/foo-bar",
      },
    },
    parameters: {
      foo: {
        in: "path",
        name: "foo",
        required: true,
        schema: {
          type: "string",
        },
      },
      bar: {
        in: "query",
        name: "bar",
        schema: {
          type: "number",
        },
      },
      baz: {
        in: "cookie",
        name: "baz",
        content: {
          "application/json": {
            schema: {
              type: "boolean",
            },
          },
        },
      },
    },
  },
} satisfies OpenAPIObject;

describe("resolveParameterAux", () => {
  it("Should resolve a parameter", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveParameterAux(openApi.components.parameters.foo, repository),
    ).resolves.toEqual({
      in: "path",
      name: "foo",
      required: true,
      schema: {
        read: "string",
        write: "string",
      },
    });
    await expect(
      resolveParameterAux(openApi.components.parameters.bar, repository),
    ).resolves.toEqual({
      in: "query",
      name: "bar",
      required: false,
      schema: {
        read: "number",
        write: "number",
      },
    });
    await expect(
      resolveParameterAux(openApi.components.parameters.baz, repository),
    ).resolves.toEqual({
      in: "cookie",
      name: "baz",
      required: false,
      content: {
        "application/json": {
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
    });
  });
});

describe("resolveParameter", () => {
  it("Should resolve a parameter", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveParameter(openApi.components.parameters.foo, repository)).resolves.toEqual({
      in: "path",
      name: "foo",
      required: true,
      schema: {
        read: "string",
        write: "string",
      },
    });
    await expect(resolveParameter(openApi.components.parameters.bar, repository)).resolves.toEqual({
      in: "query",
      name: "bar",
      required: false,
      schema: {
        read: "number",
        write: "number",
      },
    });
    await expect(resolveParameter(openApi.components.parameters.baz, repository)).resolves.toEqual({
      in: "cookie",
      name: "baz",
      required: false,
      content: {
        "application/json": {
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
    });
  });
});

describe("resolveHeader", () => {
  it("Should resolve a header", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveHeader(openApi.components.headers["foo-bar"], "foo-bar", repository),
    ).resolves.toEqual({
      in: "header",
      name: "foo-bar",
      required: true,
      schema: {
        read: "string",
        write: "string",
      },
    });
    await expect(
      resolveHeader(openApi.components.headers["bar-baz"], "baz", repository),
    ).resolves.toEqual({
      in: "header",
      name: "baz",
      required: false,
      schema: {
        read: "number",
        write: "number",
      },
    });
    await expect(
      resolveHeader(openApi.components.headers["foo-bar-2"], "foobar", repository),
    ).resolves.toEqual({
      in: "header",
      name: "foobar",
      required: true,
      schema: {
        read: "string",
        write: "string",
      },
    });
    await expect(
      resolveHeader(openApi.components.headers["foo-bar-3"], "foobar", repository),
    ).resolves.toEqual({
      in: "header",
      name: "foobar",
      required: true,
      schema: {
        read: "string",
        write: "string",
      },
    });
  });
});

describe("resolveHeaders", () => {
  it("Should headers", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveHeaders({}, repository)).resolves.toEqual({});
    await expect(
      resolveHeaders(
        {
          foo: openApi.components.headers["foo-bar"],
          bar: openApi.components.headers["bar-baz"],
          baz: openApi.components.headers["foo-bar-2"],
        },
        repository,
      ),
    ).resolves.toEqual({
      bar: {
        in: "header",
        name: "bar",
        required: false,
        schema: {
          read: "number",
          write: "number",
        },
      },
      baz: {
        in: "header",
        name: "baz",
        required: true,
        schema: {
          read: "string",
          write: "string",
        },
      },
      foo: {
        in: "header",
        name: "foo",
        required: true,
        schema: {
          read: "string",
          write: "string",
        },
      },
    });
  });
});
