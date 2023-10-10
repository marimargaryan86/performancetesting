import { z } from "zod";
import {
  type ZodIsOptional,
  type ZodNonNullish,
  type ZodNonOptional,
  zodNonNullish,
  zodNonOptional,
} from "./zod-utils";

/**
 * Get the keys of an object that don't have a `never` value
 * ```ts
 * type A = NoNeverKeys<{ a: never; b: string; c: number }>;
 * // Evaluates to
 * type A = "b" | "c";
 * ```
 * */
type NoNeverKeys<TObj extends object> = {
  [key in keyof TObj]: TObj[key] extends never ? never : key;
}[keyof TObj];

/**
 * Strips an object of the keys that have a never value
 * ```ts
 * type A = NoNeverObject<{ a: never; b: string; c: number }>;
 * // Evaluates to
 * type A = { b: string; c: number };
 * ```
 */
type NoNeverObject<TObj extends object> = Pick<TObj, NoNeverKeys<TObj>>;

/**
 * The identifier of a given `TSchema`, given it has the attributes `id` and `type`
 * ```ts
 * type A = SchemaIdentifier<ZodObject<{
 *    id: ZodString;
 *    type: ZodEnum<["test"]>;
 *    a: ZodString
 * }>>;
 * // Evaluates to
 * type A = ZodObject<{
 *    id: ZodString;
 *    type: ZodEnum<["test"]>;
 * }>;
 *
 * type B = SchemaIdentifier<ZodObject<{
 *    id: ZodString;
 *    a: ZodString;
 * }>>;
 * // Evaluates to
 * type B = undefined;
 * ```
 */
type SchemaIdentifier<TSchema extends z.ZodTypeAny> = ZodNonNullish<TSchema> extends z.ZodObject<{
  id: infer TId extends z.ZodTypeAny;
  type: infer TType extends z.ZodTypeAny;
}>
  ? z.ZodObject<{ id: TId; type: TType }>
  : undefined;

/**
 * A schema relationship, given a simpler record definition of its members
 * ```ts
 * type A = SchemaRelationships<{
 *    a: ZodArray<ZodBoolean>>;
 *    b: ZodOptional<ZodString>;
 *    c: ZodNullable<ZodNumber>;
 * }>;
 * // Evaluates to
 * type A = ZodObject<{
 *    a: ZodObject<{ data: ZodArray<ZodBoolean> }>;
 *    b: ZodOptional<ZodObject<{ data: ZodString }>>;
 *    c: ZodObject<{ data: ZodNullable<ZodNumber> }>;
 * }>;
 * ```
 */
type SchemaRelationships<TMapping extends Record<string, z.ZodTypeAny>> = z.ZodObject<{
  [key in keyof TMapping]: ZodIsOptional<TMapping[key]> extends true
    ? z.ZodOptional<z.ZodObject<{ data: ZodNonOptional<TMapping[key]> }>>
    : z.ZodObject<{ data: TMapping[key] }>;
}>;

/**
 * A schema links object, given the included link keys
 * ```ts
 * type A = SchemaLinks<{ self: true }>;
 * // Evaluates to
 * type A = ZodObject<{ self: ZodString }>;
 *
 * type B = SchemaLinks<{ next: true }>;
 * // Evaluates to
 * type B = ZodObject<{ next: ZodString }>;
 *
 * type C = SchemaLinks<{ self: true, next: true }>;
 * // Evaluates to
 * type C = ZodObject<{ self: true, next: ZodString }>;
 * ```
 */
type SchemaLinks<
  TLinks extends Partial<{ self: true; next: true }>,
  TOut extends object = NoNeverObject<TLinks>,
> = z.ZodObject<{ [key in keyof TOut]: z.ZodString }>;

/**
 * A schema model, providing methods for marshalling an API schema to and from an internal app model
 * ```ts
 * type A = SchemaModel<
 *    ZodObject<{ id: ZodString; type: ZodEnum<["test"]> a: ZodNumber }>,
 *    ZodObject<{ id: ZodString; b: ZodNumber }>
 * >;
 * // Evaluates to
 * type A = {
 *    schema: ZodObject<{ id: ZodString; type: ZodEnum<["test"]> a: ZodNumber }>;
 *    model: ZodObject<{ id: ZodString; b: ZodNumber }>;
 *    identifier: ZodObject<{ id: ZodString; type: ZodEnum<["test"]> }>;
 *    toSchema(data: unknown): { id: string; type: "test"; a: number };
 *    toModel(data: unknown): { id: string; b: number };
 * };
 * ```
 */
type SchemaModel<
  TSchema extends z.ZodTypeAny,
  TModel extends z.ZodTypeAny,
  TIdentifier = SchemaIdentifier<TSchema>,
> = {
  schema: TSchema;
  model: TModel;
  identifier: TIdentifier;
  toSchema(data: unknown): z.infer<TSchema>;
  toModel(data: unknown): z.infer<TModel>;
};

/**
 * A way to infer the types of a `SchemaModel`'s `model`, `schema`, `identifier` and API `error`
 * ```ts
 * type A = SchemaModel<
 *    ZodObject<{ id: ZodString; type: ZodEnum<["test"]> a: ZodNumber }>,
 *    ZodObject<{ id: ZodString; b: ZodNumber }>
 * >;
 * type Model = Infer<A>;
 * // Evaluates to
 * type Model = { id: string; b: number };
 *
 * type Schema = Infer<A, "schema">;
 * // Evaluates to
 * type Schema = { id: string; type: "test"; a: number };
 *
 * type Identifier = Infer<A, "identifier">;
 * // Evaluates to
 * type Identifier = { id: string; type: "test" };
 *
 * type Error = Infer<A, "error">;
 * // Evaluates to
 * type Error = "TODO: Impl";
 * ```
 */
