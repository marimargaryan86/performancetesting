import type { OpenAPIObject } from "../../openapi/types";
import { describe, it, expect } from "vitest";
import {
  resolveContent,
  resolveEncoding,
  resolveEncodingMapping,
  resolveMediaType,
} from "../content";
import Repository from "../../repository";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {},
} satisfies OpenAPIObject;

describe("resolveEncoding", () => {
  it("Should resovle an encoding", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveEncoding({}, repository)).resolves.toEqual({});
    await expect(
      resolveEncoding(
        {
          contentType: "application/json",
          headers: {
            foo: {
              schema: {
                type: "boolean",
              },
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      contentType: "application/json",
      headers: {
        foo: {
          in: "header",
          name: "foo",
          required: false,
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
    });
  });
});

describe("resolveEncodingMapping", () => {
  it("Should resolve an encoding mapping", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveEncodingMapping({}, repository)).resolves.toEqual({});
    await expect(
      resolveEncodingMapping(
        {
          "application/json": {
            headers: {
              foo: {
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
      "application/json": {
        headers: {
          foo: {
            in: "header",
            name: "foo",
            required: false,
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

describe("resolveMediaType", () => {
  it("Should resolve a media type", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveMediaType({}, repository)).resolves.toEqual({});
    await expect(
      resolveMediaType(
        {
          schema: {
            type: "array",
            items: {
              type: "string",
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      schema: {
        read: "(string)[]",
        write: "(string)[]",
      },
    });
    await expect(
      resolveMediaType(
        {
          encoding: {
            "application/json": {},
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      encoding: {
        "application/json": {},
      },
    });
  });
});

describe("resolveContent", () => {
  it("Should resolve content", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveContent({}, repository)).resolves.toEqual({});
    await expect(
      resolveContent(
        {
          "application/json": {
            schema: {
              type: "object",
              required: ["foo"],
              properties: {
                foo: {
                  type: "string",
                },
                bar: {
                  type: "number",
                },
              },
              additionalProperties: false,
            },
          },
        },
        repository,
      ),
    ).resolves.toEqual({
      "application/json": {
        schema: {
          read: "{ foo: string; bar?: number; }",
          write: "{ foo: string; bar?: number; }",
        },
      },
    });
  });
});
