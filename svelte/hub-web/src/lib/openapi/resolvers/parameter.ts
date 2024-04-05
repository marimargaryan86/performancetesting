import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { resolveContent } from "./content";
import { resolveSchema } from "./schema";

export async function resolveParameterAux(
  resolved: OpenAPI.ParameterObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.ParameterObject> {
  const [schema, content] = await Promise.all([
    resolved.schema ? resolveSchema(resolved.schema, repository) : undefined,
    resolved.content ? resolveContent(resolved.content, repository) : undefined,
  ]);

  return {
    in: resolved.in,
    name: resolved.name,
    required: Boolean(resolved.required),
    schema,
    content,
  };
}

export async function resolveParameter(
  parameter: OpenAPI.ParameterObject | OpenAPI.ReferenceObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.ParameterObject> {
  const [resolved, ref] = await repository.resolve(parameter);
  const existing = repository.getRef<ResolvedOpenAPI.ParameterObject>(ref);

  if (existing) {
    return existing;
  }

  return repository.saveRef<ResolvedOpenAPI.ParameterObject>(
    await resolveParameterAux(resolved, repository),
    ref,
  );
}

export async function resolveParameters(
  parameters: (OpenAPI.ParameterObject | OpenAPI.ReferenceObject)[],
  repository: Repository,
): Promise<ResolvedOpenAPI.OperationObject["parameters"]> {
  const tasks = parameters.map((parameter) =>
    resolveParameter(parameter, repository).then((value) => [value.name, value] as const),
  );

  const resolved = await Promise.all(tasks);
  const cookie = Object.fromEntries(resolved.filter(([, parameter]) => parameter.in === "cookie"));
  const header = Object.fromEntries(resolved.filter(([, parameter]) => parameter.in === "header"));
  const path = Object.fromEntries(resolved.filter(([, parameter]) => parameter.in === "path"));
  const query = Object.fromEntries(resolved.filter(([, parameter]) => parameter.in === "query"));

  return {
    cookie: Object.keys(cookie).length ? cookie : undefined,
    header: Object.keys(header).length ? header : undefined,
    path: Object.keys(path).length ? path : undefined,
    query: Object.keys(query).length ? query : undefined,
  };
}

export async function resolveHeader(
  header: OpenAPI.HeaderObject | OpenAPI.ReferenceObject,
  name: string,
  repository: Repository,
): Promise<ResolvedOpenAPI.ParameterObject> {
  const [resolved, ref] = await repository.resolve(header);
  const nextRef = ref ? `${ref}-${name}` : undefined;
  const existing = repository.getRef<ResolvedOpenAPI.ParameterObject>(nextRef);

  if (existing) {
    return existing;
  }

  return repository.saveRef<ResolvedOpenAPI.ParameterObject>(
    await resolveParameterAux({ ...resolved, name, in: "header" }, repository),
    nextRef,
  );
}

export async function resolveHeaders(
  headers: Record<string, OpenAPI.HeaderObject | OpenAPI.ReferenceObject>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.ParameterObject>> {
  const tasks = Object.entries(headers).map(([name, header]) =>
    resolveHeader(header, name, repository).then((value) => [name, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}
