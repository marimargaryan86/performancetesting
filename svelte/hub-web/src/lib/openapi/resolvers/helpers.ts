import type * as OpenAPI from "../openapi/types";

export function ensureDefined<T>(item: T | undefined): item is T {
  return item !== undefined;
}

export function isReference(obj: unknown): obj is OpenAPI.ReferenceObject {
  return typeof obj === "object" && obj !== null && "$ref" in obj;
}
