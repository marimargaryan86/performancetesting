import { describe, it, expect } from "vitest";
import { stringifyOperation, stringifyPathItem, stringifyPaths } from "../path";

describe("stringifyOperation", () => {
  it("Should stringify an operation", () => {
    expect(stringifyOperation({ parameters: {}, responses: {} }, 0)).toBe(`\
{
  response: Record<string, never>;
}`);
    expect(
      stringifyOperation(
        {
          parameters: {
            query: {
              foo: { in: "query", name: "foo", required: false, schema: { write: "boolean" } },
            },
          },
          responses: {},
        },
        0,
      ),
    ).toBe(`\
{
  request?: {
    query?: {
      foo?: boolean;
    };
  };
  response: Record<string, never>;
}`);
    expect(
      stringifyOperation(
        {
          parameters: {
            query: {
              foo: { in: "query", name: "foo", required: false, schema: { write: "boolean" } },
            },
            path: {
              foo: { in: "path", name: "foo", required: true, schema: { write: "number" } },
            },
          },
          responses: {},
        },
        0,
      ),
    ).toBe(`\
{
  request: {
    path: {
      foo: number;
    };
    query?: {
      foo?: boolean;
    };
  };
  response: Record<string, never>;
}`);
    expect(
      stringifyOperation(
        {
          parameters: {},
          responses: {
            401: {
              headers: {
                foo: {
                  in: "header",
                  name: "foo",
                  required: true,
                  schema: {
                    read: "boolean",
                  },
                },
              },
              content: {
                "application/json": { schema: { read: "string", write: "boolean" } },
              },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  response: {
    status: 401;
    body: {
      type: "application/json";
      data: string;
    };
    headers: {
      foo: boolean;
    };
  };
}`);
    expect(
      stringifyOperation(
        {
          parameters: {},
          responses: {
            401: {
              content: {
                "application/json": { schema: { read: "string", write: "boolean" } },
              },
            },
            200: {
              content: {
                "application/json": { schema: { read: "string", write: "boolean" } },
              },
            },
          },
        },
        0,
      ),
    ).toBe(`\
{
  response: ({
    status: 200;
    body: {
      type: "application/json";
      data: string;
    };
  } | {
    status: 401;
    body: {
      type: "application/json";
      data: string;
    };
  });
}`);
  });
});

describe("stringifyPathItem", () => {
  it("Should stringify a path item", () => {
    expect(stringifyPathItem({ get: undefined }, 0)).toBe("Record<string, never>");
    expect(stringifyPathItem({ get: { responses: {}, parameters: {} } }, 0)).toBe(`\
{
  get: {
    response: Record<string, never>;
  };
}`);
    expect(
      stringifyPathItem(
        { get: { responses: {}, parameters: {} }, patch: { responses: {}, parameters: {} } },
        0,
      ),
    ).toBe(`\
{
  get: {
    response: Record<string, never>;
  };
  patch: {
    response: Record<string, never>;
  };
}`);
  });
});

describe("stringifyPaths", () => {
  it("Should stringify paths", () => {
    expect(stringifyPaths({}, 0)).toBe("Record<string, never>");
    expect(
      stringifyPaths(
        {
          "/foo": {
            get: { responses: {}, parameters: {} },
          },
        },
        0,
      ),
    ).toBe(`\
{
  "/foo": {
    get: {
      response: Record<string, never>;
    };
  };
}`);
  });
  expect(
    stringifyPaths(
      {
        "/foo": {
          get: { responses: {}, parameters: {} },
          post: {
            parameters: {},
            responses: {},
            requestBody: {
              content: {
                "application/json": { schema: { write: "boolean" } },
              },
              required: false,
            },
          },
        },
      },
      0,
    ),
  ).toBe(`\
{
  "/foo": {
    get: {
      response: Record<string, never>;
    };
    post: {
      request?: {
        body?: {
          type: "application/json";
          data: boolean;
        };
      };
      response: Record<string, never>;
    };
  };
}`);
});
