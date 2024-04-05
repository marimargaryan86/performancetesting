import { describe, it, expect } from "vitest";
import {
  stringifyContent,
  stringifyEncoding,
  stringifyEncodingMapping,
  stringifyMediaType,
} from "../content";

describe("stringifyEncoding", () => {
  it("Should stringify an encoding", () => {
    expect(stringifyEncoding({}, 0)).toBe(`\
{
  contentType: undefined;
  headers: undefined;
}`);
    expect(
      stringifyEncoding(
        {
          contentType: "application/json",
          headers: {
            foo: {
              in: "header",
              name: "foo",
              required: true,
              schema: { read: "boolean", write: "number" },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  contentType: "application/json";
  headers: {
    foo: {
      name: "foo";
      required: true;
      schema: {
        read: boolean;
        write: number;
      };
    };
  };
}`);
  });
});

describe("stringifyEncodingMapping", () => {
  it("Should stringify an encoding mapping", () => {
    expect(
      stringifyEncodingMapping(
        {
          foo: {},
        },
        0,
      ),
    ).toBe(`\
{
  foo: {
    contentType: undefined;
    headers: undefined;
  };
}`);
  });
});

describe("stringifyMediaType", () => {
  it("Should stringify a media type", () => {
    expect(() => stringifyMediaType({}, "read", 0)).toThrow(
      "Neither schema nor encoding is defined in MediaType",
    );
    expect(
      stringifyMediaType(
        {
          schema: { read: "boolean", write: "number" },
        },
        "read",
        0,
      ),
    ).toBe("boolean");
    expect(
      stringifyMediaType(
        {
          schema: { read: "boolean", write: "number" },
        },
        "write",
        0,
      ),
    ).toBe("number");
    expect(
      stringifyMediaType(
        {
          encoding: {
            "application/json": {
              contentType: "application/json",
              headers: {
                foo: {
                  in: "header",
                  name: "foo",
                  required: true,
                  schema: { read: "boolean", write: "number" },
                },
              },
            },
          },
        },
        "write",
        0,
      ),
    ).toBe(`\
{
  "application/json": {
    contentType: "application/json";
    headers: {
      foo: {
        name: "foo";
        required: true;
        schema: {
          read: boolean;
          write: number;
        };
      };
    };
  };
}`);
  });
});

describe("stringifyContent", () => {
  it("Should stringify content", () => {
    expect(stringifyContent({}, "read", 0)).toBe("undefined");
    expect(
      stringifyContent(
        {
          "application/json": {
            schema: { read: "number", write: "boolean" },
          },
        },
        "read",
        0,
      ),
    ).toBe(`\
{
  type: "application/json";
  data: number;
}`);
    expect(
      stringifyContent(
        {
          "application/json": {
            schema: { read: "number", write: "boolean" },
          },
        },
        "write",
        0,
      ),
    ).toBe(`\
{
  type: "application/json";
  data: boolean;
}`);
  });
});
