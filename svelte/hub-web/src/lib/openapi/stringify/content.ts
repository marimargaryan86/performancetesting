import type * as ResolvedOpenAPI from "../resolvers/types";
import type { Mode } from "./types";
import { INDENT } from "./constants";
import { toStringObject, conditionalQuotes } from "./helpers";
import { stringifySchema } from "./schema";
import { stringifyParameterMapping } from "./parameter";

export function stringifyEncoding(
  encoding: ResolvedOpenAPI.EncodingObject,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  return toStringObject(
    [
      `contentType: ${encoding.contentType ? `"${encoding.contentType}"` : undefined}`,
      `headers: ${encoding.headers ? stringifyParameterMapping(encoding.headers, nextIndent) : undefined}`,
    ],
    indent,
  );
}

export function stringifyEncodingMapping(
  mapping: Record<string, ResolvedOpenAPI.EncodingObject>,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(mapping).map(
    ([mediaType, encoding]) =>
      `${conditionalQuotes(mediaType)}: ${stringifyEncoding(encoding, nextIndent)}` as const,
  );

  return toStringObject(stringified, indent);
}

export function stringifyMediaType(
  mediaType: ResolvedOpenAPI.MediaTypeObject,
  mode: Mode,
  indent: number,
): string {
  if (mediaType.schema) {
    return stringifySchema(mediaType.schema, mode);
  }

  if (mediaType.encoding) {
    return stringifyEncodingMapping(mediaType.encoding, indent);
  }

  throw new Error("Neither schema nor encoding is defined in MediaType");
}

export function stringifyContent(
  content: Record<string, ResolvedOpenAPI.MediaTypeObject>,
  mode: Mode,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(content).map(([name, mediaType]) =>
    toStringObject(
      [`type: "${name}"`, `data: ${stringifyMediaType(mediaType, mode, nextIndent)}`],
      indent,
    ),
  );

  if (stringified.length === 0) {
    return "undefined";
  }

  if (stringified.length === 1) {
    return stringified.join(" | ");
  }

  return `(${stringified.join(" | ")})`;

  // const stringified = Object.entries(content).map(
  //   ([name, mediaType]) =>
  //     `${conditionalQuotes(name)}: ${stringifyMediaType(mediaType, mode, nextIndent)}` as const,
  // );

  // return toStringObject(stringified, indent);
}
