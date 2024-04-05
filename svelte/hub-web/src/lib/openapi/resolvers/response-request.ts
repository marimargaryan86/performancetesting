import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { resolveContent } from "./content";
import { ensureDefined } from "./helpers";
import { resolveHeaders } from "./parameter";

export async function resolveResponse(
  response: OpenAPI.ResponseObject | OpenAPI.ReferenceObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.ResponseObject> {
  const [resolved, ref] = await repository.resolve(response);
  const existing = repository.getRef<ResolvedOpenAPI.ResponseObject>(ref);

  if (existing) {
    return existing;
  }

  const content = resolved.content ? resolveContent(resolved.content, repository) : undefined;
  const headers = resolved.headers ? resolveHeaders(resolved.headers, repository) : undefined;

  return repository.saveRef<ResolvedOpenAPI.ResponseObject>(
    {
      content: await content,
      headers: await headers,
    },
    ref,
  );
}

export async function resolveRequest(
  requestBody: OpenAPI.RequestBodyObject | OpenAPI.ReferenceObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.RequestBodyObject> {
  const [resolved, ref] = await repository.resolve(requestBody);
  const existing = repository.getRef<ResolvedOpenAPI.RequestBodyObject>(ref);

  if (existing) {
    return existing;
  }

  return repository.saveRef<ResolvedOpenAPI.RequestBodyObject>(
    {
      content: await resolveContent(resolved.content, repository),
      required: Boolean(resolved.required),
    },
    ref,
  );
}

export async function resolveResponses(
  responses: OpenAPI.ResponsesObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.ResponsesObject> {
  const tasks = Object.entries(responses).map(([httpCode, response]) =>
    resolveResponse(response, repository).then((value) => [httpCode, value] as const),
  );

  return Object.fromEntries((await Promise.all(tasks)).filter(ensureDefined));
}
