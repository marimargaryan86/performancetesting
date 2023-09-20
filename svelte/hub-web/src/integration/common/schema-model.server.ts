import { z } from "zod";

export type SchemaModel<TSchema extends z.ZodType, TModel extends z.ZodType> = {
  schema: TSchema;
  model: TModel;
  identifier: IdentifierSchema<TSchema>;
  toModel(data: unknown): z.infer<TModel>;
  toSchema(data: unknown): z.infer<TSchema>;
};

type IdentifierSchema<TSchema extends z.ZodType> = TSchema extends z.ZodObject<{
  id: z.ZodType;
  type: z.ZodType;
}>
  ? z.ZodObject<Pick<TSchema["shape"], "id" | "type">>
  : unknown;

export function getSchemaModel<TSchema extends z.ZodType, TModel extends z.ZodType>(
  schema: TSchema,
  model: TModel,
  strategies: {
    toModel?: (data: z.infer<TSchema>) => TModel["_input"];
    toSchema?: (data: z.infer<TModel>) => TSchema["_input"];
  } = {},
): SchemaModel<TSchema, TModel> {
  function toModel(data: unknown): z.infer<TModel> {
    const parsed = schema.parse(data);

    return model.parse(strategies.toModel?.(parsed) ?? parsed);
  }

  function toSchema(data: unknown): z.infer<TSchema> {
    const parsed = model.parse(data);

    return schema.parse(strategies.toSchema?.(parsed) ?? parsed);
  }

  return {
    schema,
    model,
    identifier: (schema instanceof z.ZodObject
      ? schema.pick({ id: true, type: true })
      : undefined) as unknown as IdentifierSchema<TSchema>,
    toModel,
    toSchema,
  };
}

type OptionalKeys<TSchema extends Record<string, z.ZodType>> = {
  [key in keyof TSchema]: TSchema[key] extends z.ZodOptional<infer _> ? key : never;
}[keyof TSchema];

type Relationship<
  TSchema extends Record<string, z.ZodType>,
  TOptionalKeys extends keyof TSchema = OptionalKeys<TSchema>,
> = {
  [key in Exclude<keyof TSchema, TOptionalKeys>]: z.ZodObject<{
    data: TSchema[key];
  }>;
} & {
  [key in keyof Pick<TSchema, TOptionalKeys>]: z.ZodOptional<
    z.ZodObject<{
      data: TSchema[key] extends z.ZodOptional<infer TInner> ? TInner : never;
    }>
  >;
};

export function relationship<TMapping extends Record<string, z.ZodType>>(
  data: TMapping,
): z.ZodObject<Relationship<TMapping>> {
  return z.object(
    Object.fromEntries(
      Object.entries(data).map(([key, val]) => {
        const optional = val instanceof z.ZodOptional;
        const nextVal = optional ? val.unwrap() : val;
        const schema = z.object({ data: nextVal });

        return [key, optional ? schema.optional() : schema];
      }),
    ),
  ) as z.ZodObject<Relationship<TMapping>>;
}

export function links<TItem extends "next" | "self">(
  items: TItem[],
): z.ZodObject<Record<TItem, z.ZodString>> {
  return z.object({
    ...(items.includes("next" as TItem) ? { next: z.string().url() } : undefined),
    ...(items.includes("self" as TItem) ? { self: z.string().url() } : undefined),
  }) as z.ZodObject<Record<TItem, z.ZodString>>;
}

export type Infer<
  TParser extends SchemaModel<z.ZodType, z.ZodType>,
  TWhat extends "schema" | "model" | "identifier" = "model",
> = TParser extends SchemaModel<infer TSchema extends z.ZodType, infer TModel extends z.ZodType>
  ? TWhat extends "identifier"
    ? TSchema extends z.AnyZodObject
      ? z.infer<z.ZodObject<{ id: TSchema["shape"]["id"]; type: TSchema["shape"]["type"] }>>
      : never
    : TWhat extends "schema"
    ? z.infer<TSchema>
    : z.infer<TModel>
  : never;
