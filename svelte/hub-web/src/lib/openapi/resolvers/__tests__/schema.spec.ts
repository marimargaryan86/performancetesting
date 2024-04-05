import { describe, it, expect } from "vitest";
import {
  resolveAdditionalProperties,
  resolveItems,
  resolvePolymorphism,
  resolveProperties,
  resolveSchema,
} from "../schema";
import type { OpenAPIObject, SchemaObject } from "../../openapi/types";
import Repository from "../../repository";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {
    schemas: {
      allOf: {
        type: "object",
        allOf: [
          {
            type: "object",
            properties: { foo: { type: "string", readOnly: true } },
            additionalProperties: false,
          },
          {
            type: "object",
            properties: { bar: { type: "number" }, baz: { type: "boolean", writeOnly: true } },
            additionalProperties: false,
          },
        ],
      },
      anyOf: {
        anyOf: [
          {
            type: "object",
            properties: { foo: { type: "string" } },
            additionalProperties: false,
          },
          {
            type: "object",
            properties: { bar: { type: "number" }, baz: { type: "boolean" } },
            additionalProperties: false,
          },
        ],
      },
      oneOf: {
        oneOf: [
          {
            type: "object",
            properties: { foo: { type: "string" } },
            additionalProperties: false,
          },
          {
            type: "object",
            properties: { bar: { type: "number" }, baz: { type: "boolean" } },
            additionalProperties: false,
          },
        ],
      },
      properties: {
        type: "object",
        required: ["foo", "bar"],
        properties: {
          foo: { type: "string" },
          bar: { type: "number", readOnly: true },
          baz: { type: "boolean", writeOnly: true },
        },
      },
      items: {
        type: "array",
        items: { type: "string" },
      },
      itemsComplicated: {
        type: "array",
        items: {
          allOf: [
            { type: "string", readOnly: true },
            { type: "number", writeOnly: true },
          ],
        },
      },
      null: { type: "null" },
      string: { type: "string" },
      number: { type: "number" },
      integer: { type: "number" },
      boolean: { type: "boolean" },
      stringArray: {
        type: "array",
        items: { type: "string" },
      },
      object: {
        type: "object",
        required: ["bar", "baz"],
        properties: {
          foo: { type: "string" },
          bar: { type: "boolean" },
          baz: { type: "integer" },
        },
      },
      pickAndMix: {
        oneOf: [
          { type: "string", writeOnly: true },
          { type: "boolean" },
          { type: "number", readOnly: true },
        ],
      },
      not: {
        anyOf: [{ type: "string" }, { type: "boolean" }, { type: "number" }],
        not: {
          anyOf: [{ type: "string" }, { type: "integer" }],
        },
      },
    },
  },
} satisfies OpenAPIObject;

describe("resolvePolymorphism", () => {
  it("Should resolve polymorphism", async () => {
    const repository = new Repository("./openapi.json", openApi as unknown as OpenAPIObject);

    await expect(
      resolvePolymorphism(
        openApi.components.schemas.allOf as unknown as SchemaObject,
        "allOf",
        repository,
      ),
    ).resolves.toEqual({
      read: "{ foo?: string; } & { bar?: number; }",
      write: "{ bar?: number; baz?: boolean; }",
    });

    await expect(
      resolvePolymorphism(
        openApi.components.schemas.anyOf as unknown as SchemaObject,
        "anyOf",
        repository,
      ),
    ).resolves.toEqual({
      read: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
      write: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
    });

    await expect(
      resolvePolymorphism(
        openApi.components.schemas.oneOf as unknown as SchemaObject,
        "oneOf",
        repository,
      ),
    ).resolves.toEqual({
      read: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
      write: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
    });
  });
});

describe("resolveAdditionalProperties", () => {
  it("Should resolve additional properties", async () => {
    const repository = new Repository("./openapi.json", openApi as unknown as OpenAPIObject);

    expect(resolveAdditionalProperties({}, repository)).toEqual(undefined);
    expect(resolveAdditionalProperties({ additionalProperties: true }, repository)).toEqual(true);
    expect(resolveAdditionalProperties({ additionalProperties: false }, repository)).toEqual(false);
    await expect(
      resolveAdditionalProperties({ additionalProperties: {} }, repository),
    ).resolves.toEqual({});
    await expect(
      resolveAdditionalProperties({ additionalProperties: { type: "string" } }, repository),
    ).resolves.toEqual({ read: "string", write: "string" });
  });
});

