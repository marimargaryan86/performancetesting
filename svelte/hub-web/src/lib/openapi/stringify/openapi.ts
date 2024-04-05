import type * as ResolvedOpenAPI from "../resolvers/types";
import { stringifyPaths } from "./path";

export function stringifyOpenAPI(specification: ResolvedOpenAPI.OpenAPIObject): string {
  return `${`export type Specification = ${stringifyPaths(specification.paths, 0)}`};\n`;
}
