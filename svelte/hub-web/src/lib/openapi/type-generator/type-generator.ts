import { ensureDefined } from "../resolvers/helpers";
import type * as OpenAPI from "../openapi/types";
import type { GetTypeScriptTypeParams, Union } from "./types";

export function getPrimitiveType(schema: OpenAPI.SchemaObject): Union {
  if (schema.enum) {
    if (schema.type === "string") {
      return {
        type: "or",
        values: schema.enum.map((value) => `"${value}"`),
      };
    }

    return {
      type: "or",
      values: schema.enum.map((value) => String(value)),
    };
  }

  if (
    schema.type === "string" ||
    schema.type === "boolean" ||
    schema.type === "null" ||
    schema.type === "number"
  ) {
    return schema.type;
  }

  if (schema.type === "integer") {
    return "number";
  }

  return undefined;
}

export function unionToString(union: Union): string | undefined {
  if (typeof union === "string") {
    return union;
  }

  if (!union) {
    return undefined;
  }

  if (union.type === "not") {
    const [base, not] = union.values;

    return not ? `Exclude<${unionToString(base)}, ${unionToString(not)}>` : unionToString(base);
  }

  const result = Array.from(new Set(union.values.map(unionToString))).filter(ensureDefined);

  if (!result.length) {
    return undefined;
  }

  const resultStr = result.join(union.type === "and" ? " & " : " | ");

  if (result.length === 1) {
    return resultStr;
  }

  return `(${resultStr})`;
}

export function getTypescriptType({
  schema,
  mode,
  properties,
  items,
  polymorphism,
}: GetTypeScriptTypeParams): string | undefined {
  const primitive = getPrimitiveType(schema);
  const obj = properties?.[mode];
  const array = items?.[mode];
  const allOf = polymorphism.allOf?.[mode];
  const oneOf = polymorphism.oneOf?.[mode];
  const anyOf = polymorphism.anyOf?.[mode];
  const not = polymorphism.not?.[mode];

  const result = {
    type: "or",
    values: [
      {
        type: "not",
        values: [
          {
            type: "and",
            values: [
              { type: "and", values: [primitive, obj, array, allOf] },
              { type: "or", values: [oneOf] },
              { type: "or", values: [anyOf] },
            ],
          },
          not,
        ],
      },
      schema.nullable ? "null" : undefined,
    ],
  } satisfies Union;

  return unionToString(result);
}
