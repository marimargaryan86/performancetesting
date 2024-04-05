import { describe, it, expect } from "vitest";
import Repository from "$lib/openapi/repository";
import {
  resolveComponentHeaders,
  resolveComponentParameters,
  resolveComponentRequestBodies,
  resolveComponentResponses,
  resolveComponentSchemas,
  resolveComponents,
} from "../component";
import type { OpenAPIObject } from "../../openapi/types";

const openApi = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {
    headers: {
      foo: {
        schema: {
          type: "string",
        },
        required: true,
      },
      "foo-bar": {
        schema: {
          type: "boolean",
        },
      },
    },
    parameters: {
      foo: {
        in: "path",
        name: "foo",
        schema: {
          type: "string",
        },
        required: true,
      },
      "foo-bar": {
        in: "path",
        name: "foo-bar",
        schema: {
          type: "number",
        },
        required: true,
      },
    },
    requestBodies: {
      foo: {
        content: {
          "application/json": {
            schema: {
              type: "string",
              writeOnly: true,
            },
          },
        },
        required: true,
      },
      "foo-bar": {
        content: {
          "application/json": {
            schema: {
              type: "number",
              writeOnly: true,
            },
          },
        },
      },
    },
    responses: {
      foo: {
        description: "A description",
        content: {
          "application/json": {
            schema: {
              type: "boolean",
            },
          },
        },
      },
      "foo-bar": {
        description: "A description",
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
              $ref: "#/components/schemas/myInteger",
            },
            required: true,
          },
        },
      },
    },
    schemas: {
      myInteger: {
        type: "integer",
      },
      "my-boolean": {
        type: "boolean",
        nullable: true,
      },
    },
  },
} satisfies OpenAPIObject;

describe("resolveComponentHeaders", () => {
  it("Should resolve component headers", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveComponentHeaders(openApi.components.headers, repository)).resolves.toEqual({
      foo: {
        in: "header",
        name: "foo",
        required: true,
        schema: {
          read: "string",
          write: "string",
        },
      },
      "foo-bar": {
        in: "header",
        name: "foo-bar",
        required: false,
        schema: {
          read: "boolean",
          write: "boolean",
        },
      },
    });
  });
});

describe("resolveComponentParameters", () => {
  it("Should resolve component parameters", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveComponentParameters(openApi.components.parameters, repository),
    ).resolves.toEqual({
      foo: {
        in: "path",
        name: "foo",
        required: true,
        schema: {
          read: "string",
          write: "string",
        },
      },
      "foo-bar": {
        in: "path",
        name: "foo-bar",
        required: true,
        schema: {
          read: "number",
          write: "number",
        },
      },
    });
  });
});

describe("resolveComponentRequestBodies", () => {
  it("Should resolve component request bodies", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveComponentRequestBodies(openApi.components.requestBodies, repository),
    ).resolves.toEqual({
      foo: {
        content: {
          "application/json": {
            schema: {
              write: "string",
            },
          },
        },
        required: true,
      },
      "foo-bar": {
        content: {
          "application/json": {
            schema: {
              write: "number",
            },
          },
        },
        required: false,
      },
    });
  });
});

describe("resolveComponentResponses", () => {
  it("Should resolve component responses", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(
      resolveComponentResponses(openApi.components.responses, repository),
    ).resolves.toEqual({
      foo: {
        content: {
          "application/json": {
            schema: {
              read: "boolean",
              write: "boolean",
            },
          },
        },
      },
      "foo-bar": {
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
            required: true,
            schema: {
              read: "number",
              write: "number",
            },
          },
        },
      },
    });
  });
});

describe("resolveComponentSchemas", () => {
  it("Should resolve component schemas", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveComponentSchemas(openApi.components.schemas, repository)).resolves.toEqual({
      myInteger: {
        read: "number",
        write: "number",
      },
      "my-boolean": {
        read: "(boolean | null)",
        write: "(boolean | null)",
      },
    });
  });
});

describe("resolveComponents", () => {
  it("Should resolve components", async () => {
    const repository = new Repository("./openapi.json", openApi);

    await expect(resolveComponents(openApi.components, repository)).resolves.toEqual({
      headers: {
        foo: {
          in: "header",
          name: "foo",
          required: true,
          schema: {
            read: "string",
            write: "string",
          },
        },
        "foo-bar": {
          in: "header",
          name: "foo-bar",
          required: false,
          schema: {
            read: "boolean",
            write: "boolean",
          },
        },
      },
      parameters: {
        foo: {
          in: "path",
          name: "foo",
          required: true,
          schema: {
            read: "string",
            write: "string",
          },
        },
        "foo-bar": {
          in: "path",
          name: "foo-bar",
          required: true,
          schema: {
            read: "number",
            write: "number",
          },
        },
      },
      requestBodies: {
        foo: {
          content: {
            "application/json": {
              schema: {
                write: "string",
              },
            },
          },
          required: true,
        },
        "foo-bar": {
          content: {
            "application/json": {
              schema: {
                write: "number",
              },
            },
          },
          required: false,
        },
      },
      responses: {
        foo: {
          content: {
            "application/json": {
              schema: {
                read: "boolean",
                write: "boolean",
              },
            },
          },
        },
        "foo-bar": {
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
              required: true,
              schema: {
                read: "number",
                write: "number",
              },
            },
          },
        },
      },
      schemas: {
        "my-boolean": {
          read: "(boolean | null)",
          write: "(boolean | null)",
        },
        myInteger: {
          read: "number",
          write: "number",
        },
      },
    });
  });
});