export type Infer<
  TSchemaModel,
  TWhich extends "model" | "schema" | "identifier" | "error" = "model",
> = TSchemaModel extends SchemaModel<infer TSchema, infer TModel, infer TIdentifier>
  ? TWhich extends "model"
    ? z.infer<TModel>
    : TWhich extends "schema"
    ? z.infer<TSchema>
    : TWhich extends "identifier"
    ? TIdentifier extends z.AnyZodObject
      ? z.infer<TIdentifier>
      : never
    : TWhich extends "error"
    ? "TODO: Impl"
    : never
  : never;

/**
 * Get the identifier of an API schema
 *
 * ```ts
 * const ident = identifier(z.object({
 *    id: z.string(),
 *    type: z.enum(["test"]),
 *    a: z.number(),
 * }));
 * // Evaluates to
 * type Ident = ZodObject<{ id: ZodString; type: ZodEnum<["test"]> }>;
 * ```
 * @param schema The API schema
 * @returns A `SchemaIdentifier` if the schema has attributes `id` and `type`, otherwise undefined
 */
export function identifier<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
): SchemaIdentifier<TSchema> {
  const innerSchema = zodNonNullish(schema) as {
    shape?: {
      id?: z.ZodString;
      type?: z.ZodString;
    };
  };

  return (
    innerSchema.shape?.id && innerSchema.shape.type
      ? z.object({ id: innerSchema.shape.id, type: innerSchema.shape.type })
      : undefined
  ) as SchemaIdentifier<TSchema>;
}

/**
 * Get a relationships schema
 *
 * ```ts
 * const rel = relationships({
 *    a: z.array(z.number()),
 *    b: z.string().optional(),
 *    c: z.number().nullable(),
 * });
 * // Evaluates to
 * type Rel = ZodObject<{
 *    a: ZodObject<{ data: ZodArray<ZodNumber> }>;
 *    b: ZodOptional<ZodObject<{ data: ZodString }>>;
 *    c: ZodObject<{ data: ZodNullable<ZodNumber> }>;
 * }>;
 * ```
 *
 * @param mapping A simplified relationships mapping
 * @returns JSON API schema compliant relationships schema
 */
export function relationships<TMapping extends Record<string, z.ZodTypeAny>>(
  mapping: TMapping,
): SchemaRelationships<TMapping> {
  return z.object(
    Object.fromEntries(
      Object.entries(mapping).map(([key, val]) => {
        const inner = z.object({ data: zodNonOptional(val) });

        return [key, val.isOptional() ? inner.optional() : inner];
      }),
    ),
  ) as SchemaRelationships<TMapping>;
}

/**
 * Get a links schema
 *
 * ```ts
 * const a = links({ self: true });
 * // Evaluates to
 * type A = ZodObject<{ self: ZodString }>;
 *
 * const b = links({ next: true });
 * // Evaluates to
 * type B = ZodObject<{ next: ZodString }>;
 *
 * const c = links({ self: true, next: true });
 * // Evaluates to
 * type C = ZodObject<{ self: ZodString; next: ZodString }>;
 * ```
 * @param which Which links to include
 * @returns JSON API schema compliant links schema
 */
export function links<TLinks extends Partial<{ self: true; next: true }>>(
  which: TLinks,
): SchemaLinks<TLinks> {
  return z.object(
    Object.fromEntries(Object.keys(which).map((key) => [key, z.string()])),
  ) as SchemaLinks<TLinks>;
}

/**
 * Get a schema model
 *
 * ```ts
 * const sm = create({
 *    schema: z.object({ id: z.string(), type: z.enum(["test"]), a: z.number() }),
 *    model: z.object({ id: z.string(), b: z.number().optional() }),
 *    toModel: (data) => ({
 *      id: data.id,
 *      b: data.a,
 *    }),
 *    toSchema: (data) =>
 *      ({
 *        id: data.id,
 *        type: "test",
 *        a: data.b ?? 0,
 *      } as const),
 * });
 *
 * // Get the model definition
 * const model = sm.model;
 * // Get the schema definition
 * const schema = sm.schema;
 * // Get the schema identifier definition
 * const identifier = sm.identifier;
 *
 * // Infer types
 * type Model = Infer<typeof sm>;
 * // Evaluates to
 * type Model = {
 *    id: string;
 *    b?: number;
 * };
 *
 * type Schema = Infer<typeof sm, "schema">;
 * // Evaluates to
 * type Schema = {
 *    id: string;
 *    type: "test";
 *    a: number;
 * };
 *
 * type Identifier = Infer<typeof sm, "identifier">;
 * // Evaluates to
 * type Identifier = {
 *    id: string;
 *    type: "test";
 * };
 *
 * // Marshall data
 * const modelOut = sm.toModel(data);
 * // Evaluates to Model or throws a ZodError
 *
 * const schemaOut = sm.toSchema(data);
 * // Evaluates to Schema or throws a ZodError
 * ```
 * @param def Schema model definition
 * @returns A `SchemaModel`
 */
export function create<TSchema extends z.ZodTypeAny, TModel extends z.ZodTypeAny>(def: {
  schema: TSchema;
  model: TModel;
  toSchema?(data: z.infer<TModel>): z.infer<TSchema>;
  toModel?(data: z.infer<TSchema>): z.infer<TModel>;
}): SchemaModel<TSchema, TModel> {
  return {
    schema: def.schema,
    model: def.model,
    identifier: identifier(def.schema),
    toSchema: (data) => def.schema.parse(def.toSchema?.(data) ?? data),
    toModel: (data) => def.model.parse(def.toModel?.(data) ?? data),
  };
}
