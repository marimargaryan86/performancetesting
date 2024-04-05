import type Repository from "../repository";
import { conditionalQuotes, maybeOptionalProp } from "../stringify/helpers";
import { getTypescriptType } from "../type-generator";
import type { MaybePromise } from "./types";
import type * as OpenAPI from "../openapi/types";
import * as ResolvedOpenAPI from "./types";
import { ensureDefined } from "./helpers";

export async function resolvePolymorphism(
  schema: OpenAPI.SchemaObject,
  which: "oneOf" | "allOf" | "anyOf",
  repository: Repository,
): Promise<ResolvedOpenAPI.SchemaObject | undefined> {
  const schemas = schema[which];

  if (!schemas) {
    return undefined;
  }

  const delimiter = which === "allOf" ? " & " : " | ";
  const tasks = schemas.map((inner) => resolveSchema(inner, repository, schema.required));
  const resolved = await Promise.all(tasks);
  const read = resolved.map((inner) => inner.read).filter(ensureDefined);
  const write = resolved.map((inner) => inner.write).filter(ensureDefined);

  return {
    read: read.length ? read.join(delimiter) : undefined,
    write: write.length ? write.join(delimiter) : undefined,
  };
}

export function resolveAdditionalProperties(
  schema: OpenAPI.SchemaObject,
  repository: Repository,
): MaybePromise<ResolvedOpenAPI.SchemaObject | boolean | undefined> {
  if (schema.additionalProperties === undefined) {
    return undefined;
  }

  if (typeof schema.additionalProperties === "boolean") {
    return schema.additionalProperties;
  }

  return resolveSchema(schema.additionalProperties, repository);
}

export async function resolveProperties({
  required,
  properties,
  additionalProperties,
  repository,
}: {
  required: string[];
  properties: Record<string, OpenAPI.SchemaObject | OpenAPI.ReferenceObject>;
  additionalProperties: boolean | ResolvedOpenAPI.SchemaObject | undefined;
  repository: Repository;
}): Promise<ResolvedOpenAPI.SchemaObject> {
  const tasks = Object.entries(properties).map(([prop, inner]) =>
    resolveSchema(inner, repository).then((value) => [conditionalQuotes(prop), value] as const),
  );

  const resolvedProperties = Object.fromEntries(await Promise.all(tasks));
  const [readProperties, writeProperties] = Object.entries(resolvedProperties).reduce<
    [string[], string[]]
  >(
    (acc, [prop, inner]) => {
      if (inner.read) {
        acc[0].push(maybeOptionalProp(prop, required.includes(prop), inner.read));
      }

      if (inner.write) {
        acc[1].push(maybeOptionalProp(prop, required.includes(prop), inner.write));
      }

      return acc;
    },
    [[], []],
  );

  if (additionalProperties === true || additionalProperties === undefined) {
    readProperties.push("[key: string]: unknown");
    writeProperties.push("[key: string]: unknown");
  }

  return {
    read: Object.keys(readProperties).length ? `{ ${readProperties.join("; ")}; }` : undefined,
    write: Object.keys(writeProperties).length ? `{ ${writeProperties.join("; ")}; }` : undefined,
  };
}

export async function resolveItems(
  items: OpenAPI.SchemaObject | OpenAPI.ReferenceObject,
  repository: Repository,
): Promise<ResolvedOpenAPI.SchemaObject> {
  const resolved = await resolveSchema(items, repository);

  return {
    read: resolved.read ? `(${resolved.read})[]` : undefined,
    write: resolved.write ? `(${resolved.write})[]` : undefined,
  };
}

export async function resolveSchema(
  schema: OpenAPI.SchemaObject | OpenAPI.ReferenceObject,
  repository: Repository,
  parentRequired: string[] = [],
): Promise<ResolvedOpenAPI.SchemaObject> {
  const [resolved, ref] = await repository.resolve(schema);
  const existing = repository.getRef<ResolvedOpenAPI.SchemaObject>(ref);

  if (existing) {
    return existing;
  }

  const required = [...(resolved.required ?? []), ...parentRequired];
  const additionalProperties = await resolveAdditionalProperties(resolved, repository);
  const items = resolved.items ? await resolveItems(resolved.items, repository) : undefined;
  const allOf = await resolvePolymorphism(resolved, "allOf", repository);
  const oneOf = await resolvePolymorphism(resolved, "oneOf", repository);
  const anyOf = await resolvePolymorphism(resolved, "anyOf", repository);
  const not = resolved.not ? await resolveSchema(resolved.not, repository) : undefined;

  let properties: ResolvedOpenAPI.SchemaObject | undefined;

  if (resolved.properties || resolved.type === "object") {
    properties = await resolveProperties({
      required,
      properties: resolved.properties ?? {},
      additionalProperties,
      repository,
    });
  }

  let read: string | undefined;

  if (!resolved.writeOnly) {
    read = getTypescriptType({
      schema: resolved,
      mode: "read",
      properties,
      items,
      polymorphism: { allOf, oneOf, anyOf, not },
    });
  }

  let write: string | undefined;

  if (!resolved.readOnly) {
    write = getTypescriptType({
      schema: resolved,
      mode: "write",
      properties,
      items,
      polymorphism: { allOf, oneOf, anyOf, not },
    });
  }

  return repository.saveRef<ResolvedOpenAPI.SchemaObject>({ read, write }, ref);
}