describe("resolveProperties", () => {
  it("Should resolve properties", async () => {
    const repository = new Repository("./openapi.json", openApi as unknown as OpenAPIObject);

    await expect(
      resolveProperties({ required: [], properties: {}, additionalProperties: false, repository }),
    ).resolves.toEqual({});

    await expect(
      resolveProperties({
        required: openApi.components.schemas.properties.required,
        properties: openApi.components.schemas.properties.properties,
        additionalProperties: false,
        repository,
      }),
    ).resolves.toEqual({
      read: "{ foo: string; bar: number; }",
      write: "{ foo: string; baz?: boolean; }",
    });

    await expect(
      resolveProperties({
        required: openApi.components.schemas.properties.required,
        properties: openApi.components.schemas.properties.properties,
        additionalProperties: undefined,
        repository,
      }),
    ).resolves.toEqual({
      read: "{ foo: string; bar: number; [key: string]: unknown; }",
      write: "{ foo: string; baz?: boolean; [key: string]: unknown; }",
    });
  });
});

describe("resolveItems", () => {
  it("Should resolve items", async () => {
    const repository = new Repository("./openapi.json", openApi as unknown as OpenAPIObject);

    await expect(resolveItems(openApi.components.schemas.items.items, repository)).resolves.toEqual(
      {
        read: "(string)[]",
        write: "(string)[]",
      },
    );
    await expect(
      resolveItems(openApi.components.schemas.itemsComplicated.items, repository),
    ).resolves.toEqual({
      read: "(string)[]",
      write: "(number)[]",
    });
  });
});

describe("resolveSchema", () => {
  it("Should resolve a schema", async () => {
    const repository = new Repository("./openapi.json", openApi as unknown as OpenAPIObject);
    const schemas = openApi.components.schemas;

    await expect(resolveSchema(schemas.string, repository, [])).resolves.toEqual({
      read: "string",
      write: "string",
    });
    await expect(resolveSchema(schemas.number, repository, [])).resolves.toEqual({
      read: "number",
      write: "number",
    });
    await expect(resolveSchema(schemas.integer, repository, [])).resolves.toEqual({
      read: "number",
      write: "number",
    });
    await expect(resolveSchema(schemas.boolean, repository, [])).resolves.toEqual({
      read: "boolean",
      write: "boolean",
    });
    await expect(resolveSchema(schemas.null, repository, [])).resolves.toEqual({
      read: "null",
      write: "null",
    });
    await expect(resolveSchema(schemas.stringArray, repository, [])).resolves.toEqual({
      read: "(string)[]",
      write: "(string)[]",
    });
    await expect(resolveSchema(schemas.object, repository, [])).resolves.toEqual({
      read: "{ foo?: string; bar: boolean; baz: number; [key: string]: unknown; }",
      write: "{ foo?: string; bar: boolean; baz: number; [key: string]: unknown; }",
    });
    await expect(
      resolveSchema(schemas.allOf as unknown as SchemaObject, repository, []),
    ).resolves.toEqual({
      read: "({ [key: string]: unknown; } & { foo?: string; } & { bar?: number; })",
      write: "({ [key: string]: unknown; } & { bar?: number; baz?: boolean; })",
    });
    await expect(
      resolveSchema(schemas.oneOf as unknown as SchemaObject, repository, []),
    ).resolves.toEqual({
      read: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
      write: "{ foo?: string; } | { bar?: number; baz?: boolean; }",
    });
    await expect(
      resolveSchema(schemas.pickAndMix as unknown as SchemaObject, repository, []),
    ).resolves.toEqual({
      read: "boolean | number",
      write: "string | boolean",
    });
    await expect(resolveSchema(schemas.not, repository, [])).resolves.toEqual({
      read: "Exclude<string | boolean | number, string | number>",
      write: "Exclude<string | boolean | number, string | number>",
    });
  });
});
