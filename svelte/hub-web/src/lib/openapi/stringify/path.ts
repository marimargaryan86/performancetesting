import type * as ResolvedOpenAPI from "../resolvers/types";
import { EMPTY_OBJECT, INDENT } from "./constants";
import { maybeOptionalProp, toStringObject } from "./helpers";
import { stringifyRequest, stringifyResponses } from "./response-request";

export function stringifyOperation(
  operation: ResolvedOpenAPI.OperationObject,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const [required, request] = stringifyRequest(
    operation.parameters,
    operation.requestBody,
    nextIndent,
  );

  return toStringObject(
    [
      request === EMPTY_OBJECT ? undefined : maybeOptionalProp("request", required, request),
      `response: ${stringifyResponses(operation.responses, nextIndent)}`,
    ],
    indent,
  );
}

export function stringifyPathItem(
  pathItem: ResolvedOpenAPI.PathItemObject,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(pathItem).map(([method, operation]) => {
    return operation
      ? (`${method}: ${stringifyOperation(operation as ResolvedOpenAPI.OperationObject, nextIndent)}` as const)
      : undefined;
  });

  return toStringObject(stringified, indent);
}

export function stringifyPaths(paths: ResolvedOpenAPI.PathsObject, indent: number): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(paths).map(
    ([path, pathItem]) => `"${path}": ${stringifyPathItem(pathItem, nextIndent)}` as const,
  );

  return toStringObject(stringified, indent);
}
