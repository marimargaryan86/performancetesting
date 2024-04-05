import type Repository from "../repository";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { resolveHeaders } from "./parameter";
import { resolveSchema } from "./schema";

export async function resolveEncoding(
  encoding: OpenAPI.EncodingObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.EncodingObject> {
  return {
    contentType: encoding.contentType,
    headers: encoding.headers ? await resolveHeaders(encoding.headers, repository) : undefined,
  };
}

export async function resolveEncodingMapping(
  encodingMapping: Record<string, OpenAPI.EncodingObject>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.EncodingObject>> {
  const tasks = Object.entries(encodingMapping).map(([contentType, encoding]) =>
    resolveEncoding(encoding, repository).then((value) => [contentType, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}

export async function resolveMediaType(
  mediaType: OpenAPI.MediaTypeObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.MediaTypeObject> {
  const [schema, encoding] = await Promise.all([
    mediaType.schema ? resolveSchema(mediaType.schema, repository) : undefined,
    mediaType.encoding ? resolveEncodingMapping(mediaType.encoding, repository) : undefined,
  ]);

  return {
    schema,
    encoding,
  };
}

export async function resolveContent(
  content: Record<string, OpenAPI.MediaTypeObject>,
  repository: Repository,
): Promise<Record<string, ResolvedOpenAPI.MediaTypeObject>> {
  const tasks = Object.entries(content).map(([contentType, mediaType]) =>
    resolveMediaType(mediaType, repository).then((value) => [contentType, value] as const),
  );

  return Object.fromEntries(await Promise.all(tasks));
}
