import { describe, it, expect } from "vitest";
import {
  stringifyParameter,
  stringifyParameterMapping,
  stringifyParameterSimple,
  stringifyParametersAux,
} from "../parameter";

describe("stringifyParameter", () => {
  it("Should stringify a paraemter", () => {
    expect(
      stringifyParameter(
        { in: "cookie", name: "foo", required: true, schema: { read: "boolean", write: "number" } },
        0,
      ),
    ).toBe(`\
{
  name: "foo";
  required: true;
  schema: {
    read: boolean;
    write: number;
  };
}`);
    expect(
      stringifyParameter(
        {
          in: "cookie",
          name: "foo",
          required: true,
          content: {
            "application/json": {
              schema: { read: "string", write: "number" },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  name: "foo";
  required: true;
  content: {
    read: {
      type: "application/json";
      data: string;
    };
    write: {
      type: "application/json";
      data: number;
    };
  };
}`);
  });
});

describe("stringifyParameterSimple", () => {
  it("Should stringify a parameter so a simple representation", () => {
    expect(() =>
      stringifyParameterSimple(
        {
          in: "cookie",
          name: "foo",
          required: false,
        },
        "read",
        0,
      ),
    ).toThrow("Neither schema nor content is defined in parameter");
    expect(
      stringifyParameterSimple(
        {
          in: "cookie",
          name: "foo",
          required: false,
          schema: { read: "number", write: "boolean" },
        },
        "read",
        0,
      ),
    ).toBe("number");
    expect(
      stringifyParameterSimple(
        {
          in: "cookie",
          name: "foo",
          required: false,
          schema: { read: "number", write: "boolean" },
        },
        "write",
        0,
      ),
    ).toBe("boolean");
    expect(
      stringifyParameterSimple(
        {
          in: "cookie",
          name: "foo",
          required: false,
          content: {
            "application/json": {
              schema: { read: "number", write: "boolean" },
            },
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

describe("stringifyParametersAux", () => {
  it("Should stringify a parameters", () => {
    expect(
      stringifyParametersAux(
        {
          foo: {
            in: "cookie",
            name: "foo",
            required: false,
            schema: { read: "string", write: "number" },
          },
        },
        "read",
        0,
      ),
    ).toEqual([false, "{\n  foo?: string;\n}"]);
    expect(
      stringifyParametersAux(
        {
          foo: {
            in: "cookie",
            name: "foo",
            required: false,
            schema: { read: "string", write: "number" },
          },
          bar: {
            in: "cookie",
            name: "bar",
            required: true,
            schema: { read: "number", write: "string" },
          },
        },
        "write",
        0,
      ),
    ).toEqual([
      true,
      `\
{
  foo?: number;
  bar: string;
}`,
    ]);
  });
});

describe("stringifyParameterMapping", () => {
  it("Should stringify a parameter mapping", () => {
    expect(
      stringifyParameterMapping(
        {
          foo: {
            in: "cookie",
            name: "foo",
            required: true,
            schema: { read: "string", write: "number" },
          },
          bar: {
            in: "cookie",
            name: "bar",
            required: false,
            schema: { read: "string", write: "number" },
          },
        },
        0,
      ),
    ).toBe(`\
{
  foo: {
    name: "foo";
    required: true;
    schema: {
      read: string;
      write: number;
    };
  };
  bar: {
    name: "bar";
    required: false;
    schema: {
      read: string;
      write: number;
    };
  };
}`);
  });
});
