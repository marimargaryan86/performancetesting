import { z } from "zod";

type SchemaParserReturnType<TSchema extends z.ZodType, TModel extends z.ZodType> = {
  schema: TSchema;
  model: TModel;
  toModel(data: unknown): z.infer<TModel>;
  toSchema(data: unknown): z.infer<TSchema>;
};

export function getSchemaModel<TSchema extends z.ZodType, TModel extends z.ZodType>(
  schema: TSchema,
  model: TModel,
  strategies: {
    toModel?: (data: z.infer<TSchema>) => TModel["_input"];
    toSchema?: (data: z.infer<TModel>) => TSchema["_input"];
  } = {},
): SchemaParserReturnType<TSchema, TModel> {
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

/* eslint-disable @typescript-eslint/ban-types */
export function links<TItem extends "next" | "self">(
  items: TItem[],
): z.ZodObject<Record<TItem, z.ZodString>> {
  return z.object({
    ...(items.includes("next" as TItem) ? { next: z.string().url() } : undefined),
    ...(items.includes("self" as TItem) ? { self: z.string().url() } : undefined),
  }) as z.ZodObject<Record<TItem, z.ZodString>>;
}
/* eslint-enable */

export type Infer<
  TParser extends SchemaParserReturnType<z.ZodType, z.ZodType>,
  TWhat extends "schema" | "model" | "identifier" = "model",
> = TParser extends SchemaParserReturnType<
  infer TSchema extends z.ZodType,
  infer TModel extends z.ZodType
>
  ? TWhat extends "identifier"
    ? TSchema extends z.AnyZodObject
      ? z.infer<z.ZodObject<{ id: TSchema["shape"]["id"]; type: TSchema["shape"]["type"] }>>
      : never
    : TWhat extends "schema"
    ? z.infer<TSchema>
    : z.infer<TModel>
  : never;
