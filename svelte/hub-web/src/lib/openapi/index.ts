import type * as OpenAPI from "./openapi/types";
import type * as ResolvedOpenAPI from "./resolvers/types";
import { resolveOpenAPIObject } from "./resolvers";
import Repository from "./repository";
import { readFile, writeFile } from "./file-handler";
import { stringifyOpenAPI } from "./stringify";
export type * as Infer from "./types";

async function loadSpecification(path: string): Promise<ResolvedOpenAPI.OpenAPIObject> {
  const specification = await readFile<OpenAPI.OpenAPIObject>(path);
  const repository = new Repository(path, specification);
  const result = await resolveOpenAPIObject(specification, repository);

  return result;
}

function saveTypes(path: string, spec: ResolvedOpenAPI.OpenAPIObject): Promise<void> {
  return writeFile(path, stringifyOpenAPI(spec));
}

export default async function process(source: string, target: string): Promise<void> {
  const spec = await loadSpecification(source);

  return saveTypes(target, spec);
}
