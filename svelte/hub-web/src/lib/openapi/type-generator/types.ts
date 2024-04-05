import type { Mode } from "../stringify/types";
import type * as ResolvedOpenAPI from "../resolvers/types";
import type * as OpenAPI from "../openapi/types";

export type Union =
  | {
      type: "and" | "or";
      values: Union[];
    }
  | {
      type: "not";
      values: [Union, Union];
    }
  | string
  | undefined;

export interface GetTypeScriptTypeParams {
  schema: OpenAPI.SchemaObject;
  mode: Mode;
  properties?: ResolvedOpenAPI.SchemaObject;
  items?: ResolvedOpenAPI.SchemaObject;
  polymorphism: {
    allOf?: ResolvedOpenAPI.SchemaObject;
    oneOf?: ResolvedOpenAPI.SchemaObject;
    anyOf?: ResolvedOpenAPI.SchemaObject;
    not?: ResolvedOpenAPI.SchemaObject;
  };
}
