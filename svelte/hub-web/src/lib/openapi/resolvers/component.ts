import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { resolveHeader, resolveParameter } from "./parameter";
import { resolveRequest, resolveResponse } from "./response-request";
import { resolveSchema } from "./schema";

export async function resolveComponentHeaders(
  headers: NonNullable<OpenAPI.ComponentsObject["headers"]>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.ParameterObject>> {
  const tasks = Object.entries(headers).map(([name, header]) =>
    resolveHeader(header, name, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveComponentParameters(
  parameters: NonNullable<OpenAPI.ComponentsObject["parameters"]>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.ParameterObject>> {
  const tasks = Object.entries(parameters).map(([name, parameter]) =>
    resolveParameter(parameter, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveComponentRequestBodies(
  requestBodies: NonNullable<OpenAPI.ComponentsObject["requestBodies"]>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.RequestBodyObject>> {
  const tasks = Object.entries(requestBodies).map(([name, requestBody]) =>
    resolveRequest(requestBody, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveComponentResponses(
  responses: NonNullable<OpenAPI.ComponentsObject["responses"]>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.ResponseObject>> {
  const tasks = Object.entries(responses).map(([name, response]) =>
    resolveResponse(response, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveComponentSchemas(
  schemas: NonNullable<OpenAPI.ComponentsObject["schemas"]>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.SchemaObject>> {
  const tasks = Object.entries(schemas).map(([name, schema]) =>
    resolveSchema(schema, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveComponents(
  components: OpenAPI.ComponentsObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.ComponentsObject> {
  const headers = resolveComponentHeaders(components.headers ?? {}, repository);
  const parameters = resolveComponentParameters(components.parameters ?? {}, repository);
  const requestBodies = resolveComponentRequestBodies(components.requestBodies ?? {}, repository);
  const responses = resolveComponentResponses(components.responses ?? {}, repository);
  const schemas = resolveComponentSchemas(components.schemas ?? {}, repository);

  return {
    headers: await headers,
    parameters: await parameters,
    requestBodies: await requestBodies,
    responses: await responses,
    schemas: await schemas,
  };
}
