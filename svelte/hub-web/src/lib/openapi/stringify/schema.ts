import type { Mode } from "./types";
import type * as ResolvedOpenAPI from "../resolvers/types";

export function stringifySchema(schema: ResolvedOpenAPI.SchemaObject, mode: Mode): string {
  return schema[mode] ?? "undefined";
}
