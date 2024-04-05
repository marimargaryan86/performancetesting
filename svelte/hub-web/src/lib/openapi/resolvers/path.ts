import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { httpMethods } from "./types";
import { ensureDefined } from "./helpers";
import { resolveParameters } from "./parameter";
import { resolveRequest, resolveResponses } from "./response-request";

export async function resolveOperation(
  operation: OpenAPI.OperationObject,
  parentParameters: (OpenAPI.ReferenceObject | OpenAPI.ParameterObject)[],
  repository: Repository,
): Promise<ResolvedOpenAPI.OperationObject> {
  const parameters = resolveParameters(
    [...(operation.parameters ?? []), ...parentParameters],
    repository,
  );
  const responses = resolveResponses(operation.responses, repository);
  const requestBody = operation.requestBody
    ? resolveRequest(operation.requestBody, repository)
    : undefined;

  return {
    parameters: await parameters,
    responses: await responses,
    requestBody: await requestBody,
  };
}

export async function resolvePathItem(
  pathItem: OpenAPI.PathItemObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.PathItemObject> {
  const [resolved, ref] = await repository.resolve(pathItem);
  const existing = repository.getRef<ResolvedOpenAPI.PathItemObject>(ref);

  if (existing) {
    return existing;
  }

  const tasks = httpMethods.map((method) => {
    const operation = resolved[method];

    if (operation) {
      return resolveOperation(operation, resolved.parameters ?? [], repository).then(
        (value) => [method, value] as const,
      );
    }

    return undefined;
  });

  return repository.saveRef<ResolvedOpenAPI.PathItemObject>(
    Object.fromEntries((await Promise.all(tasks)).filter(ensureDefined)),
    ref,
  );
}

export async function resolvePaths(
  paths: OpenAPI.PathsObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.PathsObject> {
  const tasks = Object.entries(paths).map(([path, item]) => {
    return path.startsWith("/")
      ? resolvePathItem(item, repository).then((value) => [path, value] as const)
      : undefined;
  });

  return Object.fromEntries((await Promise.all(tasks)).filter(ensureDefined));
}
