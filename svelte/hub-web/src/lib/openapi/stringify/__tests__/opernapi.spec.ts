import { describe, it, expect } from "vitest";
import { stringifyOpenAPI } from "..";

describe("stringifyOpenAPI", () => {
  it("Should stringify an open API specification", () => {
    expect(
      stringifyOpenAPI({
        paths: {
          "/foo": {
            get: {
              parameters: {},
              responses: {
                200: {
                  content: {
                    "application/json": {
                      schema: { read: "string" },
                    },
                  },
                },
              },
            },
          },
          "/bar/{baz}": {
            post: {
              parameters: {
                path: {
                  baz: {
                    in: "path",
                    name: "baz",
                    required: true,
                    schema: { write: "string" },
                  },
                },
              },
              requestBody: {
                content: {
                  "application/json": {
                    schema: {
                      write: "number",
                    },
                  },
                },
                required: false,
              },
              responses: {
                201: {
                  content: {
                    "application/json": {
                      schema: { read: "boolean" },
                    },
                  },
                },
              },
            },
          },
        },
      }),
    ).toBe(`\
export type Specification = {
  "/foo": {
    get: {
      response: {
        status: 200;
        body: {
          type: "application/json";
          data: string;
        };
      };
    };
  };
  "/bar/{baz}": {
    post: {
      request: {
        body?: {
          type: "application/json";
          data: number;
        };
        path: {
          baz: string;
        };
      };
      response: {
        status: 201;
        body: {
          type: "application/json";
          data: boolean;
        };
      };
    };
  };
};
`);
  });
});
