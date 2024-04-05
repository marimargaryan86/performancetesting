import { describe, it, expect } from "vitest";
import { resolveOpenAPIObject } from "..";
import Repository from "../../repository";
import type { OpenAPIObject } from "../../openapi/types";

const openApiWithComponents = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
  components: {},
} satisfies OpenAPIObject;

const openApiWithoutComponents = {
  info: { title: "Foo", version: "1.0.0" },
  openapi: "3.0.0",
  paths: {
    "/foo": {},
  },
} satisfies OpenAPIObject;

describe("resolveOpenAPIObject", () => {
  it("Should resolve an openAPI specification", async () => {
    const repository = new Repository("./openapi.json", openApiWithComponents);

    await expect(resolveOpenAPIObject(openApiWithComponents, repository)).resolves.toEqual({
      components: {
        headers: {},
        parameters: {},
        requestBodies: {},
        responses: {},
        schemas: {},
      },
      paths: {
        "/foo": {},
      },
    });
    await expect(resolveOpenAPIObject(openApiWithoutComponents, repository)).resolves.toEqual({
      paths: {
        "/foo": {},
      },
    });
  });
});
