import type * as ResolvedOpenAPI from "../resolvers/types";
import { EMPTY_OBJECT, INDENT } from "./constants";
import { stringifyContent } from "./content";
import { maybeOptionalProp, toStringObject } from "./helpers";
import { stringifyParametersAux } from "./parameter";

export function stringifyRequest(
  { cookie, header, path, query }: ResolvedOpenAPI.OperationObject["parameters"],
  requestBody: ResolvedOpenAPI.RequestBodyObject | undefined,
  indent: number,
): [required: boolean, request: string] {
  const nextIndent = indent + INDENT;
  const body = requestBody
    ? stringifyContent(requestBody.content, "write", nextIndent)
    : EMPTY_OBJECT;

  let requestRequired = Boolean(requestBody?.required);

  const stringified: (`${string}: ${string}` | undefined)[] = [
    body === EMPTY_OBJECT ? undefined : maybeOptionalProp("body", requestRequired, body),
  ];

  Object.entries({ cookie, headers: header, path, query }).forEach(([name, obj]) => {
    if (obj) {
      const [required, str] = stringifyParametersAux(obj, "write", nextIndent);
      requestRequired = requestRequired || required;

      stringified.push(maybeOptionalProp(name, required, str));
    }
  });

  return [requestRequired, toStringObject(stringified, indent)];
}

export function stringifyResponses(
  responses: ResolvedOpenAPI.ResponsesObject,
  indent: number,
): string {
  const nextIndent = indent + INDENT;
  const stringified = Object.entries(responses).map(([httpCode, _response]) => {
    const response = _response as ResolvedOpenAPI.ResponseObject;
    const body = response.content
      ? stringifyContent(response.content, "read", nextIndent)
      : undefined;

    let headersRequired = false;
    let headers: string | undefined;

    if (response.headers) {
      [headersRequired, headers] = stringifyParametersAux(response.headers, "read", nextIndent);
    }

    return toStringObject(
      [
        `status: ${httpCode}`,
        body ? `body: ${body}` : undefined,
        !headers || headers === EMPTY_OBJECT
          ? undefined
          : maybeOptionalProp("headers", headersRequired, headers),
      ],
      indent,
    );
  });

  if (!stringified.length) {
    return EMPTY_OBJECT;
  }

  if (stringified.length === 1) {
    return stringified.join(" | ");
  }

  return `(${stringified.join(" | ")})`;
}
