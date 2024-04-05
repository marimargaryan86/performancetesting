import { describe, it, expect } from "vitest";
import { stringifyRequest, stringifyResponses } from "../response-request";

describe("stringifyRequest", () => {
  it("Should stringify a request", () => {
    expect(
      stringifyRequest(
        {},
        {
          content: {
            "application/json": {
              schema: { write: "boolean" },
            },
          },
          required: true,
        },
        0,
      ),
    ).toEqual([
      true,
      `\
{
  body: {
    type: "application/json";
    data: boolean;
  };
}`,
    ]);
    expect(
      stringifyRequest(
        {
          header: {
            foo: {
              in: "header",
              name: "foo",
              required: true,
              schema: { write: "boolean" },
            },
          },
        },
        undefined,
        0,
      ),
    ).toEqual([
      true,
      `\
{
  headers: {
    foo: boolean;
  };
}`,
    ]);
  });
  expect(
    stringifyRequest(
      {
        cookie: {
          foo: {
            in: "cookie",
            name: "foo",
            required: true,
            schema: { write: "string" },
          },
        },
      },
      {
        content: {
          "application/json": {
            schema: { write: "boolean" },
          },
        },
        required: false,
      },
      0,
    ),
  ).toEqual([
    true,
    `\
{
  body?: {
    type: "application/json";
    data: boolean;
  };
  cookie: {
    foo: string;
  };
}`,
  ]);
});

describe("stringifyResponses", () => {
  it("Should stringify responses", () => {
    expect(stringifyResponses({}, 0)).toBe("Record<string, never>");
    expect(
      stringifyResponses(
        {
          200: {
            content: {
              "application/json": { schema: { read: "boolean", write: "number" } },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  status: 200;
  body: {
    type: "application/json";
    data: boolean;
  };
}`);
    expect(
      stringifyResponses(
        {
          200: {
            content: {
              "application/json": { schema: { read: "boolean", write: "number" } },
              "text/html": { schema: { read: "number", write: "boolean" } },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  status: 200;
  body: ({
    type: "application/json";
    data: boolean;
  } | {
    type: "text/html";
    data: number;
  });
}`);
    expect(stringifyResponses({ 200: {} }, 0)).toBe(`\
{
  status: 200;
}`);
    expect(
      stringifyResponses(
        {
          200: {
            content: {
              "application/json": { schema: { read: "boolean", write: "number" } },
            },
            headers: {
              foo: {
                in: "header",
                name: "foo",
                required: false,
                schema: { read: "number", write: "boolean" },
              },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  status: 200;
  body: {
    type: "application/json";
    data: boolean;
  };
  headers?: {
    foo?: number;
  };
}`);
  });
});
