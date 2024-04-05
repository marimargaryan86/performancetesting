import type { Mode } from "./types";
import type * as ResolvedOpenAPI from "../resolvers/types";
import { INDENT } from "./constants";
import { stringifyContent } from "./content";
import { conditionalQuotes, maybeOptionalProp, toStringObject } from "./helpers";
import { stringifySchema } from "./schema";

export function stringifyParameter(
  parameter: ResolvedOpenAPI.ParameterObject,
  indent: number,
): string {
  const nextIndent = indent + INDENT;

  let schema: string | undefined;

  if (parameter.schema) {
    schema = toStringObject(
      [
        `read: ${stringifySchema(parameter.schema, "read")}`,
        `write: ${stringifySchema(parameter.schema, "write")}`,
      ],
      nextIndent,
    );
  }

  let content: string | undefined;

  if (parameter.content) {
    const innerIndent = nextIndent + INDENT;

    content = toStringObject(
      [
        `read: ${stringifyContent(parameter.content, "read", innerIndent)}`,
        `write: ${stringifyContent(parameter.content, "write", innerIndent)}`,
      ],
      nextIndent,
    );
  }

  return toStringObject(
    [
      `name: "${parameter.name}"`,
      `required: ${parameter.required}`,
      schema ? `schema: ${schema}` : undefined,
      content ? `content: ${content}` : undefined,
    ],
    indent,
  );
}

export function stringifyParameterSimple(
  parameter: ResolvedOpenAPI.ParameterObject,
  mode: Mode,
  indent: number,
): string {
  if (parameter.schema) {
    return stringifySchema(parameter.schema, mode);
  }

  if (parameter.content) {
    return stringifyContent(parameter.content, mode, indent);
  }

  throw new Error("Neither schema nor content is defined in parameter");
}

export function stringifyParametersAux(
  parameters: Record<string, ResolvedOpenAPI.ParameterObject>,
  mode: Mode,
  indent: number,
): [required: boolean, prop: string] {
  const nextIndent = indent + INDENT;

  let required = false;

  const stringified = Object.entries(parameters).map(([name, parameter]) => {
    required = required || parameter.required;

    return maybeOptionalProp(
      conditionalQuotes(name),
      parameter.required,
      stringifyParameterSimple(parameter, mode, nextIndent),
    );
  });

  return [required, toStringObject(stringified, indent)];
}

export function stringifyParameterMapping(
  mapping: Record<string, ResolvedOpenAPI.ParameterObject>,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(mapping).map(
    ([name, parameter]) =>
      `${conditionalQuotes(name)}: ${stringifyParameter(parameter, nextIndent)}` as const,
  );

  return toStringObject(stringified, indent);
}
