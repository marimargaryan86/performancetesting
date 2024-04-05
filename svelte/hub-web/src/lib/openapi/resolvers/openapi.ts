import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { resolveComponents } from "./component";
import { resolvePaths } from "./path";

export async function resolveOpenAPIObject(
  specification: OpenAPI.OpenAPIObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.OpenAPIObject> {
  return {
    paths: await resolvePaths(specification.paths, repository),
    components: specification.components
      ? await resolveComponents(specification.components, repository)
      : undefined,
  };
}
